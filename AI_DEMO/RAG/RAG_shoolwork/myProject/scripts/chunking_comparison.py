# -*- coding: utf-8 -*-
"""
切分策略对比实验脚本（用于 report.md 第 4 节）
==============================================
对比三种切分策略在同一份制度文档上的切分统计：
    A. 固定字符切分
    B. 按中文标点切分
    C. 递归字符 + 滑动窗口切分（LlamaIndex SentenceSplitter，本项目主用）

观察指标：文本块数量 / 平均块长 / 是否存在语义截断，以及 chunk_size / chunk_overlap
参数调整对切分结果的影响。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from app.loader import load_documents
from app.splitter import (
    split_by_fixed_char,
    split_by_punctuation,
    split_documents,
    summarize_chunks,
)


def run_comparison() -> None:
    docs = load_documents(settings.data_dir)
    # 取第一份文档作为实验样本
    sample = docs[0].text
    print(f"\n实验样本：《{docs[0].metadata['source']}》，总字符数 {len(sample)}\n")

    for chunk_size in (256, 512):
        overlap = 50
        print(f"=========== chunk_size={chunk_size}, chunk_overlap={overlap} ===========")
        fixed = split_by_fixed_char(sample, chunk_size, overlap)
        punct = split_by_punctuation(sample, chunk_size, overlap)
        # 递归切分需要包装成 Document
        nodes = split_documents(docs[:1], chunk_size, overlap)
        recursive = [n.text for n in nodes]

        print(f"  固定字符切分      : {summarize_chunks(fixed)}")
        print(f"  按标点切分        : {summarize_chunks(punct)}")
        print(f"  递归+滑动窗口切分 : {summarize_chunks(recursive)}")
        # 直观展示递归切分第一块的末尾 vs 第二块开头（观察语义连续性）
        if recursive:
            print("  递归切分样例：")
            print(f"    块1 开头: {recursive[0][:40]}...")
            print(f"    块1 结尾: ...{recursive[0][-40:]}")
            if len(recursive) > 1:
                print(f"    块2 开头: {recursive[1][:40]}...")
        print()

    # 调整 overlap 观察影响
    print("=========== 调整 chunk_overlap 对固定字符切分的影响（chunk_size=512） ===========")
    for overlap in (0, 50, 128):
        stats = summarize_chunks(split_by_fixed_char(sample, 512, overlap))
        print(f"  overlap={overlap:>3} -> {stats}")


if __name__ == "__main__":
    run_comparison()
