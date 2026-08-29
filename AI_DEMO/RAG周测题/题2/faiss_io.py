# -*- coding: utf-8 -*-
"""
FAISS 本地持久化辅助模块
========================
Windows 上 faiss 的 C++ 底层（fopen）无法打开含中文/非 ASCII 字符的绝对路径，
会报 "Illegal byte sequence" 错误。本项目路径（RAG周测题\\题2）含中文，
因此统一采用「先 chdir 到索引目录、再用相对路径读写」的方式绕过该限制：

  - 传给 faiss 的路径字符串只含 ASCII（如 index.faiss），不触发编码问题；
  - 中文只出现在进程的当前工作目录里，由操作系统解析，不经过 faiss 的字符串转换。
"""
import os
from pathlib import Path
from typing import Any


def save_local(vectorstore, folder_path: str) -> None:
    """把 FAISS 向量库持久化到 folder_path（兼容含中文的路径）。"""
    folder = Path(folder_path)
    folder.mkdir(parents=True, exist_ok=True)
    old_cwd = os.getcwd()
    os.chdir(folder)  # 进入索引目录，使 faiss 只接触 ASCII 相对路径
    try:
        vectorstore.save_local(".")
    finally:
        os.chdir(old_cwd)


def load_local(folder_path: str, embeddings) -> Any:
    """从 folder_path 加载 FAISS 向量库（兼容含中文的路径）。"""
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"向量库不存在：{folder_path}")

    old_cwd = os.getcwd()
    os.chdir(folder)  # 进入索引目录，使 faiss 只接触 ASCII 相对路径
    try:
        from langchain_community.vectorstores import FAISS

        return FAISS.load_local(
            ".",
            embeddings,
            allow_dangerous_deserialization=True,
        )
    finally:
        os.chdir(old_cwd)
