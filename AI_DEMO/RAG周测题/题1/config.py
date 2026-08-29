# -*- coding: utf-8 -*-
"""
统一配置管理模块
================
密钥、路径、模型参数全部从 .env 文件读取，禁止硬编码。

.env 位置约定：
  - 优先加载上一级 RAG周测题/.env（题目指定密钥放在那里）
  - 若本目录也存在 .env，后加载、可覆盖
所有相对路径统一基于项目根目录（本文件所在目录 = 题1）解析。
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录：config.py 位于题1 目录下
BASE_DIR = Path(__file__).resolve().parent

# 加载 .env：上一级目录优先（题目指定的位置），本目录兜底可覆盖
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

    # ---------------- Embedding 双模式开关 ----------------
    # True=本地 BGE 模型（离线）；False=在线 DashScope 接口
    use_local_embed: bool = field(
        default_factory=lambda: _get("USE_LOCAL_EMBED", "True").strip().lower()
        in ("true", "1", "yes")
    )
    # 本地模型路径与参数（USE_LOCAL_EMBED=True 时生效）
    embed_model_path: str = field(
        default_factory=lambda: _resolve("EMBED_MODEL_PATH", "./models/BAAI/bge-large-zh-v1.5")
    )
    embed_device: str = field(default_factory=lambda: _get("EMBED_DEVICE", "cpu"))
    embed_dim: int = field(default_factory=lambda: int(_get("EMBED_DIM", "1024")))

    # ---------------- 在线 DashScope Embedding（USE_LOCAL_EMBED=False 时生效） ----------------
    dashscope_api_key: str = field(default_factory=lambda: _get("DASHSCOPE_API_KEY", ""))
    dashscope_base_url: str = field(
        default_factory=lambda: _get(
            "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    )
    embed_api_model: str = field(default_factory=lambda: _get("EMBED_API_MODEL", "text-embedding-v3"))

    # ---------------- 数据与向量库 ----------------
    faq_data_path: str = field(default_factory=lambda: _resolve("FAQ_DATA_PATH", "./data/faq.json"))
    vector_db_path: str = field(default_factory=lambda: _resolve("VECTOR_DB_PATH", "./vector_db"))
    collection_name: str = field(default_factory=lambda: _get("CHROMA_COLLECTION", "faq_kb"))
    top_k: int = field(default_factory=lambda: int(_get("TOP_K", "2")))


# 全局单例，供各模块复用
settings = Settings()
