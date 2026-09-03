import os
import re
import warnings
from typing import List

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.runnables import RunnableLambda

# 屏蔽langchain‑community废弃警告，仅课堂调试使用
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_community")
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from base_llm import llm, embeddings_model

# v4版要解决如下问题：
# 1.向量入库、检索；
# 2.对检索进行优化：增加混合检索；
# 3.表格占位符这部分的内容要还原

# 定义类，负责抽取表格
class TableExtractor:
    @staticmethod
    def extract_tables_and_text(text: str,start_table_id: int = 0) -> tuple[List[tuple[str, str]], str]:
        table_pattern = r'(<table>.*?</table>)'
        tables=re.findall(table_pattern,text,re.DOTALL|re.IGNORECASE)
        if not tables:
            return [], text

        # 未抽取时的内容：既有表格，也有普通文本
        cleaned_text=text
        current_id=start_table_id
        # 存放表格
        table_items=[]

        for tbl in tables:
            # 表格id---tbl_0
            tbl_id = f"tbl_{current_id}"
            # "xssss tbl_0 xxxxx"
            cleaned_text=cleaned_text.replace(tbl,tbl_id,1)
            # 存放表格id和表格内容
            table_items.append((tbl_id,tbl))
            current_id+=1
        # 返回单独的表格 和 替换后的文本
        return table_items, cleaned_text

# 定义类，负责智能切分
class MarkdownTableAwareSplitter:
    def __init__(self):
        self.table_extractor = TableExtractor()

    # 用于片段的合并判断
    @staticmethod
    def should_merge(prev_len: int, new_len: int, max_len: int) -> bool:
        """判断前后两段是否应该合并（留2个字符给换行）"""
        return (prev_len + new_len + 2) <= max_len

    # 智能切分
    def split(self,
              documents: List[Document],  # 已经按一级标题（Header 1）切分好的文档列表
              max_text_length: int = 1200,
              min_text_length_to_merge: int = 400,
              min_nonempty_text_len: int = 40
              ) -> List[Document]:

        final_docs: List[Document] = []  # 最终输出的Document列表
        pendding_text: str = ""  # 暂存区，把每一行拼接成document的时候使用的
        pendding_meta: dict = {}  # 把每一行拼接成document的时候，保存元数据时使用的
        global_table_counter = 0  # 表格id，全局的表格编号

        # 提取表格中的内容
        # <table><tr><td>ssss</td></tr></table>
        for doc in documents:  # 遍历所有的按一级标题切分后的文档
            content = doc.page_content.strip()
            if not content:
                continue
            # 调用表格抽取器，抽取表格中的内容
            table_items, cleaned_text = self.table_extractor.extract_tables_and_text(content, global_table_counter)
            # 复制一份元数据
            metadata = doc.metadata.copy()
            section_title = metadata.get("Header 1", "未知章节")

            # 对文本进行清洗----如果某行文本前后为空，我们只去掉右边的空格
            lines = [line.rstrip() for line in cleaned_text.splitlines() if line.strip()]

            # 基于贪心策略进行合并
            current_chunk = ""  # 暂存区，暂存每行文本
            for line in lines:
                current_line = (current_chunk + "\n" + line) if current_chunk else line
                if len(current_line) <= max_text_length:
                    current_chunk = current_line
                else:
                    if pendding_text and self.should_merge(len(pendding_text), len(current_chunk), max_text_length):
                        pendding_text = (pendding_text + "\n\n" + current_chunk).strip()
                    else:
                        if pendding_text:
                            final_docs.append(Document(page_content=pendding_text, metadata=pendding_meta))
                        pendding_text = current_chunk
                        pendding_meta = metadata.copy()
                    current_chunk = line

            # 处理最后一个段落
            if current_chunk:
                if pendding_text and self.should_merge(len(pendding_text), len(current_chunk), max_text_length):
                    pendding_text = (pendding_text + "\n\n" + current_chunk).strip()
                else:
                    if pendding_text:
                        final_docs.append(Document(page_content=pendding_text, metadata=pendding_meta))
                    pendding_text = current_chunk
                    pendding_meta = metadata.copy()

        # 处理表格
        for table_id, table_content in table_items:
            if pendding_text:
                final_docs.append(Document(page_content=pendding_text, metadata=pendding_meta))
                pendding_text = ""
                pendding_meta = {}
            table_mata = metadata.copy()
            # 给表格的内容增加元数据，用来区分普通文本和表格
            # {"category": "Table", "table_id": "tbl_0", "table_section": "xxx"}
            table_mata.update({"category": "Table", "table_id": table_id, "table_section": section_title})
            final_docs.append(Document(page_content=table_content, metadata=table_mata))
            global_table_counter += 1

        # 对暂存区里的内容进行处理
        if pendding_text:
            final_docs.append(Document(page_content=pendding_text, metadata=pendding_meta))

        # 过滤掉无意义的符号，比如空格、换行符等
        filtered = []
        for document in final_docs:
            text = document.page_content.strip()
            if document.metadata.get("category") == "Table":
                filtered.append(document)
                continue
            if len(text) < min_nonempty_text_len and not re.search(r'\w', text):
                continue
            filtered.append(document)
        return filtered

# 实现检索 + 混合检索
class FinanceRAG:
    def __init__(self,filepath='厦门灿坤实业股份有限公司.md',
                 persist_directory='./chromadb',collection_name='my_collection',
                 max_chunk_length=800,batch_size=10):
        self.filepath = filepath
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.max_chunk_length = max_chunk_length
        self.batch_size = batch_size

        self.vector_db = None
        self.retriever = None
        self.chain = None
        self.documents = None  # 保存原始切分后的 documents，便于 BM25 使用
        self._load_and_process()  # 加载文档
        self._build_retriever_and_chain()  # 创建链

    # 负责文档加载及切分
    def _load_and_process(self):
        ## 1. 加载文档
        loader = TextLoader(self.filepath, encoding="utf-8")
        docs = loader.load()

        # 2. 文档分割---按一级标题切分
        header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header 1")])
        split_docs = header_splitter.split_text(docs[0].page_content)

        # 3. 自定义切分：保护表格、合理合并文本段落
        table_doc_splitter = MarkdownTableAwareSplitter()
        # document对象，里面有文本（含表格id占位符）、表格
        self.documents = table_doc_splitter.split(documents=split_docs, max_text_length=self.max_chunk_length)

        # 4. 向量入库
        # 创建/连接 Chroma 向量库
        self.vector_db = Chroma(
            collection_name=self.collection_name,
            embedding_function=embeddings_model,
            persist_directory=self.persist_directory
        )

        if not len(os.listdir(self.persist_directory)) > 1:
            # 分批添加文档到向量数据库中，防止内存溢出
            for i in range(0, len(self.documents), self.batch_size):
                batch = self.documents[i:i + self.batch_size]
                print(f'第 {i // self.batch_size + 1} 批次 文件数: {len(batch)}')
                # 向量入库
                self.vector_db.add_documents(batch)

    # 负责创建检索器和链
    def _build_retriever_and_chain(self):
        vector_retriever = self.vector_db.as_retriever(search_kwargs={"k": 6})
        bm25_retriever =BM25Retriever.from_documents(self.documents)
        # 需要一个混合检索器
        self.retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.3, 0.7]
        )

        # 闭包---》把每个表格的内容，还原到该表格在原文中的原始位置上，tbl_0--->table内容
        def replace_table_placeholder(docs):
            # {"category":"Table","table_id":"tbl_0","table_section":"xxx"}
            # 去向量数据库中获取所有的表格
            table_docs = self.vector_db.get(where={"category": "Table"})
            table_map = {}  # "tbl_0":表格的内容;"tbl_1":表格的内容;"tbl_2":表格的内容...
            for meta, table_content in zip(table_docs["metadatas"], table_docs["documents"]):
                table_id = meta.get("table_id")
                if table_id:
                    # {"tbl_0":"xxx"}
                    table_map[table_id] = table_content

            # 把从向量库中获取的表格内容，替换到原始文档中，tbl_0--->table内容
            # 原文效果：”xxxxssss tbl_0 xxxxddddd tbl_1 xxxxx“
            context_parts = []
            for doc in docs:
                text = doc.page_content
                def repl(math):
                    tbl_id = f"tbl_{math.group(1)}"  # tbl_id = tbl_0
                    return table_map.get(tbl_id, f"【表格 {tbl_id} 内容缺失】")

                new_text = re.sub(r'tbl_(\d+)__', repl, text)
                context_parts.append(new_text)

            # 返回的是一个可以供模型进行推理的上下文的字符串
            # 最终效果：”xxxxssss 66666 xxxxddddd 999999 xxxxx“
            return "\n\n".join(context_parts)

        # 检索生成：
        replace_lambda = RunnableLambda(lambda x:
                                        {
                                            "context": replace_table_placeholder(x["retriever_context"]),
                                            # 所有的匹配的片段 （内容里还是table_id）-》
                                            "question": x["question"]
                                        }
                                        )

        template = """请根据下面给出的上下文或者表格来回答问题:
                        {context}
                        问题: {question}
                        回答要尽量准确、完整，使用 markdown 格式排版。
                        如果涉及表格，请一定保留关键数据，一定不要省略。
                        """
        prompt = ChatPromptTemplate.from_template(template)
        self.chain = (
                {
                    "retriever_context": lambda x: self.retriever.invoke(x["question"]),  # 所有的匹配的片段 （内容里还是table_id）
                    "question": lambda x: x["question"]
                }
                | replace_lambda | prompt | llm | StrOutputParser())

    # 负责查询
    def query(self, question: str) -> str:
        if self.chain:
            return self.chain.invoke({"question": question})
        return "RAG系统未初始化"

if __name__ == "__main__":
    rag=FinanceRAG()
    result=rag.query("主要会计数据和财务指标")
    print(result)