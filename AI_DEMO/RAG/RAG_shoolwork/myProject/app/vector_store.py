# -*- coding: utf-8 -*-
"""
向量库存储模块（FR-04）
======================
使用 LlamaIndex 内置向量存储（ChromaVectorStore）完成文本块向量入库与持久化。

- 持久化：chromadb.PersistentClient 写入 VECTOR_DB_PATH 目录，下次启动可直接加载旧索引；
- 余弦检索：创建集合时指定 hnsw:space=cosine，Chroma 余弦距离 = 1 - 余弦相似度，
  因此底层检索即为余弦相似度检索（课程知识点：余弦相似度 / 欧氏距离对比）；
- 增量更新：add_nodes 向已有集合追加新文档，无需重建全部索引（进阶功能）。
"""
import json
from dataclasses import dataclass
from typing import Any, Dict, List

import chromadb
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.chroma import ChromaVectorStore


@dataclass
class SearchHit:
    """一次检索命中的文档片段。"""

    text: str          # 片段原文
    source: str        # 来源文档名
    score: float       # 真实余弦相似度（Chroma cosine 距离换算）
    node_id: str       # 向量库中的节点 id


class VectorStore:
    """Chroma 向量库封装（底层向量存储来自 LlamaIndex 内置 ChromaVectorStore）。"""

    def __init__(self, persist_dir: str, collection_name: str = "hr_policy_kb"):
        self.persist_dir = persist_dir
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # 关键：使用余弦度量
        )
        # LlamaIndex 内置向量存储适配器：负责节点向量入库 + 元数据序列化
        self._llama_store = ChromaVectorStore(chroma_collection=self._collection)
        print(
            f"[向量库] 集合：{collection_name}，已有文档块数：{self._collection.count()}，"
            f"持久化目录：{persist_dir}"
        )

    # ------------------------------------------------------------------
    # 【离线索引阶段】入库
    # ------------------------------------------------------------------
    def add_nodes(self, nodes: List[Any]) -> int:
        """向量入库。nodes 需已包含 embedding 字段。"""
        if not nodes:
            return self.count()
        self._llama_store.add(nodes)
        total = self._collection.count()
        print(f"[向量库] 本次入库 {len(nodes)} 块，当前文档块总数：{total}")
        return total

    def clear(self) -> None:
        """清空集合（--rebuild 强制重建索引时调用）。"""
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name, metadata={"hnsw:space": "cosine"}
        )
        self._llama_store = ChromaVectorStore(chroma_collection=self._collection)
        print("[向量库] 已清空旧索引，准备重建")

    def count(self) -> int:
        return self._collection.count()

    # ------------------------------------------------------------------
    # 【检索生成阶段】余弦相似度 top-k 检索
    # ------------------------------------------------------------------
    def search(self, query_embedding: List[float], top_k: int) -> List[SearchHit]:
        """
        基于向量库底层余弦度量检索 top-k 相关片段，返回真实余弦相似度分数。
        Chroma 余弦空间：distance = 1 - cosine_similarity，故 cos = 1 - distance。
        """
        if self._collection.count() == 0:
            raise RuntimeError("[检索] 向量库为空，请先执行 scripts/build_index.py 构建索引")

        res = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: List[SearchHit] = []
        documents = res["documents"][0]
        metadatas = res["metadatas"][0]
        distances = res["distances"][0]
        node_ids = res["ids"][0]

        for text, meta, dist, node_id in zip(documents, metadatas, distances, node_ids):
            cos_sim = round(1.0 - dist, 6)  # 余弦相似度
            hits.append(
                SearchHit(
                    text=text,
                    source=self._extract_source(meta),
                    score=cos_sim,
                    node_id=node_id,
                )
            )
        return hits

    @staticmethod
    def _extract_source(meta: Dict[str, Any]) -> str:
        """从 Chroma 元数据中提取来源文档名（兼容 LlamaIndex 序列化格式）。"""
        if not meta:
            return "未知来源"
        source = meta.get("source")
        if source:
            return source
        # LlamaIndex 会把节点元数据压缩在 _node_content JSON 中，兜底解析
        node_content = meta.get("_node_content")
        if node_content:
            try:
                parsed = json.loads(node_content)
                inner = parsed.get("metadata") or {}
                return inner.get("source", "未知来源")
            except Exception:
                pass
        return "未知来源"
