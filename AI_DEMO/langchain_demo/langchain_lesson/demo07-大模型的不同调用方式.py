from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 调用方式1：直接调用模型
# llm = ChatOpenAI(
#     api_key=os.getenv("DASHSCOPE_API_KEY"),
#     base_url=os.getenv("DASHSCOPE_BASE_URL"),
#     model="qwen3.7-plus"
# )
#
# res=llm.invoke("什么是大模型？")
# print(res.content)

# 调用方式2：init_chat_model,这种写法不支持阿里千文模型
# from langchain.chat_models import init_chat_model
# llm2=init_chat_model(
#     model="deepseek-v4-pro",
#     api_key=os.getenv("DEEPSEEK_API_KEY"),
#     base_url=os.getenv("DEEPSEEK_BASE_URL"),
# )
#
# res2=llm2.invoke("什么是大模型？")
# print(res2.content)

# 调用方式3：调用deepseek特有的模型
from langchain_deepseek import ChatDeepSeek

llm3=ChatDeepSeek(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model_name="deepseek-reasoner")

res3=llm3.invoke("什么是大模型")
print(res3.content)
