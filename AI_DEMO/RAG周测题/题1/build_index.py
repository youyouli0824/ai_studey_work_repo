# -*- coding: utf-8 -*-
"""
知识库构建主流程入口（build_index.py）
=====================================
流程：
1. 从 config 读取全部配置（.env 管理）
2. 读取 data/faq.json 问答对（instruction=用户问题，output=标准答案）
3. 创建 Embedding 实例（本地 BGE / 在线 DashScope 由 USE_LOCAL_EMBED 切换）
4. 批量向量化所有问题
5. 将问题向量与标准答案绑定，写入 Chroma 持久化向量库

用法：
    python build_index.py            # 正常入库（追加）
    python build_index.py --rebuild  # 先清空旧索引再重建
"""
import json
import sys
from typing import List, Tuple

from config import settings
from embedding import create_embedding
from vector_store import ChromaVectorStore


def load_faq(path: str) -> Tuple[List[str], List[str]]:
    """读取 FAQ JSON：每条含 instruction（用户问题）、output（标准答案）。"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    questions = []
    answers = []
    for i, item in enumerate(data, start=1):
        if "instruction" not in item or "output" not in item:
            print(f"[警告] 第 {i} 条缺少 instruction/output 字段，已跳过")
            continue
        questions.append(item["instruction"])
        answers.append(item["output"])
    print(f"[数据] 共读取 {len(questions)} 条 FAQ（文件：{path}）")
    return questions, answers


def main() -> None:
    # 1. 配置
    rebuild = "--rebuild" in sys.argv

    # 2. 数据
    questions, answers = load_faq(settings.faq_data_path)
    if not questions:
        print("[错误] 没有可入库的 FAQ 数据，请检查 FAQ_DATA_PATH 指向的 JSON 文件")
        sys.exit(1)

    # 3. 向量化实例
    embedder = create_embedding(
        use_local=settings.use_local_embed,
        model_path=settings.embed_model_path,
        device=settings.embed_device,
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        api_model=settings.embed_api_model,
        dim=settings.embed_dim,
    )

    # 4. 批量向量化问题
    print("[向量化] 正在向量化全部问题...")
    question_embeddings = embedder.embed_texts(questions)
    print(f"[向量化] 完成，向量维度：{len(question_embeddings[0])}")

    # 5. 入库
    store = ChromaVectorStore(settings.vector_db_path, settings.collection_name)
    if rebuild:
        store.clear()
    store.add_pairs(questions, answers, question_embeddings)

    print(f"[完成] 知识库构建成功，当前共 {store.count()} 条 FAQ")


if __name__ == "__main__":
    main()
