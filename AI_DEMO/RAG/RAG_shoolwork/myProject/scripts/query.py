# -*- coding: utf-8 -*-
"""
【检索生成阶段】自然语言问答入口。

用法：
    python scripts/query.py "转正流程是什么？"
    python scripts/query.py                          # 进入交互问答模式
    python scripts/query.py "入职需要提交哪些资料？" --no-rerank   # 关闭重排（对比实验）
    python scripts/query.py "公司年终奖发放规则"     # 知识库外问题，应回复"不知道"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from app.pipeline import RAGSystem


def main() -> None:
    parser = argparse.ArgumentParser(description="企业人事制度知识库问答")
    parser.add_argument("question", nargs="?", help="单条问题；不传则进入交互问答模式")
    parser.add_argument("--no-rerank", action="store_true", help="关闭 Rerank 重排（对比用）")
    args = parser.parse_args()

    rag = RAGSystem(settings)

    if args.question:
        rag.ask(args.question, use_rerank=not args.no_rerank)
        return

    print("进入交互问答模式（输入 exit 退出）")
    while True:
        try:
            q = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "退出"):
            break
        try:
            result = rag.ask(q, use_rerank=not args.no_rerank)
        except Exception as exc:
            print(f"[错误] {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
