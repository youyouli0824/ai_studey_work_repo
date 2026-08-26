# 导入LangChain中的OpenAI模型接口
from langchain_openai import ChatOpenAI
# 导入LangChain中的提示模板
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
#创建模型实例
model=ChatOpenAI(api_key=os.getenv("API_KEY"),
                 base_url=os.getenv("BASE_URL"),
                 model="deepseek-v4-flash")
prompt=PromptTemplate(
    template="您是一位专业的程序员。\n对于信息{text}进行简短描述"
)

#输入提示
input = prompt.format(text="大模型langchain")

#得到模型的输出
output=model.invoke(input)

#打印输出
print(output.content)