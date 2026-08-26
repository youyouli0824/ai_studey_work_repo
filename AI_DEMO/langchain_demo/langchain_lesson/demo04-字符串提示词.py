from langchain_openai import ChatOpenAI
# 导入LangChain中的提示模板
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3.7-plus"
)
# 设计提示词模板
prompt=PromptTemplate(template="您是一位专业的程序员。\n请对如下信息：{text} 进行简短描述")
# 填充提示词模板中的占位符
# 您是一位专业的程序员。\n请对如下信息：大模型 进行简短描述
input=prompt.format(text="大模型")
res=llm.invoke(input)
print(res)
