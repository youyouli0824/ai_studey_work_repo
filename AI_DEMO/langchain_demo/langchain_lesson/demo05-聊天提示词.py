from langchain_openai import ChatOpenAI
# 导入LangChain中的提示模板
from langchain_core.prompts import ChatPromptTemplate

import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3.7-plus"
)

# 提示词文本
template = "你是一个翻译专家,擅长将{input_language}语言翻译成 {output_language}语言."
# 聊天提示词模板
chat_prompt=ChatPromptTemplate.from_messages([
        ("system",template),
        ("human","{text}")
    ])

# 填充提示词模板中的占位符
input=chat_prompt.format_messages(input_language="中文",output_language="英文",text="今天星期二，还有好几天过周末")

res=llm.invoke(input)
print(res)
