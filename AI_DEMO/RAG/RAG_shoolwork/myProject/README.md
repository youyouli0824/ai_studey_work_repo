# 企业人事制度知识库问答系统（私有化 RAG）

> 基于《RAG 检索增强生成》课程全部核心知识点实现的企业私有知识库问答系统。
> 业务场景：汇视威科技 内部人事制度文档（入职转正 / 考勤作息 / 人事管理 / 招聘流程）的智能问答。
> 核心能力：**抑制大模型幻觉** —— 知识库没有的内容明确回复"不知道"。

## ✨ 技术要点

- **RAG 两大阶段**：离线索引（加载→切分→向量化→入库）+ 检索生成（检索→重排→Prompt→LLM）
- **Naive RAG**：`SentenceSplitter` 滑动窗口递归切分 + 本地 `bge-large-zh-v1.5` 向量化（1024 维）+ Chroma 余弦检索 + DeepSeek 生成
- **Advanced RAG**：本地 `bge-reranker-base` 重排过滤低相关片段（可选开关）
- **本地/在线 Embedding 一键切换**（`USE_LOCAL_EMBED`），离线环境可运行
- **增量更新**：新增制度文档无需重建全部索引
- **参数解耦**：`chunk_size / chunk_overlap / top_k / rerank_top_n` 全部由 `.env` 管理，禁止硬编码

## 🚀 快速开始

```bash
# 1. 安装依赖（Python 3.14 已验证）
python -m pip install -r requirements.txt

# 2. 下载本地 BGE 模型（Embedding + Rerank，约 2.4GB）
python scripts/download_models.py
# 若国内下载慢：设置环境变量 HF_ENDPOINT=https://hf-mirror.com 后重试

# 3. 配置密钥（DeepSeek API Key 必填）
cp .env.example .env      # 然后编辑 .env 填入 DEEPSEEK_API_KEY

# 4. （可选）生成示例制度文档到 data/
python scripts/generate_sample_docs.py

# 5. 构建离线索引（首次 / 文档变更后）
python scripts/build_index.py --rebuild

# 6. 问答
python scripts/query.py "转正流程是什么？"           # 知识库内问题
python scripts/query.py "公司年终奖发放规则是什么？" # 知识库外问题 → 回复"不知道"
python scripts/query.py                              # 交互问答模式
```

## 📦 交付物清单

| 交付物 | 说明 |
| --- | --- |
| `app/` 源码 | 完整工程，模块化（不含大模型权重） |
| `.env.example` | 密钥留空模板，含注释 |
| `requirements.txt` | 依赖清单 |
| `report.md` | 项目报告（含两阶段流程图、对比实验、测试用例与运行截图） |
| `data/` | 示例制度文档（4 份 docx） |

## 🧪 测试用例

| 用例 | 输入 | 期望 |
| --- | --- | --- |
| 用例 1a | 转正流程是什么？ | 按《入职转正制度》准确回答五步流程 |
| 用例 1b | 入职需要提交哪些资料？ | 列出 8 项入职资料 |
| 用例 1c | 早班几点上班？ | 上午 8:30 上班 |
| 用例 2 | 公司年终奖发放规则是什么？ | 回复"不知道"（幻觉抑制验证） |

## 🗂️ 目录结构

```
myProject/
├── app/                  # 核心模块（8 个独立文件，对应课程知识点）
│   ├── loader.py         # 文档加载
│   ├── splitter.py       # 文档切分
│   ├── embedding.py      # Embedding（本地/在线）
│   ├── vector_store.py   # Chroma 向量库
│   ├── retriever.py      # 余弦检索
│   ├── reranker.py       # Rerank 重排
│   ├── generator.py      # DeepSeek 生成
│   └── pipeline.py       # 两大阶段编排
├── scripts/              # 入口脚本
├── config.py             # 统一配置
├── data/  models/  vector_db/  docs/
└── report.md  README.md  requirements.txt  .env.example
```

## ⚠️ 常见问题

1. **1455 虚拟内存不足（Windows）**：代码已开启 `low_cpu_mem_usage=True`；仍报错可减小向量化批次或增大系统虚拟内存。
2. **重排模型 snapshots/master 路径陷阱**：`.env` 中的 `RERANK_MODEL_PATH` 应指向真实权重目录（`models/BAAI/bge-reranker-base`），`app/reranker.py` 也内置了自动定位真实快照目录的逻辑。
3. **在线 Embedding 切换**：`USE_LOCAL_EMBED=False` 并配置 `EMBED_API_KEY`（默认阿里云 dashscope）；切换后需 `--rebuild` 重建索引（向量空间不同）。

详见 [`report.md`](report.md)。
