# -*- coding: utf-8 -*-
"""
embeddings.py —— 共享模型工厂模块（LangChain 积木式组件）
============================================================
本模块统一封装项目中用到的两个核心模型组件，各功能模块直接复用，
体现 LangChain “组件可组合、积木式开发” 的核心思想：

    1. get_llm()          —— 对话大模型组件
       · 通过 langchain_openai.ChatOpenAI 调用 DeepSeek 大模型（deepseek-v4-flash）
       · 密钥、base_url、模型名全部从 .env 读取，禁止硬编码
       · 对应知识点：大模型调用 ChatOpenAI

    2. get_embeddings()   —— 文本嵌入模型组件
       · local    方案：使用本地 bge 中文嵌入模型（离线可用，无需额外密钥）
       · dashscope方案：使用阿里云 DashScope 的 text-embedding-v4（需 DASHSCOPE_API_KEY）
       · 通过 EMBED_PROVIDER 环境变量切换，对应知识点：Embedding 嵌入模型
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载 .env 环境变量（密钥、模型名、url 统一放 .env，符合工程规范）
load_dotenv()

# 项目根目录：以本文件所在目录为准，保证从任意目录运行脚本都能定位到模型/向量库
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def resolve_project_path(path: str) -> str:
    """
    把相对路径解析为基于项目根目录的绝对路径。

    用户可能不在项目目录下运行脚本（如：python D:/xxx/work/build_knowledge.py），
    相对路径会相对当前工作目录解析而导致找不到模型/向量库，这里统一锚定到项目根目录。

    参数:
        path: 相对或绝对路径

    返回:
        绝对路径
    """
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)


def get_llm(temperature: float = 0):
    """
    创建对话大模型组件（DeepSeek）。

    参数:
        temperature: 生成温度，0 表示尽量确定、减少随机，适合制度问答。

    返回:
        ChatOpenAI 实例（OpenAI 兼容接口调用 DeepSeek）
    """
    # 从环境变量读取 DeepSeek 凭证与模型名（禁止硬编码密钥）
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_name = os.getenv("LLM_MODEL", "deepseek-v4-flash")

    # 密钥缺失时给出友好提示，避免裸奔报错
    if not api_key:
        raise ValueError("未配置 API_KEY，请先在 .env 文件中填入 DeepSeek API 密钥")

    # langchain-openai 的 ChatOpenAI 是 OpenAI 兼容接口，
    # 市面上兼容 OpenAI 协议的大模型（DeepSeek/通义/DeepSeek 等）可无缝切换
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model_name=model_name,
        temperature=temperature,
    )


def get_embeddings():
    """
    创建文本嵌入模型组件（文档/问题向量化）。

    根据 .env 中 EMBED_PROVIDER 决定使用哪种嵌入方案：
        local     —— 本地 bge-small-zh-v1.5 中文嵌入模型（离线可用，默认）
        dashscope —— 阿里云 DashScope text-embedding-v4（需配置 DASHSCOPE_API_KEY）

    返回:
        LangChain Embeddings 实例
    """
    provider = os.getenv("EMBED_PROVIDER", "local").lower()

    # ---------- 方案一：本地 bge 中文嵌入模型（推荐，离线可用） ----------
    if provider == "local":
        # 优先从 langchain-huggingface 导入（官方新包），否则回退到 langchain-community
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            from langchain_community.embeddings import HuggingFaceEmbeddings

        model_path = os.getenv("LOCAL_EMBED_MODEL", "models/bge-small-zh-v1.5")
        # 解析为基于项目根目录的绝对路径，避免从其他目录运行时找不到本地模型
        model_path = resolve_project_path(model_path)
        return HuggingFaceEmbeddings(
            model_name=model_path,          # 支持加载本地模型目录（离线加载，无需联网）
            encode_kwargs={"normalize_embeddings": True},  # 归一化，便于余弦相似度检索
        )

    # ---------- 方案二：阿里云 DashScope 嵌入（知识文档课程方案） ----------
    elif provider == "dashscope":
        from langchain_community.embeddings import DashScopeEmbeddings

        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        if not dashscope_key:
            raise ValueError(
                "EMBED_PROVIDER=dashscope 但未配置 DASHSCOPE_API_KEY，"
                "请到 .env 中配置，或将 EMBED_PROVIDER 改回 local"
            )
        # 对应知识点：DashScopeEmbeddings 文档向量化
        return DashScopeEmbeddings(
            dashscope_api_key=dashscope_key,
            model=os.getenv("EMBED_MODEL", "text-embedding-v4"),
        )

    # ---------- 非法配置兜底 ----------
    raise ValueError(f"EMBED_PROVIDER 配置非法: {provider}，可选值 local / dashscope")


# ---------- 本模块自测入口：python embeddings.py ----------
if __name__ == "__main__":
    # 验证 LLM 组件
    llm = get_llm()
    print("LLM 组件创建成功 ->", type(llm).__name__)

    # 验证嵌入组件
    emb = get_embeddings()
    vec = emb.embed_query("测试一句话")
    print("嵌入组件创建成功 ->", type(emb).__name__)
    print("向量维度:", len(vec))
