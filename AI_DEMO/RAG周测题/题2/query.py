# -*- coding: utf-8 -*-
"""
企业制度问答调用主流程入口（query.py）—— 独立入口二
====================================================
加载已构建的 FAISS 向量库，组装完整 RAG「检索-生成」链路，
对用户问题给出严格基于文档的 JSON 格式回答。

流程：
1. 从 config 读取全部配置（.env 管理）
2. 加载本地 FAISS 向量库 → 构造检索器 retriever
3. ChatPromptTemplate 构建提示词（强制约束：检索不到就固定回复，禁止编造）
4. JsonOutputParser 输出解析器 + create_stuff_documents_chain
   + create_retrieval_chain 组装完整 RAG 链
5. 最终以 JSON 输出：{"answer": "回答内容", "source": ["来源文档名"]}

用法：
    python query.py "财务报销的流程是什么"   # 命令行传入问题
    python query.py                          # 交互式输入问题
"""
import json
import sys
import warnings
from pathlib import Path

# 屏蔽 langchain-community 迁移期的噪音警告，保证运行截图干净
warnings.filterwarnings("ignore", message=r"`langchain-community` is being sunset.*")

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import settings
from faiss_io import load_local

# 固定兜底回复：检索不到相关制度时统一返回，禁止编造
NO_DATA_ANSWER = "知识库中暂无相关制度信息"

# 提示词模板：{context}=检索到的制度片段，{input}=用户问题
SYSTEM_PROMPT = f"""你是企业行政部的制度问答助手。请严格基于下面提供的《企业制度》检索片段回答员工的问题，禁止编造任何文档中不存在的内容。

<检索到的制度片段>
{{context}}
</检索到的制度片段>

回答要求：
1. 只依据上面检索片段中的信息作答，不引入片段之外的任何知识；
2. 如果检索片段与问题无关、或没有检索到相关制度信息，必须一律回复“{NO_DATA_ANSWER}”，不要编造；
3. 最终只输出一个 JSON 对象，包含两个字段：
   - "answer"：对用户问题的回答内容；
   - "source"：回答所依据的制度文档名（取自片段中的 source 元数据）；无资料时为空字符串。

用户问题：{{input}}"""


def build_rag_chain():
    """组装完整 RAG 链路：向量库 → 检索器 → 提示词 → LLM → 输出解析 → 检索生成链。"""
    # 1. 向量化实例（与构建知识库时保持一致）
    if not settings.dashscope_api_key:
        print("[错误] 未配置 DASHSCOPE_API_KEY，请在 .env 中填写")
        sys.exit(1)
    embeddings = DashScopeEmbeddings(
        dashscope_api_key=settings.dashscope_api_key,
        model=settings.embed_model,
    )

    # 2. 加载本地持久化的 FAISS 向量库，并构造检索器（返回 TopK 条相关文档）
    if not Path(settings.faiss_index_path).exists():
        print(f"[错误] 向量库不存在：{settings.faiss_index_path}，请先运行 python build_index.py")
        sys.exit(1)
    vectorstore = load_local(settings.faiss_index_path, embeddings)  # faiss_io 兼容中文路径
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.top_k})
    print(f"[检索] 已加载向量库：{settings.faiss_index_path}（TopK={settings.top_k}）")

    # 3. 对话模型：DeepSeek（OpenAI 兼容接口）
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
    )
    print(f"[模型] 对话模型：{settings.llm_model}")

    # 4. 提示词 + 输出解析器
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{input}")]
    )
    output_parser = JsonOutputParser()  # 输出解析：把 LLM 输出解析为 JSON 对象

    # 5. 组装完整 RAG 链
    #    create_stuff_documents_chain：把检索到的文档"塞进"提示词的 {context}，交给 LLM 生成
    #    create_retrieval_chain：先检索再生成，返回 {"context": 文档列表, "answer": 解析后JSON}
    combine_docs_chain = create_stuff_documents_chain(
        llm, prompt, output_parser=output_parser
    )
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
    return rag_chain


def get_question() -> str:
    """获取用户问题：优先命令行参数，否则交互输入。"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return input("请输入您的问题：").strip()


def extract_sources(context_docs: list) -> list:
    """从检索到的文档元数据中提取去重后的来源文档名（保证 source 真实可靠）。"""
    sources = []
    for doc in context_docs:
        name = Path(doc.metadata.get("source", "")).name or "未知文档"
        if name not in sources:
            sources.append(name)
    return sources


def main() -> None:
    question = get_question()
    if not question:
        print("[错误] 问题不能为空")
        sys.exit(1)

    # 组装 RAG 链并调用「检索-生成」全流程
    rag_chain = build_rag_chain()
    try:
        result = rag_chain.invoke({"input": question})
        context_docs = result.get("context", [])
        parsed = result.get("answer", {}) or {}          # JsonOutputParser 解析出的 JSON
        answer_text = parsed.get("answer", NO_DATA_ANSWER)
    except Exception as e:
        # 生成/解析异常兜底：仍以 JSON 返回，避免链路中断
        print(f"[警告] 回答生成失败：{e}")
        print(json.dumps({"answer": "抱歉，回答生成失败，请重试", "source": []},
                         ensure_ascii=False, indent=2))
        return

    # 两种“无资料”情形，统一返回固定回复且 source 为空，杜绝编造：
    #   1) 完全没有检索到文档（代码层兜底）；
    #   2) 检索到但内容与问题无关，模型按提示词约束回复了固定短语。
    if not context_docs or answer_text == NO_DATA_ANSWER:
        final = {"answer": NO_DATA_ANSWER, "source": []}
    else:
        # 有资料：source 以检索到的真实文档为准，避免模型编造来源
        final = {"answer": answer_text, "source": extract_sources(context_docs)}

    # 最终回答以 JSON 格式输出（answer / source 两个字段）
    print(json.dumps(final, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
