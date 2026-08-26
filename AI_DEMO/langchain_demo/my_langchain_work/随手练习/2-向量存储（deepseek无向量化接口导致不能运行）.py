import os
from langchain_community.document_loaders import WebBaseLoader
import bs4
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from torch import embedding

# 加载环境变量
load_dotenv()
#初始化WebBaseLoader
loader = WebBaseLoader(
    'https://www.gov.cn/zhengce/content/202510/content_7043916.htm',
    bs_kwargs=dict(parse_only=bs4.SoupStrainer(id='UCAP-CONTENT'))
)
docs=loader.load()

#分割文档
text_splitter =RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
)
documents=text_splitter.split_documents(docs)
print(f"总文档数量：{len(documents)}")

#初始化DashScope嵌入模型
embeddings=DashScopeEmbeddings(
    dashscope_api_key=os.getenv("API_KEY"),
    model="text-embedding-v4"
)

#初始化FAISS索引
vector=None
batch_size=10

# 分批处理文档
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i + batch_size]
    print(f'第{i // batch_size + 1}批次 文档数量: {len(batch_docs)}')

    # 第一批：创建新的 FAISS 索引
    if i == 0:
        vector = FAISS.from_documents(batch_docs, embeddings)
    # 后续批次：将新文档添加到现有索引
    else:
        new_vector = FAISS.from_documents(batch_docs, embeddings)
        vector.merge_from(new_vector)  # 合并新索引到现有索引


vector.save_local("faiss_index")
print("FAISS 索引已保存到 faiss_index 文件夹")