from llama_index.core.prompts import RichPromptTemplate

prompt_template ="""
        # 任务说明
        你是企业信息问答助手，需严格基于提供的上下文信息回答问题，不得编造内容。
        # 上下文信息
        ---------------------
        {{ context_str }}
        
        ---------------------
        # 待回答问题
        {{ query_str }}
        
        # 回答要求:
        1. 严格按照问题要求的格式回答；
        2. 仅使用上下文里的信息，不添加额外解释；
        3. 若上下文无相关信息，回复："未查询到相关信息"。
        """

template=RichPromptTemplate(prompt_template)

# 模拟上下文信息
context_str = """
【企业基础信息】
公司全称：杭州深度求索人工智能基础技术研究有限公司
成立时间：2023年7月17日（工商注册日期）
核心技术：数据蒸馏技术（用于优化大语言模型训练数据）
股东背景：由幻方量化（知名私募机构）孵化
注册地址：浙江省杭州市拱墅区环城北路169号汇金国际大厦西1幢1201室
法定代表人：裴湉
核心业务：大语言模型（LLM）研发、技术服务、软件开发、技术转让
【补充说明】
1. 公司成立后6个月内完成首轮融资，估值超10亿人民币；
2. 数据蒸馏技术为公司核心专利，已应用于多款自研大模型。
"""

query_str="DeepSeek公司是哪年处理的？"

# 格式化提示词
# format方法回到一个纯字符串！
prompt=template.format(context_str=context_str,query_str=query_str)
print("prompt:",prompt)

# 格式化提示词为消息列表，会得到一个ChatMessage数组，每个对象内部都会包含role、additional_kwargs、blocks等属性
# 该类型特别适合聊天模型
messages_prompt=template.format_messages(context_str=context_str,query_str=query_str)
# [ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='# 任务
print("messages_prompt:",messages_prompt)


