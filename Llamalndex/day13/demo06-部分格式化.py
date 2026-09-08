import re

from llama_index.core.prompts import RichPromptTemplate

qa_prompt_tmpl_str = """\
上下文信息如下:
---------------------
{{ context_str }}
---------------------
给定上下文信息而不是先验知识，回答查询。
请以 {{ tone_name }} 的语气写出答案
查询: {{ query_str }}
答案: 
"""

# 函数映射。把context_str 传递映射到format_context_fn 函数中
rich_prompt = RichPromptTemplate(qa_prompt_tmpl_str)
# 得到了一个“半成品”的提示词，需要再格式化一次才能使用
partial_prompt = rich_prompt.partial_format(tone_name="赵本山")
#print(partial_prompt)

# 用格式化后的半成品提示词再次格式化，得到最终的提示词
prompt=partial_prompt.format(context_str="在这项工作中，我们开发并发布了 Llama 2，这是一组经过预训练和微调的大型语言模型 (LLM)，其规模从 70 亿到 700 亿个参数不等",
    query_str="llama 2 有多少个参数")
print(prompt)
