# -*- coding: utf-8 -*-
"""
下载本地 BGE 模型（Embedding + Rerank）到 models/ 目录。
==========================================================
- BAAI/bge-large-zh-v1.5   本地 Embedding 模型（1024 维）
- BAAI/bge-reranker-base   本地重排模型（Advanced-RAG）

用法：
    python scripts/download_models.py            # 下载全部
    python scripts/download_models.py --embed    # 只下载 Embedding
    python scripts/download_models.py --rerank   # 只下载 Rerank

下载后会直接落到真实权重目录（避免 HuggingFace snapshots/master 软链路径陷阱）。
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from huggingface_hub import snapshot_download


def download(model_id: str, local_dir: Path) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n开始下载 {model_id} -> {local_dir} ...")
    snapshot_download(repo_id=model_id, local_dir=str(local_dir))
    print(f"完成：{model_id} 已保存到 {local_dir}")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="下载本地 BGE 模型")
    parser.add_argument("--embed", action="store_true", help="只下载 Embedding 模型")
    parser.add_argument("--rerank", action="store_true", help="只下载 Rerank 模型")
    args = parser.parse_args()

    tasks = []
    if args.embed or not (args.embed or args.rerank):
        tasks.append(("BAAI/bge-large-zh-v1.5", root / "models" / "BAAI" / "bge-large-zh-v1.5"))
    if args.rerank or not (args.embed or args.rerank):
        tasks.append(("BAAI/bge-reranker-base", root / "models" / "BAAI" / "bge-reranker-base"))

    for model_id, local_dir in tasks:
        download(model_id, local_dir)

    print("\n[完成] 模型下载结束。若下载超时，可配置环境变量 HF_ENDPOINT=https://hf-mirror.com 后重试")


if __name__ == "__main__":
    main()
