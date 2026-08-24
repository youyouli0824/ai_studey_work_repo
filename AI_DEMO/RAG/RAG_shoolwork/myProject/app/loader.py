# -*- coding: utf-8 -*-
"""
文档加载模块（FR-01）
====================
【离线索引阶段】读取本地 docx 格式企业人事制度文档，返回 LlamaIndex Document 列表。

支持：
- 扫描指定目录下全部 .docx（递归）；
- 按文档原始顺序解析段落与表格，保留来源文件名等元数据；
- 单个文件解析失败不中断整体加载，给出明确错误提示。
"""
from pathlib import Path
from typing import List, Optional

from docx import Document as DocxDocument
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from llama_index.core.schema import Document as LlamaDocument


def _iter_block_items(doc: DocxDocument):
    """按 Word 文档 body 顺序迭代"段落 / 表格"，保证提取文本顺序与原文一致。"""
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def _docx_to_text(docx_path: Path) -> str:
    """解析单个 docx：段落直接取文本，表格按行用 | 拼接。"""
    doc = DocxDocument(str(docx_path))
    lines: List[str] = []
    for block in _iter_block_items(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if text:
                lines.append(text)
        elif isinstance(block, Table):
            for row in block.rows:
                cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                lines.append(" | ".join(cells))
    return "\n".join(lines)


def _build_document(docx_path: Path) -> Optional[LlamaDocument]:
    """将单个 docx 文件包装为 LlamaIndex Document（带来源元数据）。"""
    text = _docx_to_text(docx_path)
    if not text.strip():
        print(f"[文档加载] 警告：{docx_path.name} 内容为空，已跳过")
        return None
    return LlamaDocument(
        text=text,
        metadata={"source": docx_path.name, "path": str(docx_path)},
    )


def load_documents(data_dir: str) -> List[LlamaDocument]:
    """扫描目录下全部 .docx 制度文档并加载。"""
    data_path = Path(data_dir)
    if not data_path.exists() or not data_path.is_dir():
        raise FileNotFoundError(f"[文档加载] 数据目录不存在：{data_path}")

    docx_files = sorted(data_path.rglob("*.docx"))
    if not docx_files:
        raise FileNotFoundError(f"[文档加载] 数据目录下未找到任何 .docx 文档：{data_path}")

    documents: List[LlamaDocument] = []
    for f in docx_files:
        try:
            doc = _build_document(f)
            if doc is not None:
                documents.append(doc)
                print(f"[文档加载] 成功：{f.name}（{len(doc.text)} 字符）")
        except Exception as exc:  # 单文件失败不中断整体
            print(f"[文档加载] 失败：{f.name} -> {type(exc).__name__}: {exc}")

    if not documents:
        raise RuntimeError("[文档加载] 没有任何文档被成功加载，请检查 data 目录")
    print(f"[文档加载] 共加载文档 {len(documents)} 份")
    return documents


def load_documents_from_paths(docx_paths: List[str]) -> List[LlamaDocument]:
    """加载指定路径的 docx（供增量更新模块使用）。"""
    documents: List[LlamaDocument] = []
    for raw in docx_paths:
        p = Path(raw)
        if not p.exists():
            print(f"[文档加载] 跳过（路径不存在）：{raw}")
            continue
        try:
            doc = _build_document(p)
            if doc is not None:
                documents.append(doc)
                print(f"[文档加载] 成功：{p.name}（{len(doc.text)} 字符）")
        except Exception as exc:
            print(f"[文档加载] 失败：{p.name} -> {type(exc).__name__}: {exc}")
    return documents
