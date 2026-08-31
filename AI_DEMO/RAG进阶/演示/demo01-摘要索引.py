# 摘要检索(MultiVector多向量检索)落地实现方案，属于索引优化技术。
import os
import uuid
import warnings
# 屏蔽废弃包警告
warnings.filterwarnings("ignore", category=DeprecationWarning)
# 配置爬虫UA，解决网页加载阻塞
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome 120.0.0.0"
from base_llm import llm, embeddings_model
from langchain_core.stores import InMemoryByteStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, WebBaseLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# MultiVectorRetriever 多用检索
from langchain_classic.retrievers import MultiVectorRetriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap

# 1. 加载文档
url = "https://news.pku.edu.cn/xwzh/687160cb45fc4bb891d8ff384c42d56d.htm"
loaders=[
    UnstructuredWordDocumentLoader("人事管理流程.docx"),
    WebBaseLoader(url)
]

# 真正执行加载方法
docs=[]
for loader in loaders:
    docs.extend(loader.load())
print(f"【进度1完成】总文档页数：{len(docs)}")

# 2.文本分段
splitter=RecursiveCharacterTextSplitter(chunk_size=512,chunk_overlap=50)
chunks=splitter.split_documents(docs)
print(f"【进度2完成】总分段数：{len(chunks)}")

# 3.把分段文本提取对应的摘要
# "doc": 分段的文本---->prompt--->llm--->输出解析器
chain=({"doc":lambda x:x.page_content}
       | ChatPromptTemplate.from_template("总结下面的文档:\n\n{doc}")
       | llm
       | StrOutputParser()
       )
# 并发执行5个分段
summary=chain.batch(chunks,{"max_concurrency":5})
print("sum摘要:",summary)
print(f"【进度3完成】总摘要数：{len(summary)}")

# 4. 把摘要进行向量化入库，把原文存入内存中
vector = Chroma(collection_name="summ",embedding_function=embeddings_model)
# 内存存储，用于存储原文
store=InMemoryByteStore()

# 5. 多向量检索
id_key="doc_id"
retriever=MultiVectorRetriever(
    vectorstore=vector,
    byte_store=store,
    id_key=id_key
)

# 6.把摘要变成向量，并存入向量库
doc_ids=[str(uuid.uuid4()) for _ in chunks]
# 为每一个摘要添加一个唯一ID---uuid
summary_docs = [Document(page_content=s,metadata={id_key:doc_ids[i]}) for i,s in enumerate(summary) ]
retriever.vectorstore.add_documents(summary_docs)
print("【进度4】摘要向量库入库完成")

# 7. 原文存储到内存中.zip()函数将ID和文档对应起来
retriever.docstore.mset(list(zip(doc_ids,chunks)))
print("【进度5】原文存储到内存中完成")

# 8. 进行问题的检索
prompt = ChatPromptTemplate.from_template("根据下面的文档回答问题:\n\n{doc}\n\n问题: {question}")
# {"doc":检索到的与问题相关的片段，带有doc_id；"question":"病假请假流程是什么？"}
question_chain=RunnableMap({"doc":lambda x: retriever.invoke(x["question"]),
             "question":lambda x: x["question"]
             }) | prompt | llm

query = "病假的请假流程"
result = question_chain.invoke({"question":query})
print("=======文档的结果========")
print(result.content)

# 从向量中直接查询，进一步验证与问题相关的答案，直接利用线速度搜索进行检索
sub_docs = retriever.vectorstore.similarity_search("病假的请假流程?")
print(sub_docs[0])

# 从内存中直接查询
summ_id = sub_docs[0].metadata[id_key]
# 从内存中读取doc_id对应的完整原始文档
# 类似于：select * from table where doc_id = ?
orig_doc = retriever.docstore.mget([summ_id])
print("\n=====对应的完整原始文档=====")
print(orig_doc)








