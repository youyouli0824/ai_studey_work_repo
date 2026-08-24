# -*- coding: utf-8 -*-
"""
Embedding 向量化模块（FR-03）
============================
将文本块 / 查询转为向量，支持两种模式一键切换（USE_LOCAL_EMBED 环境变量）：

1. 本地模式（默认，True）：bge-large-zh-v1.5，底层 sentence-transformers，离线可运行。
   输出向量维度 1024，归一化后便于余弦相似度计算。
2. 在线模式（False）：OpenAI 兼容 Embedding API（默认阿里云 dashscope text-embedding-v3），
   同时兼容 DeepSeek 等 OpenAI 兼容服务（改 EMBED_API_BASE / EMBED_API_MODEL 即可）。

说明：bge 系列检索时为 query 添加中文指令前缀，可显著提升召回质量。
"""
from typing import List

# bge 中文查询指令（只加在 query 上，不加在文档上）
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class LocalBgeEmbedding:
    """本地 BGE 向量化：基于 sentence-transformers 封装。"""

    def __init__(
        self,
        model_path: str,
        device: str = "cpu",
        low_cpu_mem_usage: bool = True,
    ):
        from sentence_transformers import SentenceTransformer

        print(f"[Embedding] 加载本地模型：{model_path}（device={device}）")
        # low_cpu_mem_usage 透传给 transformers，规避 Windows 虚拟内存不足（1455）问题
        self._model = SentenceTransformer(
            model_name_or_path=model_path,
            device=device,
            trust_remote_code=True,
            model_kwargs={"low_cpu_mem_usage": low_cpu_mem_usage},
        )
        # 兼容新旧版 sentence-transformers 的维度方法名
        get_dim = getattr(self._model, "get_embedding_dimension", None) or self._model.get_sentence_embedding_dimension
        self.dim = get_dim()
        print(f"[Embedding] 本地模型加载完成，向量维度：{self.dim}")

    def embed_query(self, text: str) -> List[float]:
        """query 向量化（bge 检索指令前缀 + 归一化）。"""
        return self._model.encode(
            QUERY_INSTRUCTION + text, normalize_embeddings=True
        ).tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量文本块向量化（归一化，余弦相似度友好）。"""
        return self._model.encode(
            texts, normalize_embeddings=True, batch_size=32
        ).tolist()


class OnlineEmbedding:
    """在线 Embedding：OpenAI 兼容接口（默认阿里云 dashscope）。"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        embed_dim: int = 1024,
    ):
        from openai import OpenAI

        if not api_key:
            raise ValueError(
                "[Embedding] 在线模式需要配置 EMBED_API_KEY（或 DASHSCOPE_API_KEY），"
                "请在 .env 中填写"
            )
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self.dim = embed_dim
        print(f"[Embedding] 使用在线 Embedding：base_url={base_url}, model={model}")

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        resp = self._client.embeddings.create(model=self._model, input=texts)
        return [item.embedding for item in resp.data]


def create_embedding(
    use_local: bool,
    embed_model_path: str,
    embed_device: str,
    embed_api_base: str,
    embed_api_key: str,
    embed_api_model: str,
    embed_dim: int = 1024,
):
    """工厂方法：按配置创建本地或在线 Embedding 实例。"""
    if use_local:
        return LocalBgeEmbedding(embed_model_path, device=embed_device)
    return OnlineEmbedding(
        api_key=embed_api_key,
        base_url=embed_api_base,
        model=embed_api_model,
        embed_dim=embed_dim,
    )
