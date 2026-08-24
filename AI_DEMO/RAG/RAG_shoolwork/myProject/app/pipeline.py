# -*- coding: utf-8 -*-
"""
RAG 全流程编排模块（Naive RAG / Advanced RAG）
=============================================
统一封装两大阶段：

【离线索引阶段】文档加载 -> 文档切分 -> Embedding 向量化 -> 向量库入库
【检索生成阶段】Query 向量化 -> 余弦 top-k 检索 -> (Rerank 重排) -> Prompt 组装 -> LLM 生成

支持：
- 持久化加载已有索引（Chroma 持久化，无需每次重建）；
- --rebuild 强制重建；add_documents 增量更新（FR-08，无需全量重建）。
"""
from dataclasses import dataclass, field
from typing import List, Optional

from config import Settings, settings as default_settings

from app.loader import load_documents, load_documents_from_paths
from app.splitter import split_documents
from app.embedding import create_embedding
from app.vector_store import SearchHit, VectorStore
from app.retriever import retrieve
from app.generator import Generator


@dataclass
class AnswerResult:
    """问答结果：大模型回答 + 召回/重排片段 + 分数。"""

    question: str
    answer: str
    hits: List[SearchHit] = field(default_factory=list)
    rerank_scores: List[float] = field(default_factory=list)


class RAGSystem:
    """RAG 问答系统（懒加载各重量级组件，按需初始化）。"""

    def __init__(self, settings: Settings = None):
        self.settings = settings or default_settings
        self._embedding = None
        self._vector_store = None
        self._reranker = None
        self._generator = None

    # ------------------------------------------------------------------
    # 懒加载组件
    # ------------------------------------------------------------------
    def embedding(self):
        if self._embedding is None:
            s = self.settings
            self._embedding = create_embedding(
                use_local=s.use_local_embed,
                embed_model_path=s.embed_model_path,
                embed_device=s.embed_device,
                embed_api_base=s.embed_api_base,
                embed_api_key=s.embed_api_key,
                embed_api_model=s.embed_api_model,
                embed_dim=s.embed_dim,
            )
        return self._embedding

    def vector_store(self) -> VectorStore:
        if self._vector_store is None:
            s = self.settings
            self._vector_store = VectorStore(
                persist_dir=s.vector_db_path,
                collection_name=s.collection_name,
            )
        return self._vector_store

    def reranker(self):
        if self._reranker is None:
            from app.reranker import Reranker

            s = self.settings
            self._reranker = Reranker(s.rerank_model_path, s.rerank_device)
        return self._reranker

    def generator(self) -> Generator:
        if self._generator is None:
            s = self.settings
            self._generator = Generator(
                api_key=s.deepseek_api_key,
                base_url=s.deepseek_base_url,
                model=s.deepseek_model,
                temperature=s.deepseek_temperature,
                system_prompt=s.system_prompt,
            )
        return self._generator

    # ------------------------------------------------------------------
    # 【离线索引阶段】
    # ------------------------------------------------------------------
    def build_index(self, force_rebuild: bool = False) -> int:
        """
        构建知识库索引：加载文档 -> 切分 -> 向量化 -> 入库。
        返回向量库文档块总数。
        """
        vs = self.vector_store()
        if force_rebuild:
            vs.clear()

        # 1) 文档加载
        documents = load_documents(self.settings.data_dir)

        # 2) 文档切分（滑动窗口递归切分，参数来自环境变量）
        nodes = split_documents(
            documents,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        # 3) 向量化（打印向量维度，观察 bge-large-zh-v1.5 输出 1024 维）
        emb = self.embedding()
        vectors = emb.embed_texts([n.text for n in nodes])
        for node, vec in zip(nodes, vectors):
            node.embedding = vec
        dim = len(vectors[0]) if vectors else 0
        print(f"[向量化] 共向量化 {len(vectors)} 个文本块，向量维度：{dim}")

        # 4) 向量入库（Chroma 持久化）
        vs.add_nodes(nodes)
        return vs.count()

    def add_documents(self, docx_paths: List[str]) -> int:
        """
        增量更新知识库（FR-08）：新增 docx 无需重建全部索引。
        """
        vs = self.vector_store()
        documents = load_documents_from_paths(docx_paths)
        if not documents:
            print("[增量更新] 没有可入库的新文档")
            return vs.count()

        nodes = split_documents(
            documents,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        emb = self.embedding()
        vectors = emb.embed_texts([n.text for n in nodes])
        for node, vec in zip(nodes, vectors):
            node.embedding = vec
        print(f"[向量化] 新增向量化 {len(vectors)} 个文本块，向量维度：{len(vectors[0]) if vectors else 0}")
        vs.add_nodes(nodes)
        return vs.count()

    # ------------------------------------------------------------------
    # 【检索生成阶段】
    # ------------------------------------------------------------------
    def ask(
        self,
        question: str,
        use_rerank: bool = True,
        verbose: bool = True,
    ) -> AnswerResult:
        """
        回答一个自然语言问题。
        链路：Query 向量化 -> 余弦 top-k 检索 -> [Rerank 重排] -> Prompt 组装 -> DeepSeek 生成。
        """
        s = self.settings
        emb = self.embedding()
        vs = self.vector_store()

        # 1) Query 向量化 + 余弦 top-k 检索
        hits = retrieve(emb, vs, question, top_k=s.sim_top_k)
        if verbose:
            print("\n[检索] 召回的 top-{} 片段：".format(s.sim_top_k))
            for i, h in enumerate(hits, 1):
                print(f"  #{i} 来源:{h.source} 余弦相似度={h.score:.4f} | {h.text[:60]}")

        # 2) Rerank 重排（Advanced-RAG，可开关做对比实验）
        rerank_scores: List[float] = []
        if use_rerank and s.use_rerank and hits:
            rer = self.reranker()
            ranked = rer.rerank(question, hits, s.rerank_top_n)
            hits = [h for h, _ in ranked]
            rerank_scores = [score for _, score in ranked]
            if verbose:
                print(f"\n[重排] bge-reranker 重排后保留 top-{s.rerank_top_n} 片段：")
                for i, h in enumerate(hits, 1):
                    print(f"  #{i} 来源:{h.source} 重排分={rerank_scores[i - 1]:.4f} | {h.text[:60]}")
        else:
            if verbose:
                print("\n[重排] 未开启（Naive-RAG 模式）")

        # 3) Prompt 组装 + 调用 DeepSeek 生成回答
        gen = self.generator()
        answer = gen.generate(question, [h.text for h in hits])
        if verbose:
            print("\n[生成] DeepSeek 回答：\n" + "-" * 50 + "\n" + answer + "\n" + "-" * 50)

        return AnswerResult(
            question=question,
            answer=answer,
            hits=hits,
            rerank_scores=rerank_scores,
        )
