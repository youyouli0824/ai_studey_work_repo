# -*- coding: utf-8 -*-
"""
prompt_demo.py —— 模块3：多种提示词模板演示
============================================================
逐个演示 LangChain 的三类核心提示词模板，每个模板封装为独立函数，
可单独调用运行。通过“输入提示(Format) → 调用模型(Predict) → 输出解析(Parse)”
的 Model I/O 流程，展示如何用模板快速、稳定地驱动大模型。

对应知识点（课程学习清单）：
    1. PromptTemplate          基础字符串提示模板 —— 文档摘要
    2. ChatPromptTemplate      聊天提示模板（system + human 角色消息）—— 翻译功能
    3. FewShotPromptTemplate   少样本提示模板（示例教学）—— 流程步骤列表

运行方式：
    python prompt_demo.py
"""

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    PromptTemplate,
)

from embeddings import get_llm

# 样例文档片段（模拟一段企业制度文档，用于摘要演示）
SAMPLE_DOC = (
    "为加强公司考勤管理，规范员工出勤行为，根据国家有关规定结合公司实际情况，"
    "特制定本制度。员工上下班需通过人脸识别闸机打卡，每日两次。"
    "因公外出需提前在OA系统提交外出申请单，经部门负责人审批后方可外出。"
    "迟到或早退超过30分钟按旷工半天处理，全年累计旷工超过3天将影响年终绩效评定。"
)


# ---------------- 模板一：PromptTemplate 基础字符串模板 ----------------
def summarize_with_prompt_template(text: str) -> str:
    """
    文档内容摘要（对应知识点：PromptTemplate）。

    使用 String 提示模板，将固定指令与动态文本 {text} 组合成提示词，
    让大模型对文档片段生成简短摘要。

    参数:
        text: 待摘要的文档片段

    返回:
        摘要文本
    """
    # 创建提示模板：模板化字符串，{text} 是变量占位符，运行时可动态填充
    prompt = PromptTemplate(
        template="你是一位专业的企业制度梳理助手。\n"
                 "请用一句话简要概括以下文档片段的核心内容：\n{document}",
        input_variables=["document"],
    )

    # 输入提示：把变量值填入模板，生成最终提示词字符串
    input_text = prompt.format(document=text)

    # 调用模型（Predict），得到输出
    llm = get_llm()
    output = llm.invoke(input_text)
    return output.content


# ---------------- 模板二：ChatPromptTemplate 聊天提示模板 ----------------
def translate_with_chat_template(text: str, target_lang: str = "中文") -> str:
    """
    简单翻译功能（对应知识点：ChatPromptTemplate）。

    聊天提示模板由多条不同角色的消息组成：
        system 角色：定义助手身份与翻译规则
        human  角色：传入待翻译的文本
    演示 system + human 角色消息的用法。

    参数:
        text: 待翻译文本
        target_lang: 目标语言

    返回:
        翻译结果
    """
    # 聊天模板：messages 列表，每项是 (角色, 内容)，支持 {变量} 占位符
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一名资深翻译专家，擅长把任意语言翻译成 {target_lang}，只输出译文不输出多余内容。"),
            ("human", "请翻译以下内容：{text}"),
        ]
    )

    # 格式化提示消息，得到可以直接传给聊天模型的消息列表
    messages = chat_prompt.format_messages(text=text, target_lang=target_lang)

    # 调用模型
    llm = get_llm()
    output = llm.invoke(messages)
    return output.content


# ---------------- 模板三：FewShotPromptTemplate 少样本提示模板 ----------------
def process_steps_with_fewshot(question: str) -> str:
    """
    流程类问题步骤列表（对应知识点：FewShotPromptTemplate）。

    提供 2 组“问题 → 步骤列表”的输入输出示例，教会大模型
    流程类问题的标准回答格式，强制输出 “1.xxx\n2.xxx” 有序列表，
    有效抑制输出格式混乱。

    参数:
        question: 流程类问题

    返回:
        有序步骤列表
    """
    # 示例集：每个示例是一个字典，键为输入变量名，值为对应的输入输出
    examples = [
        {"question": "员工请年假需要什么流程？",
         "steps": "1. 登录OA系统填写《年假申请单》\n2. 直属主管审批\n3. HR备案生效"},
        {"question": "员工报销差旅费需要什么流程？",
         "steps": "1. 整理发票填写《报销单》\n2. 部门负责人签字\n3. 财务审核打款"},
    ]

    # 定义每个示例如何格式化成字符串
    example_prompt = PromptTemplate.from_template("问：{question}\n答：\n{steps}")

    # 少样本提示模板：examples 提供示范，suffix 是实际要回答的问题
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="你是一名企业流程解答助手。请严格按照示例的格式回答，"
               "必须用“1.xxx\\n2.xxx”的有序列表输出步骤，不要输出其他格式。",
        suffix="问：{question}\n答：",
        input_variables=["question"],
    )

    # 格式化出带示例的完整提示词
    final_prompt = few_shot_prompt.format(question=question)

    # 调用模型
    llm = get_llm()
    output = llm.invoke(final_prompt)
    return output.content


# ---------------- 主入口：依次演示三类模板 ----------------
def main() -> None:
    """依次运行三类提示词模板演示。"""
    print("=" * 60)
    print("模块3：三种提示词模板演示")
    print("=" * 60)

    # 1) PromptTemplate 基础字符串模板 —— 文档摘要
    print("\n[1/3] PromptTemplate 基础字符串模板 —— 文档摘要")
    print("-" * 60)
    summary = summarize_with_prompt_template(SAMPLE_DOC)
    print("摘要:", summary)

    # 2) ChatPromptTemplate 聊天提示模板 —— 翻译
    print("\n[2/3] ChatPromptTemplate 聊天提示模板 —— 翻译（system + human 角色消息）")
    print("-" * 60)
    translated = translate_with_chat_template(
        "Artificial intelligence is transforming the manufacturing industry.",
        target_lang="中文",
    )
    print("译文:", translated)

    # 3) FewShotPromptTemplate 少样本提示模板 —— 流程步骤列表
    print("\n[3/3] FewShotPromptTemplate 少样本提示模板 —— 流程步骤列表")
    print("-" * 60)
    steps = process_steps_with_fewshot("员工申请调休需要什么流程？")
    print("回答:")
    print(steps)

    print("\n" + "=" * 60)
    print("三类提示词模板演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
