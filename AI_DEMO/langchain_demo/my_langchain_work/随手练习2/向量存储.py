import os

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

loader=PyPDFLoader(r"AI_DEMO\langchain_demo\my_langchain_work\文档包\01-RAG基础.pdf")
pages=loader.load_and_split()

text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=100,
    length_function=len,
    add_start_index=True,
)

# 将数据进行切割成块
paragraphs = text_splitter.create_documents([page.page_content for page in pages if pages])
#print(paragraphs)

embeddings=HuggingFaceEmbeddings(model_name=r"AI_DEMO\RAG\RAG_shoolwork\myProject\models\BAAI\bge-large-zh-v1.5")

db=Chroma(persist_directory="chroma_db",
          embedding_function=embeddings)

query="RAG作用是？"
docs=db.similarity_search(query)
for doc in docs:
    print(f"{doc}\n-------\n")