# -*- coding: utf-8 -*-
"""
app 包：企业人事制度知识库 RAG 问答系统核心模块。

模块划分（对应课程知识点）：
- loader.py        文档加载模块（FR-01）
- splitter.py      文档切分模块（FR-02）
- embedding.py     Embedding 向量化模块（FR-03，本地/在线切换）
- vector_store.py  向量库存储模块（FR-04，Chroma 持久化）
- retriever.py     检索模块（FR-05，余弦 top-k）
- reranker.py      重排模块（FR-06，bge-reranker，Advanced-RAG）
- generator.py     回答生成模块（FR-07，DeepSeek + Prompt 幻觉约束）
- pipeline.py      RAG 全流程编排（Naive / Advanced RAG）
"""
