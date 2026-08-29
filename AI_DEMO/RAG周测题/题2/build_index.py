# -*- coding: utf-8 -*-
"""
知识库构建主流程入口（build_index.py）—— 独立入口一
===================================================
把 data/ 目录下的全部 PDF 制度文档入库，构建并持久化 FAISS 向量库。

流程：
1. 从 config 读取全部配置（.env 管理）
2. PyPDFLoader 逐份加载 PDF 制度文档                     （文档加载）
3. RecursiveCharacterTextSplitter 递归语义分块          （文本切分）
4. DashScopeEmbeddings 向量化                           （嵌入）
5. FAISS.from_documents 建库 + save_local 本地持久化     （向量库存储）

用法：
    python build_index.py
"""
import sys
import warnings
from pathlib import Path

# 屏蔽 langchain-community 迁移期的噪音警告，保证运行截图干净
warnings.filterwarnings("ignore", message=r"`langchain-community` is being sunset.*")

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings
from faiss_io import save_local


def load_all_pdfs(data_dir: str) -> list:
    """文档加载：PyPDFLoader 加载 data 目录下全部 PDF，返回 Document 列表。"""
    pdf_files = sorted(Path(data_dir).glob("*.pdf"))
    if not pdf_files:
        print(f"[错误] {data_dir} 目录下没有 PDF 文档，请先放入制度文档")
        sys.exit(1)

    documents = []
    for pdf in pdf_files:
        loader = PyPDFLoader(str(pdf))
        docs = loader.load()  # 每页一个 Document，元数据自带 source=文件名
        print(f"[加载] {pdf.name}：{len(docs)} 页")
        documents.extend(docs)
    print(f"[加载] 共加载 {len(documents)} 页文档")
    return documents


def main() -> None:
    # 1. 配置
    print(f"[配置] 文档目录：{settings.pdf_data_path}")
    print(f"[配置] 向量库目录：{settings.faiss_index_path}")

    # 2. 文档加载
    documents = load_all_pdfs(settings.pdf_data_path)

    # 3. 文本切分：递归语义分块（chunk_size / chunk_overlap 来自 .env）
    #    额外补充中文标点分隔符，让分块更贴合中文句子/段落边界
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(
        f"[切分] 共生成 {len(chunks)} 个文本块"
        f"（chunk_size={settings.chunk_size}，chunk_overlap={settings.chunk_overlap}）"
    )

    # 4. 向量化：DashScope Embedding
    if not settings.dashscope_api_key:
        print("[错误] 未配置 DASHSCOPE_API_KEY，请在 .env 中填写")
        sys.exit(1)
    embeddings = DashScopeEmbeddings(
        dashscope_api_key=settings.dashscope_api_key,
        model=settings.embed_model,
    )
    print(f"[向量化] 使用 DashScope Embedding：{settings.embed_model}")

    # 5. 建库 + 本地持久化
    vectorstore = FAISS.from_documents(chunks, embeddings)  # 向量化 + FAISS 建库
    save_local(vectorstore, settings.faiss_index_path)      # 持久化到本地磁盘（faiss_io 兼容中文路径）
    print(f"[完成] 知识库构建成功，共 {len(chunks)} 个文本块已入库")
    print(f"[完成] FAISS 索引已保存到：{settings.faiss_index_path}")


if __name__ == "__main__":
    main()
