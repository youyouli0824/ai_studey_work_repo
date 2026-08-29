from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
load_dotenv()

llm=ChatOpenAI(api_key=os.getenv("API_KEY"),
               base_url=os.getenv("BASE_URL"),
               model_name="deepseek-v4-flash")

response=llm.invoke("你好，我是liyouyou")

print(response.content)

response=llm.invoke("我是谁？")

print(response.content)

#结果说明了没有记忆