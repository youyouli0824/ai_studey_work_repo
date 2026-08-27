from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# 创建解析器
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser, XMLOutputParser
from langchain_classic.chains import LLMChain  # 新增：导入 LLMChain 用于非 LCEL 链式调用
from dotenv import load_dotenv
import os

load_dotenv()

model=ChatOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model="deepseek-v4-flash",
)

xml_parser=XMLOutputParser()

prompt=ChatPromptTemplate.from_messages([
    ("system","你是一个专业程序员"),
    ("user","{input}")
])

#使用LLMChain构建链
chain=LLMChain(
    llm=model,
    prompt=prompt,
    output_parser=xml_parser#指定输出解析器
)

res=chain.invoke({"input":"langchain是什么？使用xml格式输出"})

print(res)