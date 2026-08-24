# -*- coding: utf-8 -*-
"""
重排模块（FR-06，Advanced-RAG）
==============================
【检索生成阶段】对向量检索返回的 top-k 片段，用本地 bge-reranker-base 重排序，
过滤低相关性片段，保留 RERANK_TOP_N 个高质量上下文送入大模型。

⚠️ 注意 HuggingFace 的 snapshots/master 软链路径陷阱：
   形如 ".../snapshots/master" 的路径通常是软链接目录，若目标缺失会导致加载失败，
   本模块会尝试向上定位真实权重目录。
"""
from pathlib import Path
from typing import List, Tuple

from app.vector_store import SearchHit


def _has_weights(d: Path) -> bool:
    """判断目录是否为真实模型权重目录（含 config + 权重文件）。"""
    if not (d / "config.json").exists():
        return False
    return any((d / f).exists() for f in ("model.safetensors", "pytorch_model.bin"))


def resolve_model_path(model_path: str) -> str:
    """解决 snapshots/master 软链路径陷阱，返回真实权重目录。"""
    p = Path(model_path)
    if _has_weights(p):
        return str(p)
    # 路径中包含 snapshots 段：遍历其子目录找真实快照（真实目录名是 commit hash）
    snap_dir = next((a for a in p.parents if a.name == "snapshots"), None)
    if snap_dir is not None and snap_dir.is_dir():
        for child in snap_dir.iterdir():
            if child.is_dir() and _has_weights(child):
                return str(child)
    # 回退：检查上一级目录
    if _has_weights(p.parent):
        return str(p.parent)
    # 找不到真实目录时原样返回，让 CrossEncoder 尝试按模型名加载
    return str(p)


class Reranker:
    """本地 bge-reranker-base 交叉编码器重排。"""

    def __init__(self, model_path: str, device: str = "cpu"):
        from sentence_transformers import CrossEncoder

        resolved = resolve_model_path(model_path)
        print(f"[重排] 加载本地重排模型：{resolved}（device={device}）")
        self._model = CrossEncoder(
            model_name_or_path=resolved,
            device=device,
            model_kwargs={"low_cpu_mem_usage": True},  # 规避 Windows 虚拟内存不足
        )
        print("[重排] 重排模型加载完成")

    def rerank(
        self,
        query: str,
        hits: List[SearchHit],
        top_n: int,
    ) -> List[Tuple[SearchHit, float]]:
        """
        对检索片段重新打分排序，返回重排后保留的 top_n 片段（附重排分）。
        分数越高代表与 query 相关度越高（bge-reranker 输出 relevance logits）。
        """
        pairs = [(query, hit.text) for hit in hits]
        scores = self._model.predict(pairs).tolist()
        ranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]
