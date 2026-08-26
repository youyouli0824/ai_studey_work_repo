# 企业内部知识库 RAG 问答系统

基于 LangChain 的企业内部知识库 RAG 问答原型：员工输入自然语言问题，系统基于企业内部网页文档给出精准回答，并输出参考来源。调用 **DeepSeek `deepseek-v4-flash`** 大模型，嵌入使用本地 `bge-small-zh-v1.5` 中文模型（离线可用）。

## 一、环境搭建

```bash
# 1. 安装依赖（国内推荐清华源）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 配置环境变量
cp .env.example .env        # 然后编辑 .env 填入 DeepSeek API_KEY
```

## 二、运行顺序

```bash
# 1. 构建知识库（生成 faiss_store 向量库）
python build_knowledge.py

# 2. RAG 问答（交互式，输入 quit 退出；以“流程：”开头走少样本流程问答）
python rag_chat.py

# 3. 三类提示词模板演示（摘要 / 翻译 / 流程步骤）
python prompt_demo.py
```

## 三、文件说明

| 文件 | 说明 |
| ---- | ---- |
| `embeddings.py` | 共享模型工厂：LLM（DeepSeek）与嵌入模型（本地/DashScope 可切换） |
| `build_knowledge.py` | 知识库构建：知识源加载（WebBaseLoader 网页 + 本地制度文档）→ 文本分块 → 向量化 → FAISS 入库 |
| `rag_chat.py` | RAG 问答：ChatPromptTemplate + create_stuff_documents_chain + create_retrieval_chain |
| `prompt_demo.py` | PromptTemplate / ChatPromptTemplate / FewShotPromptTemplate 三类模板演示 |
| `data/enterprise_policies.html` | 制造型企业制度汇编（内置知识源，含考勤/请假/差旅报销/加班/奖惩/保密/离职） |
| `faiss_store/` | 运行生成的向量库，不提交 |

> 知识库来源可在 `.env` 的 `KNOWLEDGE_URLS` 配置：默认 = 本地制造企业制度汇编 + 夏津燃气员工手册（真实企业网页）。

> 详细说明见《使用文档.md》（位于项目上级"知识文档、需求文档等"文件夹）。
