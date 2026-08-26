# -*- coding: utf-8 -*-
"""
rag_chat.py —— 模块2：知识库问答 RAG 核心模块
============================================================
职责：加载本地 FAISS 向量库 → 用户输入自然语言问题 →
      检索相关文档片段 → 结合提示词模板交给大模型 → 返回基于资料的精准回答。

两个问答入口：
    1. ask_rag(question)        —— 通用制度问答（ChatPromptTemplate 聊天模板）
    2. ask_process(question)    —— 流程类问答（FewShotPromptTemplate 少样本模板，强制输出步骤列表）

对应知识点（课程学习清单）：
    · FAISS.load_local            加载本地向量库（allow_dangerous_deserialization=True）
    · ChatPromptTemplate          聊天提示词模板（区分 system / human 角色消息）
    · create_stuff_documents_chain 文档合并链（把检索到的文档塞进上下文）
    · create_retrieval_chain      完整 RAG 检索链
    · FewShotPromptTemplate       少样本提示模板（流程类问题固定输出格式）
"""

import os
import sys

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain

from embeddings import get_embeddings, get_llm, resolve_project_path

# 加载 .env 环境变量
load_dotenv()

# RAG 主业务提示词：ChatPromptTemplate 聊天模板，区分 system（系统指令）与 human（用户问题）角色
RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        # system 角色：约束模型行为，强制只基于检索上下文回答，抑制大模型幻觉
        (
            "system",
            "你是一名企业内部制度问答助手。请严格遵守以下规则：\n"
            "1. 只允许根据 <context> 中提供的企业资料回答，禁止编造、联想或补充上下文中不存在的制度内容；\n"
            "2. 如果检索到的资料与问题无关或找不到相关资料，直接回复：知识库未查询到相关制度；\n"
            "3. 回答应简洁、准确、条理清晰，可以引用条款原文。",
        ),
        # human 角色：注入检索到的上下文 + 用户问题
        (
            "human",
            "<context>\n{context}\n</context>\n\n问题：{input}",
        ),
    ]
)

# 流程类问答的少样本示例（2 组输入-输出样例，教模型输出标准步骤列表）
PROCESS_EXAMPLES = [
    {
        "question": "员工请年假需要什么流程？",
        "steps": "1. 登录内部OA系统填写《年假申请单》\n2. 直属主管在系统内审批\n3. HR 部门备案后生效",
    },
    {
        "question": "员工报销差旅费需要什么流程？",
        "steps": "1. 整理发票并填写《费用报销单》\n2. 部门负责人签字确认\n3. 财务部审核无误后打款",
    },
]
# 每个示例的格式化模板
PROCESS_EXAMPLE_PROMPT = PromptTemplate.from_template(
    "问：{question}\n答（步骤列表）：\n{steps}"
)
# 流程类问答的少样本提示模板（对应知识点：FewShotPromptTemplate）
PROCESS_PROMPT = FewShotPromptTemplate(
    examples=PROCESS_EXAMPLES,
    example_prompt=PROCESS_EXAMPLE_PROMPT,
    prefix="你是一名企业流程解答助手。请严格按照示例的格式，用“1.xxx\\n2.xxx”的有序列表回答流程类问题。",
    suffix="参考资料：\n{context}\n\n请用有序列表回答以下流程类问题：\n{question}",
    input_variables=["context", "question"],
)


def load_vector_store():
    """
    加载本地已构建的 FAISS 向量库（对应知识点：FAISS.load_local）。

    注意：allow_dangerous_deserialization=True 允许加载 pickle 文件，
    仅适用于可信的本地文件（课程知识文档中原样要求）。

    返回:
        FAISS 向量库实例（retriever 可检索）
    """
    # 解析为基于项目根目录的绝对路径，兼容从任意目录运行
    save_dir = resolve_project_path(os.getenv("FAISS_DIR", "faiss_store"))

    # 向量库不存在时给出友好提示，引导先运行 build_knowledge.py
    if not os.path.isdir(save_dir):
        raise FileNotFoundError(
            f"未找到向量库目录 {save_dir}，请先运行: python build_knowledge.py 构建知识库"
        )

    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        folder_path=save_dir,
        embeddings=embeddings,
        allow_dangerous_deserialization=True,  # 允许反序列化本地 pickle（仅可信文件）
    )
    return vector_store


def build_rag_chain(vector_store):
    """
    构建完整 RAG 检索链（对应知识点：create_stuff_documents_chain + create_retrieval_chain）。

    RAG 流程：
        用户问题 → 检索器召回相关文档片段 → 文档合并链把片段填入提示词上下文
                → 大模型基于上下文生成答案

    参数:
        vector_store: 已加载的 FAISS 向量库

    返回:
        tuple: (retrieval_chain, retriever)
            - retrieval_chain: 完整 RAG 检索链（invoke 后返回 answer + context）
            - retriever: 检索器（流程类问答单独取上下文时复用）
    """
    # 1) 创建检索器：从向量库中召回最相关的 k 个文档片段
    k = int(os.getenv("RETRIEVER_K", "3"))
    retriever = vector_store.as_retriever(search_kwargs={"k": k})

    # 2) 创建文档合并链：把检索到的文档片段填进提示词的 {context} 占位符
    llm = get_llm()
    document_chain = create_stuff_documents_chain(llm, RAG_PROMPT)

    # 3) 组装完整 RAG 检索链：先检索、后生成
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    return retrieval_chain, retriever


def ask_rag(retrieval_chain, question: str) -> dict:
    """
    通用制度问答入口（ChatPromptTemplate 聊天模板）。

    参数:
        retrieval_chain: RAG 检索链
        question: 用户自然语言问题

    返回:
        dict，包含 answer（模型答案）与 sources（检索到的参考来源 URL 列表）
    """
    response = retrieval_chain.invoke({"input": question})

    # 提取检索到的参考文档来源（网页 url），去重输出
    sources = list({d.metadata.get("source", "未知来源") for d in response.get("context", [])})
    return {"answer": response.get("answer", ""), "sources": sources}


def ask_process(retriever, question: str) -> dict:
    """
    流程类问答入口（FewShotPromptTemplate 少样本模板，强制输出步骤列表）。

    先检索相关资料作为参考上下文，再用少样本模板约束模型
    必须输出 “1.xxx\n2.xxx” 格式的有序步骤列表，抑制输出格式混乱。

    参数:
        retriever: 检索器（从向量库召回相关文档）
        question: 流程类问题

    返回:
        dict，包含 answer（步骤列表答案）与 sources（参考来源 URL）
    """
    # 召回相关资料作为参考上下文
    context_docs = retriever.invoke(question)
    context_text = "\n\n".join(d.page_content for d in context_docs)
    sources = list({d.metadata.get("source", "未知来源") for d in context_docs})

    # 用少样本提示模板格式化出最终提示词
    prompt_text = PROCESS_PROMPT.format(context=context_text, question=question)

    # 调用大模型生成步骤列表
    llm = get_llm()
    answer = llm.invoke(prompt_text).content
    return {"answer": answer, "sources": sources}


def main() -> None:
    """RAG 问答主入口：启动交互式问答控制台。"""
    print("=" * 60)
    print("企业内部知识库 RAG 问答系统")
    print("=" * 60)

    try:
        # 加载本地向量库并构建 RAG 检索链（同时拿到检索器）
        print("[加载] 本地 FAISS 向量库...")
        vector_store = load_vector_store()
        retrieval_chain, retriever = build_rag_chain(vector_store)
        print("[就绪] RAG 检索链构建完成，开始问答。")

    except Exception as e:
        # 向量库缺失 / 密钥缺失 / API 异常统一友好提示
        print(f"\n[启动失败] {e}")
        sys.exit(1)

    print("-" * 60)
    print("支持的命令：")
    print("  输入任意问题          → 通用制度问答")
    print("  输入 流程：<问题>     → 流程类问答（少样本模板，输出步骤列表）")
    print("  输入 quit 或 exit     → 退出系统")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n请输入问题: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                print("再见！")
                break
            if not user_input:
                continue

            # 流程类问题：以“流程：”开头的输入走少样本模板
            if user_input.startswith("流程："):
                question = user_input[3:].strip()
                print("\n[少样本模板] 流程类问答...")
                result = ask_process(retriever, question)
            # 其余走通用 RAG 问答
            else:
                print("\n[检索生成] 正在查询知识库...")
                result = ask_rag(retrieval_chain, user_input)

            # 输出：①模型答案 ②检索到的参考文档来源（网页 url）
            print("\n回答: ", result["answer"])
            if result["sources"]:
                print("参考来源: ")
                for s in result["sources"]:
                    print("  -", s)

        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"\n[问答出错] {e}")


if __name__ == "__main__":
    main()
