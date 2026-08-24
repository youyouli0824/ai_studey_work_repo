# -*- coding: utf-8 -*-
"""
统一配置管理模块
================
从 .env 环境变量读取全部业务参数，禁止在代码中硬编码密钥与模型绝对路径。
所有相对路径统一基于项目根目录（本文件所在目录）解析，方便移植。
"""
from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv

# --------------------------------------------------------------------------
# 项目根目录：config.py 位于项目根目录下
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# 加载项目根目录下的 .env 文件（若存在则生效）
load_dotenv(BASE_DIR / ".env")

# 默认 System Prompt：严格约束大模型，抑制幻觉
# 核心要求：知识库没有的信息必须回复"不知道"，禁止编造
_DEFAULT_SYSTEM_PROMPT = (
    "你是企业人事制度知识库问答助手，负责依据公司内部制度文档回答员工问题。\n"
    "\n"
    "请严格遵守以下规则：\n"
    "1. 只能依据下面【检索到的制度文档片段】中的内容作答，禁止编造、猜测或补充文档中没有的制度条款；\n"
    "2. 如果文档片段中没有与问题相关的信息，请直接回复\"不知道\"，不要给出任何推测性答案；\n"
    "3. 回答要尽量准确、简洁，直接引用制度原文的要点；\n"
    "4. 如文档中涉及多条相关条款，请分点列明，并标注依据的文档名称。"
)


def _get(name: str, default: str = "") -> str:
    """读取环境变量，未配置时返回默认值。"""
    return os.getenv(name, default)


def _resolve(env_name: str, default: str) -> str:
    """
    解析路径类环境变量：相对路径统一基于项目根目录，返回绝对路径字符串。
    """
    raw = _get(env_name, default)
    p = Path(raw)
    return str(p if p.is_absolute() else (BASE_DIR / p))


@dataclass
class Settings:
    """全部业务配置。可通过 settings = Settings() 单例使用。"""

    # ---------------- LLM 配置（DeepSeek） ----------------
    deepseek_api_key: str = field(default_factory=lambda: _get("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(
        default_factory=lambda: _get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    )
    deepseek_model: str = field(default_factory=lambda: _get("DEEPSEEK_MODEL", "deepseek-chat"))
    deepseek_temperature: float = field(
        default_factory=lambda: float(_get("DEEPSEEK_TEMPERATURE", "0"))
    )

    # ---------------- Embedding 配置（本地 / 在线一键切换） ----------------
    use_local_embed: bool = field(
        default_factory=lambda: _get("USE_LOCAL_EMBED", "True").strip().lower()
        in ("true", "1", "yes")
    )
    embed_model_path: str = field(
        default_factory=lambda: _resolve("EMBED_MODEL_PATH", "./models/BAAI/bge-large-zh-v1.5")
    )
    embed_device: str = field(default_factory=lambda: _get("EMBED_DEVICE", "cpu"))
    embed_dim: int = field(default_factory=lambda: int(_get("EMBED_DIM", "1024")))
    # 在线 Embedding（OpenAI 兼容格式，USE_LOCAL_EMBED=False 时生效）
    embed_api_base: str = field(
        default_factory=lambda: _get(
            "EMBED_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    )
    embed_api_key: str = field(
        default_factory=lambda: _get("EMBED_API_KEY", _get("DASHSCOPE_API_KEY", ""))
    )
    embed_api_model: str = field(
        default_factory=lambda: _get("EMBED_API_MODEL", "text-embedding-v3")
    )

    # ---------------- Rerank 重排配置（Advanced-RAG，可选） ----------------
    use_rerank: bool = field(
        default_factory=lambda: _get("USE_RERANK", "True").strip().lower()
        in ("true", "1", "yes")
    )
    rerank_model_path: str = field(
        default_factory=lambda: _resolve("RERANK_MODEL_PATH", "./models/BAAI/bge-reranker-base")
    )
    rerank_device: str = field(default_factory=lambda: _get("RERANK_DEVICE", "cpu"))
    rerank_top_n: int = field(default_factory=lambda: int(_get("RERANK_TOP_N", "3")))

    # ---------------- RAG 业务参数（参数解耦，全部从环境变量读取） ----------------
    chunk_size: int = field(default_factory=lambda: int(_get("CHUNK_SIZE", "512")))
    chunk_overlap: int = field(default_factory=lambda: int(_get("CHUNK_OVERLAP", "50")))
    sim_top_k: int = field(default_factory=lambda: int(_get("SIM_TOP_K", "6")))

    # ---------------- 数据与索引路径 ----------------
    data_dir: str = field(default_factory=lambda: _resolve("DATA_DIR", "./data"))
    vector_db_path: str = field(
        default_factory=lambda: _resolve("VECTOR_DB_PATH", "./vector_db")
    )
    collection_name: str = field(default_factory=lambda: _get("CHROMA_COLLECTION", "hr_policy_kb"))

    # ---------------- Prompt ----------------
    system_prompt: str = field(default_factory=lambda: _get("SYSTEM_PROMPT", _DEFAULT_SYSTEM_PROMPT))


# 全局单例，供各模块复用
settings = Settings()
