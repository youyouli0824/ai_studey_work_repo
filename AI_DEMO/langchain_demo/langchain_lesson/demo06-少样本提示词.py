from langchain_openai import ChatOpenAI
# 导入LangChain中的提示模板
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3.7-plus"
)

# few‑shot示范样本
examples = [
    {"input": "2+2", "output": "4", "description": "加法运算"},
    {"input": "5-2", "output": "3", "description": "减法运算"},
]

# example_prompt：专门渲染examples里面的每一条样例，给模型观摩学习
example_prompt = PromptTemplate.from_template(
    "算式：{input}，值：{output}，使用：{description}"
)

shotPrompt=FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    # 任务指令，告诉模型要完成的任务
    suffix="请严格模仿上面示例的格式，完成下面的算式。输出格式必须和例子完全一致。算式为：{input}",
    # 输入变量
    input_variables=["input"]
)

# 填充提示词模板中的占位符
input=shotPrompt.format(input="3*2")
res=llm.invoke(input)
print(res.content)
