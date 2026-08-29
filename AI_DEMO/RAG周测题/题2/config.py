# -*- coding: utf-8 -*-
"""
统一配置管理模块（题2 · 企业制度RAG问答系统）
============================================
所有密钥、路径、模型参数全部从 .env 文件读取，禁止硬编码。

.env 位置约定：
  - 优先加载上一级 RAG周测题/.env（题目指定的密钥存放位置）
  - 若本目录也存在 .env，后加载、可覆盖

所有相对路径统一基于项目根目录（本文件所在目录 = 题2）解析，保证
无论从哪里运行脚本，data/、vector_db/ 等路径都能正确指向。
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录：config.py 位于题2 目录下
BASE_DIR = Path(__file__).resolve().parent

# 加载 .env：上一级目录优先（题目指定位置），本目录兜底可覆盖
load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env")


def _get(name: str, default: str = "") -> str:
    """读取环境变量，未配置时返回默认值。"""
    return os.getenv(name, default)


def _resolve(env_name: str, default: str) -> str:
    """相对路径统一基于项目根目录解析，返回绝对路径字符串。"""
    raw = _get(env_name, default)
    p = Path(raw)
    return str(p if p.is_absolute() else (BASE_DIR / p))


@dataclass
class Settings:
    """全部业务配置。通过 settings = Settings() 单例使用。"""

    # ---------------- 对话模型（DeepSeek，OpenAI 兼容接口） ----------------
    llm_api_key: str = field(default_factory=lambda: _get("API_KEY", ""))
    llm_base_url: str = field(
        default_factory=lambda: _get("BASE_URL", "https://api.deepseek.com/v1")
    )
    llm_model: str = field(default_factory=lambda: _get("LLM_MODEL", "deepseek-chat"))
    llm_temperature: float = field(
        default_factory=lambda: float(_get("LLM_TEMPERATURE", "0"))
    )

    # ---------------- 向量模型（DashScope Embedding） ----------------
    dashscope_api_key: str = field(
        default_factory=lambda: _get("DASHSCOPE_API_KEY", "")
    )
    embed_model: str = field(
        default_factory=lambda: _get("EMBED_API_MODEL", "text-embedding-v3")
    )

    # ---------------- 数据与向量库 ----------------
    pdf_data_path: str = field(
        default_factory=lambda: _resolve("PDF_DATA_PATH", "./data")
    )
    faiss_index_path: str = field(
        default_factory=lambda: _resolve("FAISS_INDEX_PATH", "./vector_db")
    )

    # ---------------- 文本切分参数 ----------------
    chunk_size: int = field(default_factory=lambda: int(_get("CHUNK_SIZE", "500")))
    chunk_overlap: int = field(default_factory=lambda: int(_get("CHUNK_OVERLAP", "50")))

    # ---------------- 检索参数 ----------------
    top_k: int = field(default_factory=lambda: int(_get("RAG_TOP_K", "3")))


# 全局单例，供各模块复用
settings = Settings()
