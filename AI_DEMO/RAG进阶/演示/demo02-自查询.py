from langchain_chroma import Chroma
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
# Chroma的专用翻译器
from langchain_community.query_constructors.chroma import ChromaTranslator
from meta_data import docs, metadata_field_info
from base_llm import llm, embeddings_model

# 1. 初始化Chroma数据库
vectorstore = Chroma.from_documents(docs,embeddings_model)

# 可以把大模型的结果，转换为Chroma能够理解的查询语句
translator=ChromaTranslator()

# 文档内容描述
document_contents = "brief description of technical articles"

# 2. 初始化自查询检索器
retriever = SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    structured_query_translator=translator,
    metadata_field_info=metadata_field_info,
    document_contents=document_contents
)

result=retriever.invoke("作者A发表的论文")
for doc in result:
    print(doc.metadata,doc.page_content)
