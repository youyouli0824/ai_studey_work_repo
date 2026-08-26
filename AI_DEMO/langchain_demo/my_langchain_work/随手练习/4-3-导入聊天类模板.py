from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 系统模板的构建
system_template = "你是一个翻译专家,擅长将 {input_language} 语言翻译成 {output_language}语言."
system_message_prompt=SystemMessagePromptTemplate.from_template(system_template)

#用户模板的构建
human_template="{text}"
human_message_prompt=HumanMessagePromptTemplate.from_template(human_template)

#组装成最终模板
prompt_template=ChatPromptTemplate.from_messages([system_message_prompt,human_message_prompt])

#格式化提示消息生成提示
prompt=prompt_template.format_prompt(input_language="英文",
                                     output_language="中文",
                                     text="i love large language model").to_messages()
#打印模板
print("prompt:",prompt)

model=ChatOpenAI(api_key=os.getenv("API_KEY"),
                 base_url=os.getenv("BASE_URL"),
                 model="deepseek-v4-flash")

result=model.invoke(prompt)

print("result:",result.content)