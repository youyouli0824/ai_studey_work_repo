from langchain_core.prompts.chat import ChatPromptTemplate
# 导入LangChain中的ChatOpenAI模型接口
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

template = "你是一个数学家，你可以计算任何算式"
human_template="{text}"

chat_prompt=ChatPromptTemplate.from_messages([
    ("system",template),
    ("human",human_template),
])
#print(chat_prompt)

model=ChatOpenAI(api_key=os.getenv("API_KEY"),
                 base_url=os.getenv("BASE_URL"),
                 model="deepseek-v4-flash")

#输入提示
messages=chat_prompt.format_messages(text="我今年18岁，我的舅舅今年38岁，我的爷爷今年72岁，我和舅舅一共多少岁了？")
#print(messages)

#得到模型输出
output=model.invoke(messages)

#结果
print(output.content)