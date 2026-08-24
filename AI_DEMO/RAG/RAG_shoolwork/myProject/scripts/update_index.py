# -*- coding: utf-8 -*-
"""
增量更新知识库（进阶功能 FR-08）
================================
新增制度文档时，无需重建全部索引，直接把新文档向量化后追加进已有向量库。

用法：
    python scripts/update_index.py data/新制度文档.docx
    python scripts/update_index.py data/新制度文档1.docx data/新制度文档2.docx
    python scripts/update_index.py --dir data/新增目录        # 扫描目录下全部 docx
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from app.pipeline import RAGSystem


def main() -> None:
    parser = argparse.ArgumentParser(description="增量更新知识库索引")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("paths", nargs="*", help="新增的 docx 文件路径")
    group.add_argument("--dir", help="扫描目录下全部 .docx")
    args = parser.parse_args()

    if args.dir:
        d = Path(args.dir)
        if not d.exists():
            print(f"[错误] 目录不存在：{d}")
            sys.exit(1)
        paths = [str(p) for p in sorted(d.glob("*.docx"))]
    else:
        paths = args.paths

    if not paths:
        print("[提示] 未指定任何新增文档")
        sys.exit(0)

    rag = RAGSystem(settings)
    total = rag.add_documents(paths)
    print(f"\n[完成] 增量更新成功，向量库现有文档块总数：{total}")


if __name__ == "__main__":
    main()
