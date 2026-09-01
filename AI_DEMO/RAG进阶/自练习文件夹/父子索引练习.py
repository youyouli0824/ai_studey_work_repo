# ParentDocument父子索引检索实现方案，属于RAG索引构建阶段分层分块优化（MultiVector多向量检索实现路线之一）
import os
import warnings
import uuid
# 屏蔽废弃包警告，消除控制台冗余提示
warnings.filterwarnings("ignore", category=DeprecationWarning)
# 配置网页爬虫UA，解决网页加载阻塞、超时问题
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome 120.0.0.0"
from base_llm import llm, embeddings_model
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.stores import InMemoryByteStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser

# 1. 文档加载
url = "https://news.pku.edu.cn/xwzh/687160cb45fc4bb891d8ff384c42d56d.htm"
loader = WebBaseLoader(url)
#["page_content":"网页正文"]
raw_doc=loader.load()

#清洗原始文本
doc=[]
for d in raw_doc:
    content=d.page_content.strip().replace("\n","").replace("\r","")
    # 过滤内容长度不足80的导航/空白文本(网页菜单、页脚、版权、跳转链接等)
    if len(content)>80:
        d.page_content=d.page_content.strip()
        # [Document(page_id="1", page_content="hello world")]
        doc.append(d)
print("【进度1】网页正文加载+清洗完成，过滤导航空白文本")

#文本分段
#创建父文档切分对象
parent_splitter=RecursiveCharacterTextSplitter(chunk_size=800,
                                               chunk_overlap=80,
                                               separators=["\n\n","。","！","？","\n"])
#子文档切分对象
child_splitter=RecursiveCharacterTextSplitter(chunk_size=350,
                                              chunk_overlap=40,
                                              separators=["\n\n", "。", "！", "？", "\n"])

#进行父文档切分
parent_docs=parent_splitter.split_documents(doc)
all_child_text=[]
#存放子文档的元数据
all_child_meta=[]
parent_id_map={}

#对父文档进行子文档切分
for p_doc in parent_docs:
    #生成父文档的唯一id
    parent_id=str(uuid.uuid4())
    parent_id_map[parent_id]=p_doc
    #切分出子文档
    child_text_list=child_splitter.split_text(p_doc.page_content)
    #清洗切分出的子文档
    for text in child_text_list:
        clean_text=text.strip()
        #过滤30字符以下的碎片导航文字
        if len(clean_text)>=30:
            all_child_text.append(clean_text)
            #给每一个子文档身上关联了父文档的唯一id
            all_child_meta.append({"parent_id":parent_id})

#把父文档存入内存库
store=InMemoryByteStore()
store.mset(list(parent_id_map.items()))
# 把子文档存入向量库
vector = Chroma(collection_name="my_vector_db", embedding_function=embeddings_model)
if len(all_child_text)>0:
    # 把Document对象变向量
    #vector.add_documents(all_child_text,metadatas=all_child_meta)
    vector.add_texts(texts=all_child_text, metadatas=all_child_meta)

#进行检索
#自定义一个检索函数
def custom_retrieve(query:str,k=3):
    # 向量库检索出子片段
    child_docs = vector.similarity_search(query, k=k)
    # 提取父ID
    parent_ids = set([d.metadata["parent_id"] for d in child_docs])
    # 从内存读取完整父文档
    parent_docs = store.mget(parent_ids)
    return [p for p in parent_docs if p is not None]

# 进行检索查询
template = """请根据下面给出的上下文来回答问题:
{context}
问题: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
# {"context":"上下文参考内容--父文档的正文内容","question":"北京大学开了个什么会？"}
chain=RunnableMap({"context":lambda x: custom_retrieve(x["question"],k=3),
             "question":lambda x: x["question"]
             }) | prompt | llm

result=chain.invoke({"question":"北京大学开了个什么会？"})
print("=======最终的检索结果=====")
print(result.content)    