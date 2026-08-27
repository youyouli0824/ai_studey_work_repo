from langchain_classic.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

template= "桌上有{number}个苹果，四个桃子和 3 本书，一共有几个水果?"

#创建实例模型
llm=ChatOpenAI(api_key=os.getenv("API_KEY"),
               base_url=os.getenv("BASE_URL"),
               model="deepseek-v4-flash",
               temperature=0.4)

#创建LLMChain
llm_chain=LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(template)
)

#调用LLMChain，返回结果
result=llm_chain.invoke({"number":2})
print(result)
print(type(result))
print(result['text'])