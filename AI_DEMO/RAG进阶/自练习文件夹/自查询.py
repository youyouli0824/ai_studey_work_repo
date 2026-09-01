from langchain_chroma import Chroma
from langchain_classic.retrievers.self_query.base import SelfQueryRetriever
# Chroma的专用翻译器
from langchain_community.query_constructors.chroma import ChromaTranslator
from meta_data import docs, metadata_field_info
from base_llm import llm, embeddings_model

#1.初始化Chroma数据库
vectorstore=Chroma.from_documents(docs,embeddings_model)

translator=ChromaTranslator()

document_contents="brief description of technical articles"

#自查询检索器
retriever=SelfQueryRetriever.from_llm(
    llm=llm,
    vectorstore=vectorstore,
    structured_query_translator=translator,
    metadata_field_info=metadata_field_info,
    document_contents=document_contents
)

result=retriever.invoke("作者A发表的论文")
for doc in result:
    print(doc.metadata,doc.page_content)