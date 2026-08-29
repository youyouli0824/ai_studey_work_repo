# -*- coding: utf-8 -*-
"""
语义检索主流程入口（query.py）
==============================
流程：
1. 创建 Embedding 实例（与构建时保持同一模式）
2. 打开 Chroma 向量库
3. 用户输入自然语言问题（命令行参数或交互输入）
4. 问题向量化，余弦检索 TopK 条最相似标准答案

用法：
    python query.py "信用卡还款日是哪天"   # 命令行传入问题
    python query.py                        # 交互式输入问题
"""
import sys

from config import settings
from embedding import create_embedding
from vector_store import ChromaVectorStore


def get_question() -> str:
    """获取用户问题：优先命令行参数，否则交互输入。"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    return input("请输入您的问题：").strip()


def main() -> None:
    question = get_question()
    if not question:
        print("[错误] 问题不能为空")
        sys.exit(1)

    # 1. 向量化实例（与构建知识库时保持同一模式）
    embedder = create_embedding(
        use_local=settings.use_local_embed,
        model_path=settings.embed_model_path,
        device=settings.embed_device,
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        api_model=settings.embed_api_model,
        dim=settings.embed_dim,
    )

    # 2. 打开向量库
    store = ChromaVectorStore(settings.vector_db_path, settings.collection_name)

    # 3. 问题向量化
    query_vector = embedder.embed_query(question)

    # 4. 语义检索 TopK
    print(f"\n您的问题：{question}")
    print("=" * 60)
    hits = store.search(query_vector, top_k=settings.top_k)
    print(f"Top{len(hits)} 最相似的标准答案（相似度从高到低）：\n")
    for idx, hit in enumerate(hits, start=1):
        print(f"--- 第 {idx} 条  相似度：{hit.score:.4f} ---")
        print(f"命中标准问题：{hit.question}")
        print(f"标准答案：{hit.answer}")
        print()


if __name__ == "__main__":
    main()
