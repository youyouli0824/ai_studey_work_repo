from urllib import response

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

llm = ChatOpenAI(api_key=os.getenv("API_KEY"),
                 base_url=os.getenv("BASE_URL"),
                 model_name="deepseek-v4-flash")

response=llm.invoke("什么是大模型？")
print(response)
print("--------")
print(response.content)