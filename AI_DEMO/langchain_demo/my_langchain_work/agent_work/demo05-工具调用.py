# `WebBaseLoader`爬网页时缺少浏览器标识，部分网站会拦截无 UA 请求，如下：
# USER_AGENT environment variable not set, consider setting it to identify your requests.
import os

from langchain_openai import ChatOpenAI

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

# 查询 Tavily 搜索 API 并返回 json 的工具
search = TavilySearch(tavily_api_key=os.getenv("tavily_key"))
# # 执行查询
res = search.invoke("目前市场上苹果手机17的售价是多少？")
# {'query': '目前市场上苹果手机17的销量怎么样？', ...,'results': [{'url': 'https://www.ifanr.com/1642985', 'title': '苹果在中国营收依旧下滑，好消息是iPhone 17 卖爆了 - 爱范儿', 'content':
print(res)
# 获取第一个结果的url
#print(res['results'][0]['url'])
#url=res['results'][0]['url']

# 创建索引器根据上述查询的结果

# 加载HTML内容为一个文档对象,可以将上面获取的url作为参数
loader = WebBaseLoader("https://news.qq.com/rain/a/20260412A04DK800")
# 读取文档
docs = loader.load()
# print(docs)

# 分割文档
documents = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

# 向量化
vector = FAISS.from_documents(documents, DashScopeEmbeddings(dashscope_api_key=os.getenv('DASHSCOPE_API_KEY')))

# 创建检索器
retriever = vector.as_retriever()
# 测试检索结果
# print(retriever.invoke("目前市场上苹果手机17的销量是多少？"))

# 创建一个工具来检索文档----》检索器工具
retriever_tool = create_retriever_tool(
    retriever,
    "iPhone_price_search",
    "搜索有关 iPhone 17 的销量信息。对于iPhone 17的任何问题，您必须使用此工具！",
)

# 初始化大模型
llm = ChatOpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"),
                 base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                 model='qwen-plus', temperature=0)

# 定义提示词
hub = Client()
# ValueError: Pulling a public prompt by owner/name is disabled by default...set `dangerously_pull_public_prompt=True`
# prompt = hub.pull_prompt("hwchase17/openai-functions-agent")
prompt = hub.pull_prompt("hwchase17/openai-functions-agent", dangerously_pull_public_prompt=True)
# 打印Prompt
print(prompt)

# 创建将在下游使用的工具列表
tools = [search, retriever_tool]

# 创建智能体---》创建一个functions风格的智能体
from langchain_classic.agents import create_openai_functions_agent
agent=create_openai_functions_agent(llm,tools,prompt)

# 将工具列表传递给智能体去执行
from langchain_classic.agents import AgentExecutor
# 智能体执行器
executor=AgentExecutor(agent=agent,tools=tools,verbose=True)
#print(executor.invoke({"input":"目前市场上苹果手机17的销量是多少？"}))
print(executor.invoke({"input":"哪个女明星最漂亮？"}))

