from ast import mod
import os
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from torch import embedding

# 加载环境变量
load_dotenv()
#嵌入模型
model_name=r"AI_DEMO\RAG\RAG_shoolwork\myProject\models\BAAI\bge-large-zh-v1.5"
embeddings=HuggingFaceEmbeddings(model_name=model_name)

#加载现有的Chroma数据库
persist_directory=r"chroma_db"
db=Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)
print(f"成功加载 Chroma 数据库从 {persist_directory}")

#实例化检索器
retriever=db.as_retriever(search_kwargs={"k":4})

query="name"

docs=retriever.invoke(query)
print(docs)
for i,doc in enumerate(docs,1):
    print(f"结果{i}:\n{doc.page_content}")