# -*- coding: utf-8 -*-
"""
【离线索引阶段】构建 / 重建企业人事制度知识库索引。

用法：
    python scripts/build_index.py            # 若向量库已有数据则复用，追加新增文档
    python scripts/build_index.py --rebuild  # 强制清空旧索引后重建
"""
import argparse
import sys
from pathlib import Path

# 保证可以从项目根目录 import config / app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from app.pipeline import RAGSystem


def main() -> None:
    parser = argparse.ArgumentParser(description="构建企业人事制度知识库索引")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="强制重建：清空向量库旧索引后重新构建",
    )
    args = parser.parse_args()

    rag = RAGSystem(settings)
    total = rag.build_index(force_rebuild=args.rebuild)
    print(f"\n[完成] 离线索引构建成功，向量库共 {total} 个文档块")


if __name__ == "__main__":
    main()
