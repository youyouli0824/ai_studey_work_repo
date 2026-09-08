import re

from llama_index.core.prompts import RichPromptTemplate


# 方法：隐藏敏感信息
def hide_sensitive_info(text):
    # 隐藏姓名（假设格式为 "姓名：XXX"） +: 1次或多次
    text = re.sub(r'姓名：[^\n\r]+', '姓名：[已隐藏]', text)
    # 隐藏身份证号码（15位或18位数字） ？ 0次或1次
    text = re.sub(r'身份证：\d{15}(\d{2}[0-9Xx])?', '身份证：[已隐藏]', text)
    # 也可以隐藏其他格式的身份证 * 0次或多次
    text = re.sub(r'身份证[：:]\s*\d+[0-9Xx]*', '身份证：[已隐藏]', text)
    return text

# 对上下文进行格式化
def format_context_fn(**kwargs):
    #context=kwargs.get("context")
    context_str = kwargs["context_str"]
    # 隐藏敏感信息
    context_str = hide_sensitive_info(context_str)

    # 用项目符号格式化上下文
    context_list = context_str.split("\n\n")
    context_list = [c.strip() for c in context_list if c.strip()]
    return "\n\n".join([f"- {c}" for c in context_list])

templete_str = """
上下文信息如下:
--------------------- 
{{ context_str }} 
---------------------
给定上下文信息而不是先验知识，回答查询。
查询：{{ query_str }}
答案：
"""

# 模拟的上下文信息---假如是从RAG中检索出来的上下文片段
context_str = """\
姓名：小明

身份证：123456798123456

这项工作中，我们开发并发布了 Llama 2，这是一组经过预训练和微调的大型语言模型 (LLM)，其规模从 70 亿到 700 亿个参数不等。

我们经过微调的 LLM 称为 Llama 2-Chat，针对对话用例进行了优化。

在我们测试的大多数基准测试中，我们的模型都优于开源聊天模型，并且根据我们对有用性和安全性的人工评估，它们可能是闭源模型的合适替代品。
"""

# 函数映射。把context_str 传递映射到format_context_fn 函数中
rich_prompt = RichPromptTemplate(template_str=templete_str,
                                 function_mappings={"context_str":format_context_fn})

prompt=rich_prompt.format(context_str=context_str, query_str="Llama 2-Chat 是什么？")
print(prompt)
