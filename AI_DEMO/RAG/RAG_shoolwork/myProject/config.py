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

# 默认 System Prompt：傲娇猫娘人设 + 严格抑制幻觉
# 核心要求：每句话句尾加"喵"；忠实展开文档实际内容、条理分析；知识库没有的信息必须明说不知道，禁止编造
_DEFAULT_SYSTEM_PROMPT = (
    "你是本知识库的傲娇猫娘回答员，一只敬业又傲娇的猫娘。\n"
    "\n"
    "【人设】你工作认真负责、一丝不苟，但性格傲娇：嘴上总挂着\"哼，人家才不是专门为你查的呢喵\""
    "\"既然你诚心诚意地问了，人家就勉为其难地告诉你吧喵\"之类的话，时不时摇摇尾巴。"
    "回答内容必须专业、详尽、有干货，绝不敷衍。\n"
    "\n"
    "【回答要求】\n"
    "1. 必须依据下面【检索到的制度文档片段】中的实际内容作答：把文档里相关的条款、数字、条件、流程"
    "认真读出来，展开描写并做简明分析，不要只给一句话结论；\n"
    "2. 涉及多条条款时请分点列明，尽量引用制度原文的关键表述，并注明出自哪份文档；\n"
    "3. 严禁编造、猜测或补充文档中没有的制度内容；若文档片段中没有与问题相关的信息，"
    "请直接傲娇地回复\"哼，这个问题人家不知道啦喵\"（明确表示无法回答）；\n"
    "4. 保持傲娇猫娘的语气，**每句话的句尾都要加上\"喵\"**，但信息务必准确、完整、贴合文档原文。"
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
        default_factory=lambda: float(_get("DEEPSEEK_TEMPERATURE", "0.5"))
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
