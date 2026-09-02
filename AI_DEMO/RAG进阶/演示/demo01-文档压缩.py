from base_llm import llm, embeddings_model
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import shutil
import os

# 1. 加载文档
doc=TextLoader("deepseek介绍.txt",encoding="utf-8").load()

# 2. 分割文档
text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,
                                             chunk_overlap=100)
texts=text_splitter.split_documents(doc)

# 3. 向量入库
chroma=Chroma.from_documents(
    documents=texts,
    embedding=embeddings_model,
    persist_directory="./chroma_db",
)

# 4. 得到一个检索器
retriver=chroma.as_retriever()
doc_result=retriver.invoke("deepseek的发展历程")

print("===========压缩前的效果=============")
if len(doc_result) == 0:
    print("警告：基础检索没有召回任何文档！检查文本内容与查询是否相关")
else:
    for d in doc_result:
        print("-" * 50)
        print(d.page_content)

print("===========压缩后的效果=============")
# 得到一个压缩器对象
compressor=LLMChainExtractor.from_llm(llm=llm)
# 得到一个压缩后的检索器,ContextualCompressionRetriever知识一个包装类，
compressed_retriver=ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriver
)

compressed_result=compressed_retriver.invoke("deepseek的发展历程")
for d in compressed_result:
    print("-" * 50)
    print(d.page_content)


