# -*- coding: utf-8 -*-
"""
build_knowledge.py —— 模块1：知识库构建（离线预处理模块）
============================================================
职责：加载企业政策网页 → 语义分块 → 文本向量化 → 保存本地 FAISS 向量库。

完整 RAG 链路的第一步，处理完成后生成 faiss_store 目录，
供 rag_chat.py（模块2）加载做检索问答。

对应知识点（课程学习清单）：
    · WebBaseLoader                  网页文档加载，过滤无关 HTML 标签
    · RecursiveCharacterTextSplitter 递归字符文本分割（chunk_size / chunk_overlap）
    · DashScopeEmbeddings / 本地嵌入  文档片段向量化
    · FAISS                          本地向量数据库，持久化保存
    · LangChain 组件可组合、积木式开发（本模块拆分为独立函数）
"""

import os
import sys

# 在导入 requests/WebBaseLoader 之前设置 UA，避免其提示 USER_AGENT 未设置
os.environ.setdefault("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

import bs4
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embeddings import get_embeddings, resolve_project_path

# 加载 .env 环境变量
load_dotenv()

# 网页正文所在 HTML 容器 class（从 .env 读取，用于过滤导航、广告等无关标签，
# 只提取正文内容；留空则提取整页）。示例页面为正则匹配到的正文容器 class。
CONTENT_SELECTOR = os.getenv("CONTENT_SELECTOR", "p-2 text-justify").strip()


def get_knowledge_urls() -> list:
    """从 .env 读取知识源网页地址列表（英文逗号分隔）。"""
    raw = os.getenv("KNOWLEDGE_URLS", "")
    urls = [u.strip() for u in raw.split(",") if u.strip()]
    if not urls:
        raise ValueError("未在 .env 中配置 KNOWLEDGE_URLS（知识源网页地址）")
    return urls


def _pick_best_text(soup: "bs4.BeautifulSoup") -> str:
    """
    从已解析的 HTML 中选取正文内容最多的容器文本。

    依次尝试 CONTENT_SELECTOR 中的各候选 class，取提取内容最长的一个；
    若全部候选提取内容过少（<200 字），则回退返回整页文本。

    参数:
        soup: 已解析的 BeautifulSoup 对象

    返回:
        提取到的正文文本
    """
    selectors = [s.strip() for s in CONTENT_SELECTOR.split("|") if s.strip()]

    best_text, best_len = "", -1
    for sel in selectors:
        parts = soup.find_all(class_=sel)
        text = "\n".join(p.get_text() for p in parts).strip()
        if len(text) > best_len:
            best_text, best_len = text, len(text)

    # 所有候选均未提取到有效正文时，回退返回整页文本
    if best_len < 200:
        best_text = soup.get_text()
    return best_text


def load_web_documents(urls: list) -> list:
    """
    企业政策文档加载（对应知识点：WebBaseLoader 网页加载 + 过滤无关标签）。

    每个知识源支持两种形式：
        · http(s)://...  真实网页 —— 使用 WebBaseLoader 抓取，配合 BeautifulSoup
                         SoupStrainer 只解析正文容器，过滤导航、广告等无关标签；
        · 本地文件路径    制度文档网页（data/xxx.html）—— 直接读取本地 HTML，
                         使用与网页一致的正文容器过滤逻辑解析。

    参数:
        urls: 知识源地址列表（网页 URL 或本地 HTML 文件路径）

    返回:
        LangChain Document 对象列表
    """
    docs = []
    for url in urls:
        # ---------- 本地 HTML 制度文档 ----------
        if not url.startswith(("http://", "https://")):
            abs_path = resolve_project_path(url)
            print(f"  [加载本地制度网页] {abs_path}")
            with open(abs_path, encoding="utf-8") as f:
                soup = bs4.BeautifulSoup(f.read(), "html.parser")
            page_docs = [
                Document(
                    page_content=_pick_best_text(soup),
                    metadata={"source": abs_path},
                )
            ]
        # ---------- 真实网页 ----------
        else:
            print(f"  [加载网页] {url}")
            selectors = [s.strip() for s in CONTENT_SELECTOR.split("|") if s.strip()]
            page_docs, best_len = None, -1
            # 依次尝试各候选正文容器，取提取内容最完整的一个
            for sel in selectors:
                loader = WebBaseLoader(
                    url, bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=sel))
                )
                cand_docs = loader.load()
                cand_len = sum(len(d.page_content) for d in cand_docs)
                if cand_len > best_len:
                    best_len, page_docs = cand_len, cand_docs
            # 所有候选均未提取到有效正文时，回退加载整页
            if best_len < 200:
                loader = WebBaseLoader(url)
                page_docs = loader.load()
                best_len = sum(len(d.page_content) for d in page_docs)

        docs.extend(page_docs)
        total = sum(len(d.page_content) for d in page_docs)
        print(f"  [完成] 该知识源提取文档 {len(page_docs)} 篇，共 {total} 字")
    return docs


def split_documents(documents: list, chunk_size: int = 300, chunk_overlap: int = 50) -> list:
    """
    文本语义分块（对应知识点：RecursiveCharacterTextSplitter）。

    递归地按分隔符层级将长文档切成语义连贯的小块，
    通过 chunk_overlap 让相邻块保留重叠内容，避免语义断裂。

    参数:
        documents: 待分割的 Document 列表
        chunk_size: 每块最大字符数
        chunk_overlap: 相邻块之间重叠的字符数

    返回:
        分块后的 Document 列表
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def build_faiss_store(chunks: list, save_dir: str, batch_size: int = 10) -> None:
    """
    向量化并持久化保存到本地 FAISS 向量库（对应知识点：向量化 + FAISS）。

    使用嵌入模型把每个文档块转成向量，构建 FAISS 索引。
    为方便大批量文档入库，采用“分批向量化 + 合并索引”的方式
    （第一批创建索引，后续批次 merge_from 合并）。

    参数:
        chunks: 待向量化入库的文档块列表
        save_dir: 向量库保存目录（如 faiss_store）
        batch_size: 每批处理的文档块数量
    """
    embeddings = get_embeddings()
    print(f"  嵌入模型: {type(embeddings).__name__}")

    vector_store = None
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_no = i // batch_size + 1
        print(f"  [向量化入库] 第 {batch_no} 批，文档块数量: {len(batch)}")

        # 第一批：创建新的 FAISS 索引
        if i == 0:
            vector_store = FAISS.from_documents(batch, embeddings)
        # 后续批次：将新批次索引合并进现有索引
        else:
            new_vector = FAISS.from_documents(batch, embeddings)
            vector_store.merge_from(new_vector)

    # 持久化保存到本地 faiss_store 文件夹（含索引文件 + .pkl 文档映射）
    vector_store.save_local(save_dir)
    print(f"  [保存] FAISS 向量库已保存到目录: {save_dir}")


def main() -> None:
    """知识库构建主流程：网页加载 → 分块 → 向量化入库。"""
    print("=" * 60)
    print("开始构建知识库（离线预处理）")
    print("=" * 60)

    try:
        # 步骤1：读取知识源网页地址
        urls = get_knowledge_urls()
        print(f"[步骤1/3] 加载 {len(urls)} 个知识源网页...")
        docs = load_web_documents(urls)
        if not docs:
            print("警告: 网页未提取到正文内容，请检查 KNOWLEDGE_URLS 与 CONTENT_ID 是否匹配")
            return

        # 步骤2：文本语义分块
        print(f"[步骤2/3] 文本分块，共 {len(docs)} 篇文档...")
        chunks = split_documents(docs)
        print(f"  分块完成，共 {len(chunks)} 个文档块")

        # 步骤3：向量化并保存 FAISS 向量库
        print("[步骤3/3] 文档向量化并保存到 FAISS 向量库...")
        save_dir = resolve_project_path(os.getenv("FAISS_DIR", "faiss_store"))
        build_faiss_store(chunks, save_dir)

        print("=" * 60)
        print(f"知识库构建成功！向量库目录: {save_dir}")
        print("接下来运行 rag_chat.py 即可进行检索问答")
        print("=" * 60)

    except Exception as e:
        # 统一捕获异常，给出友好提示，避免脚本直接崩溃
        print(f"\n[构建失败] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
