# -*- coding: utf-8 -*-
"""
Chroma 向量数据库操作类
======================
封装 Chroma 持久化向量库的全部操作：

- 入库：add_pairs —— 把问题向量与标准答案绑定后写入集合（问题向量化、答案作为文档存储）
- 检索：search —— 输入 query 向量，返回 TopK 最相似的标准答案（余弦相似度）
- 管理：count / clear / 持久化到 VECTOR_DB_PATH 目录

关键点：
- 集合使用余弦度量（hnsw:space=cosine），Chroma 余弦距离 = 1 - 余弦相似度，
  因此底层检索就是余弦相似度检索；
- PersistentClient 自动持久化到磁盘，下次启动无需重建索引。
"""
from dataclasses import dataclass
from typing import Dict, List

import chromadb


@dataclass
class SearchHit:
    """一次检索命中的 FAQ 条目。"""

    question: str   # 命中条目的用户问题
    answer: str     # 对应标准答案
    score: float    # 余弦相似度（0~1，越大越相似）
    doc_id: str     # 向量库中的 id


class ChromaVectorStore:
    """Chroma 向量库封装：FAQ 问题向量 + 答案绑定入库与余弦检索。"""

    def __init__(self, persist_dir: str, collection_name: str = "faq_kb"):
        self._client = chromadb.PersistentClient(path=persist_dir)
        # 余弦度量：Chroma cosine 距离 = 1 - 余弦相似度
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        print(
            f"[向量库] 集合：{collection_name}，已有 FAQ 条数：{self._collection.count()}，"
            f"持久化目录：{persist_dir}"
        )

    # ------------------------------------------------------------------
    # 入库
    # ------------------------------------------------------------------
    def add_pairs(self, questions: List[str], answers: List[str],
                  embeddings: List[List[float]]) -> int:
        """
        批量入库 FAQ 问答对。
        - 问题向量 embeddings 是检索用的向量
        - 答案 answers 作为文档内容存储，问题 questions 写入元数据（绑定关系）
        """
        ids = [f"faq_{i}" for i in range(self._collection.count(),
                                          self._collection.count() + len(questions))]
        self._collection.add(
            ids=ids,
            documents=answers,                                # 标准答案
            metadatas=[{"question": q} for q in questions],   # 绑定对应问题
            embeddings=embeddings,                            # 问题向量
        )
        total = self._collection.count()
        print(f"[向量库] 本次入库 {len(questions)} 条，当前 FAQ 总数：{total}")
        return total

    def clear(self) -> None:
        """清空集合（切换向量化方式后重建索引时使用）。"""
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name, metadata={"hnsw:space": "cosine"}
        )
        print("[向量库] 已清空旧索引，准备重建")

    def count(self) -> int:
        return self._collection.count()

    # ------------------------------------------------------------------
    # 语义检索
    # ------------------------------------------------------------------
    def search(self, query_embedding: List[float], top_k: int = 2) -> List[SearchHit]:
        """基于余弦相似度检索 TopK 条标准答案。"""
        if self._collection.count() == 0:
            raise RuntimeError("[检索] 向量库为空，请先运行 build_index.py 构建知识库")

        res = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: List[SearchHit] = []
        for doc_id, answer, meta, dist in zip(
            res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            cos_sim = round(1.0 - dist, 6)  # 余弦距离 -> 余弦相似度
            hits.append(
                SearchHit(
                    question=self._extract_question(meta),
                    answer=answer,
                    score=cos_sim,
                    doc_id=doc_id,
                )
            )
        return hits

    @staticmethod
    def _extract_question(meta: Dict[str, str]) -> str:
        """从元数据中取出绑定的用户问题。"""
        return meta.get("question", "未知问题") if meta else "未知问题"
