# -*- coding: utf-8 -*-
"""
检索模块（FR-05）
================
【检索生成阶段】对用户 query 向量化，在向量库中基于余弦相似度检索 top-K 相关文档片段。

链路：query 自然语言 -> query 向量化（同一 Embedding 模型）-> 余弦 top-k 检索。
"""
from typing import List

from app.vector_store import SearchHit, VectorStore


def retrieve(
    embedding,
    vector_store: VectorStore,
    query: str,
    top_k: int,
) -> List[SearchHit]:
    """执行检索，返回按余弦相似度降序排列的 top-k 片段。"""
    # 1) Query 向量化（与索引阶段使用同一 Embedding 模型，保证向量空间一致）
    query_vector = embedding.embed_query(query)
    # 2) 向量库底层余弦相似度 top-k 检索
    hits = vector_store.search(query_vector, top_k=top_k)
    print(f"[检索] query 向量维度：{len(query_vector)}，召回 top-{top_k} 片段")
    return hits
