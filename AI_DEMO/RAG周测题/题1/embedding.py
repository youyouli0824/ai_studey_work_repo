# -*- coding: utf-8 -*-
"""
Embedding 向量化模块（双模式一键切换）
====================================
由 .env 的 USE_LOCAL_EMBED 决定使用哪种向量化方式：

1. 本地模式（True，默认）：bge-large-zh-v1.5，底层 sentence-transformers，离线可用。
2. 在线模式（False）：DashScope Embedding 接口（OpenAI 兼容格式，用 openai 客户端调用）。

说明：BGE 系列检索 query 时加中文指令前缀可显著提升召回质量（只加在 query 上）。
"""
from typing import List

# bge 中文检索指令（只加在 query 上，不加在文档上）
QUERY_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class LocalBgeEmbedding:
    """本地 BGE 向量化：基于 sentence-transformers。"""

    def __init__(self, model_path: str, device: str = "cpu", low_cpu_mem_usage: bool = True):
        from sentence_transformers import SentenceTransformer

        print(f"[Embedding] 加载本地模型：{model_path}（device={device}）")
        # low_cpu_mem_usage 规避 Windows 虚拟内存不足（1455）问题
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
        return self._model.encode(QUERY_INSTRUCTION + text, normalize_embeddings=True).tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量文档向量化（归一化，余弦相似度友好）。"""
        return self._model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()


class OnlineDashScopeEmbedding:
    """在线 DashScope Embedding：OpenAI 兼容接口。"""

    def __init__(self, api_key: str, base_url: str, model: str, embed_dim: int = 1024):
        from openai import OpenAI

        if not api_key:
            raise ValueError(
                "[Embedding] 在线模式需要配置 DASHSCOPE_API_KEY，请在 .env 中填写"
            )
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self.dim = embed_dim
        print(f"[Embedding] 使用在线 DashScope Embedding：base_url={base_url}，model={model}")

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """批量向量化。DashScope 接口单次最多传 10 条，超出则分批调用。"""
        results: List[List[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            resp = self._client.embeddings.create(model=self._model, input=batch)
            results.extend(item.embedding for item in resp.data)
        return results


def create_embedding(use_local: bool, model_path: str, device: str,
                     api_key: str, base_url: str, api_model: str, dim: int):
    """工厂方法：按配置创建本地或在线 Embedding 实例。"""
    if use_local:
        return LocalBgeEmbedding(model_path, device=device)
    return OnlineDashScopeEmbedding(
        api_key=api_key, base_url=base_url, model=api_model, embed_dim=dim
    )
