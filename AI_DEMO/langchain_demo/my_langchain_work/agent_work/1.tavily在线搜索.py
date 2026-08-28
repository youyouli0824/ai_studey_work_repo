# `WebBaseLoader`爬网页时缺少浏览器标识，部分网站会拦截无 UA 请求，如下：
# USER_AGENT environment variable not set, consider setting it to identify your requests.
import os

from langchain_openai import ChatOpenAI
from openai import api_key

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
# 加载所需的库
import os
from langsmith import Client
from langchain_tavily import TavilySearch
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_core.tools.retriever import create_retriever_tool

load_dotenv()

search=TavilySearch(tavily_api_key=os.getenv("TAVILY_API_KEY"))
res=search.invoke("目前市场上苹果手机17的销量怎么样？")
#print(res)

# 获取第一个结果的url
#print(res['results'][0]['url'])
url=res['results'][0]['url']
#加载HTML为一个文档对象
loader=WebBaseLoader(f"{url}")
docs=loader.load()
#print(docs)

#分割文档
documents=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200).split_documents(docs)

#文档向量化
vector=FAISS.from_documents(documents,DashScopeEmbeddings(api_key=os.getenv("API_KEY")))

#创建检索器
retriever=vector.as_retriever()
#测试检索
print(retriever.invoke("目前市场上苹果手机17的销量是多少？"))

#创建工具，检索文档--检索器工具
retriever_tool=create_retriever_tool(
    retriever,
    "iPhone_price_search",
    "搜索有关iPhone 17 的销量信息。"
)

#初始化大模型
llm=ChatOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model="deepseek-v4-flash",
    temperature=0.4
)

#提示词
hub=Client()
prompt=hub.pull_prompt("hwchase17/openai-functions-agent", dangerously_pull_public_prompt=True)

#创建要使用的工具列表
tools=[search,retriever_tool]

#创建智能体
from langchain_classic.agents import create_openai_functions_agent

agent=create_openai_functions_agent(
    llm,
    tools,
    prompt
)

#将工具列表传递给智能体去执行
from langchain_classic.agents import AgentExecutor

executor=AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)
print(executor.invoke({"input":"《火影忍者》的主角头发是什么颜色的？"}))