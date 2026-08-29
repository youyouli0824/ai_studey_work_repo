# FAQ 语义匹配 RAG 系统（题1）

基于 Chroma 向量数据库的轻量级 FAQ 语义检索系统。金融客服沉淀的标准问答对（`instruction` 问题 / `output` 答案）先向量化入库，用户提问时语义匹配 Top2 最相似标准答案，解决传统关键词检索无法应对同义改写的问题。

## 目录结构

```
题1/
├── config.py           # 统一配置（从 .env 读取，禁止硬编码）
├── embedding.py        # 双模式向量化：本地 BGE / 在线 DashScope
├── vector_store.py     # Chroma 向量库操作类（入库 / 检索 / 管理）
├── build_index.py      # 【主流程·建库】读取 FAQ JSON → 向量化 → 入库
├── query.py            # 【主流程·检索】输入问题 → Top2 标准答案
├── data/faq.json       # 示例 FAQ 问答对（40条，可替换为真实1000条）
├── vector_db/          # Chroma 持久化目录（自动生成）
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖
python -m pip install -r requirements.txt

# 2. 构建知识库（默认本地 BGE 模型，离线）
python build_index.py

# 3. 语义检索（命令行传问题，或交互输入）
python query.py "信用卡免息还款期是多久？"
python query.py   # 然后交互输入问题
```

## 双模式向量化切换

所有配置都在 `AI_DEMO/RAG周测题/.env` 中管理：

| 配置项 | 含义 |
| --- | --- |
| `USE_LOCAL_EMBED=True` | 本地 BGE 模型（离线可用，推荐默认） |
| `USE_LOCAL_EMBED=False` | 在线 DashScope Embedding 接口 |
| `EMBED_MODEL_PATH` | 本地 BGE 模型路径 |
| `EMBED_DEVICE` / `EMBED_DIM` | 本地模型设备 / 向量维度 |
| `EMBED_API_MODEL` | 在线 Embedding 模型名（默认 text-embedding-v3） |
| `DASHSCOPE_API_KEY` / `DASHSCOPE_BASE_URL` | 在线接口密钥与地址 |
| `FAQ_DATA_PATH` / `VECTOR_DB_PATH` | 数据文件 / 向量库路径 |
| `CHROMA_COLLECTION` / `TOP_K` | 集合名 / 返回条数 |

**切换模式后需重建索引**（不同模型向量维度/空间不同）：

```bash
python build_index.py --rebuild
```

## 核心原理

- **余弦检索**：Chroma 集合使用 `hnsw:space=cosine`，检索距离 = 1 - 余弦相似度，即底层就是语义相似度排序。
- **问题向量 + 答案绑定**：只对问题做向量化入库，答案作为文档存储、问题写入元数据，检索命中的就是绑定答案。
- **BGE 检索指令**：本地模式对 query 加中文检索前缀「为这个句子生成表示以用于检索相关文章：」，显著提升召回质量。
