from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
import os
from dotenv import load_dotenv
from sympy import fu
load_dotenv()

#定义查询订单状态的函数
def query_order_status(order_id):
    if order_id == "1024":
        return "订单 1024 的状态是：已发货，预计送达时间是 3-5 个工作日。"
    else:
        return f"未找到订单 {order_id} 的信息，请检查订单号是否正确。"

#定义退款政策说明函数
def company_refund_policy(company_name):
    print(company_name)
    if company_name=="tom":
        return "tom公司的退款政策是：在购买后7天内可以申请全额退款，需提供购买凭证。"
    else:
        print("输入有误")

#查询年龄
def get_age(name):
    if name=="tom":
        print(name)
        return "我的年龄是56岁！"
    else:
        print("输入有误")

#创建工具列表
tools = [
    TavilySearch(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=1),
    Tool(
        name="query_order_status",
        func=query_order_status,
        description="根据订单id查询订单状态",
        args={"order_id":"订单的id"}
    ),
    Tool(
        name="company_refund_policy",
        func=company_refund_policy,
        description="查询不同公司的退款政策",
        args={"company_name":"公司名称"}
    ),
    Tool(
        name="get_age",
        func=get_age,
        description="根据姓名查询年龄",
        args={"name":"姓名"}
    )
]

#创建LLM，作为Agent的大脑
llm=ChatOpenAI(api_key=os.getenv("API_KEY"),
               base_url=os.getenv("BASE_URL"),
               model="deepseek-v4-flash")

#创建Agent
agent=create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个客服助手，使用工具回答问题。传递给工具的内容必须是准确的json数据,如果是字符串数据必须和输入的保持一致,要完整,不能篡改。如果是调用company_refund_policy工具，传递的参数不能包含‘公司’二字**重要规则**"

)

# 提供测试问题：
queries = [
    "请问订单1024的状态是什么？",
    "请问tom公司退款政策是什么？",
    "2024年谁胜出了美国总统的选举"
]

for query in queries:
    print("客户的问题：",query)
    # 设计用户提示词
    inputs = {"messages":[{"role":"user","content":query}]}
    # 调用agent
    result = agent.invoke(inputs)
    print(result["messages"][-1].content)