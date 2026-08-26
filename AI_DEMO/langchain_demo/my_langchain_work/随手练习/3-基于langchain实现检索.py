import os
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv

load_dotenv()

#创建嵌入模型
embeddings=DashScopeEmbeddings(
    dashscope_api_key=os.getenv("API_KEY"),
    model="text-embedding-v4"
)
#加载本地FAISS索引
save_path="faiss_index"

vector_store=FAISS.load_local(
    folder_path=save_path,
    embeddings=embeddings,
    allow_dangerous_deserialization=True#允许加载pickle文件（仅可信文件）
)
#创建提示模板
prompt=ChatPromptTemplate.from_template("""仅根据提供的上下文回答以下问题:

<context>
{context}
</context>

问题: {input}""")

# 创建 LLM 连接（继续使用阿里云 qwen-plus）
llm = ChatOpenAI(
    api_key=os.getenv("API_KEY"),  # 确保环境变量名为API_KEY
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus"
)

#创建文档组合链
document_chain=create_stuff_documents_chain(llm,prompt)
#创建检索器
retriever=vector_store.as_retriever(search_kwargs={"k":3})#限制检索3个文档
#创建检索链
retrieval_chain=create_retrieval_chain(retriever,document_chain)
#调用检索链，获取回答
response=retrieval_chain.invoke({"input":"xxxxx"})

print("\n回答:",response["answer"])