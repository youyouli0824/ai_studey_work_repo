from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv()

# 创建提示词
prompt = ChatPromptTemplate.from_template("tell me a short joke about {topic}")

#创建llm模型
model=ChatOpenAI(api_key=os.getenv("API_KEY"),
                 base_url=os.getenv("BASE_URL"),
                 model="deepseek-v4-flash")

#创建输出解释器
output_parser=StrOutputParser()

#使用chain链在一起
chain = prompt | model | output_parser
print(chain.invoke({"topic":"ice cream"}))