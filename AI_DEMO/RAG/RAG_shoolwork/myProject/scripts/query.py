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
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 静默模型加载时的 tqdm 进度条（Loading weights: ...）
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

from config import settings
from app.pipeline import RAGSystem


def ask_quiet(rag: RAGSystem, question: str, use_rerank: bool) -> str:
    """执行问答，只返回 DeepSeek 的回答，屏蔽模型加载/检索等全部日志输出。"""
    with redirect_stdout(StringIO()):
        result = rag.ask(question, use_rerank=use_rerank, verbose=False)
    return result.answer


def main() -> None:
    parser = argparse.ArgumentParser(description="企业人事制度知识库问答")
    parser.add_argument("question", nargs="?", help="单条问题；不传则进入交互问答模式")
    parser.add_argument("--no-rerank", action="store_true", help="关闭 Rerank 重排（对比用）")
    args = parser.parse_args()

    rag = RAGSystem(settings)

    if args.question:
        print("ai回答：" + ask_quiet(rag, args.question, not args.no_rerank))
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
            print("ai回答：" + ask_quiet(rag, q, not args.no_rerank))
        except Exception as exc:
            print(f"[错误] {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
