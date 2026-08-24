# -*- coding: utf-8 -*-
"""
文档切分模块（FR-02）
====================
【离线索引阶段】采用"滑动窗口递归字符切分"（LlamaIndex SentenceSplitter）将长文档切分为文本块。
- chunk_size / chunk_overlap 通过环境变量配置，代码不写死；
- 递归切分：优先按段落 -> 句子 -> 子句 -> 字符逐级切分，尽量保证语义完整；
- 滑动窗口：相邻块保留 overlap 重叠，避免关键词落在块边界被切断。

同时提供"固定字符切分 / 按标点切分"两种策略，供 report.md 切分效果对比实验使用。
"""
import re
from typing import List, Sequence

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document, TextNode


def split_documents(
    documents: Sequence[Document],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> List[TextNode]:
    """
    主用切分策略：LlamaIndex SentenceSplitter（递归字符切分 + 滑动窗口 overlap）。
    返回带元数据（来源文档）的 TextNode 列表。
    """
    if chunk_overlap >= chunk_size:
        raise ValueError(f"[文档切分] chunk_overlap({chunk_overlap}) 必须小于 chunk_size({chunk_size})")

    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    nodes = splitter.get_nodes_from_documents(list(documents))
    print(
        f"[文档切分] 递归+滑动窗口切分完成：chunk_size={chunk_size}, "
        f"chunk_overlap={chunk_overlap}, 生成文本块 {len(nodes)} 个"
    )
    return nodes


# ---------------------------------------------------------------------------
# 以下为切分策略对比实验用（report.md 第 4 节：滑动窗口切分参数测试对比）
# ---------------------------------------------------------------------------

def split_by_fixed_char(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    """策略 A：固定字符切分——不感知语义，按字符硬切，易切断句子。"""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size")
    step = chunk_size - chunk_overlap
    return [text[i:i + chunk_size] for i in range(0, max(len(text), 1), step)]


def split_by_punctuation(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    """策略 B：按中文标点切分——先切句，再按目标长度聚合，尽量保持句子完整。"""
    sentences = [s.strip() for s in re.split(r"(?<=[。！？；;])", text) if s.strip()]
    chunks: List[str] = []
    current = ""
    for sent in sentences:
        # 若单句就超过 chunk_size，按固定长度回退切分
        while len(sent) > chunk_size:
            if current:
                chunks.append(current)
                current = ""
            sent = sent[:chunk_size]
        if len(current) + len(sent) > chunk_size:
            chunks.append(current)
            # 保留前 overlap 个字符作为滑动窗口重叠
            current = current[-chunk_overlap:] + sent if chunk_overlap else sent
        else:
            current += sent
    if current:
        chunks.append(current)
    return chunks


def summarize_chunks(chunks: List[str]) -> dict:
    """统计切分结果：块数、平均长度、最长/最短、总字符覆盖。"""
    lengths = [len(c) for c in chunks]
    return {
        "块数": len(chunks),
        "平均长度": round(sum(lengths) / len(lengths), 1) if lengths else 0,
        "最长": max(lengths) if lengths else 0,
        "最短": min(lengths) if lengths else 0,
    }
