# 题2 · LangChain 企业制度 RAG 问答系统

基于 LangChain 的完整 RAG 链路，让员工用自然语言查询企业内部 PDF 制度文档。
严格基于文档内容回答，抑制大模型幻觉。

## 技术栈

| 环节 | 组件 |
|------|------|
| 文档加载 | `PyPDFLoader`（本地 data/ 目录下 PDF 制度文档） |
| 文本切分 | `RecursiveCharacterTextSplitter`（chunk_size / chunk_overlap） |
| 向量化 | `DashScopeEmbeddings`（DashScope text-embedding-v3） |
| 向量存储 | `FAISS`（本地持久化，save_local / load_local） |
| 提示词 | `ChatPromptTemplate` |
| 输出解析 | `JsonOutputParser`（JSON：answer / source 两字段） |
| 检索生成 | `create_stuff_documents_chain` + `create_retrieval_chain` |
| 对话模型 | DeepSeek（OpenAI 兼容接口，`ChatOpenAI` 调用） |

## 目录结构

```
题2/
├── config.py            # 配置管理（全部从 .env 读取，禁止硬编码）
├── build_index.py       # 独立入口一：知识库构建（PDF → 分块 → 向量库）
├── query.py             # 独立入口二：问答调用（检索 → 生成 → JSON）
├── faiss_io.py          # FAISS 本地持久化辅助（兼容 Windows 中文路径）
├── data/                # 存放 PDF 制度文档
│   ├── 财务管理文档.pdf
│   └── 员工考勤管理制度.pdf
├── vector_db/           # FAISS 向量库持久化目录（运行时生成）
├── requirements.txt
└── README.md
```

> 说明：faiss_io.py 处理 Windows 上 faiss 无法读写含中文绝对路径的问题
> （本项目路径 `RAG周测题\题2` 含中文），通过 chdir + 相对路径读写绕过。

## 使用步骤

### 0. 环境准备

密钥配置在上一级 `RAG周测题/.env`（题目指定位置），无需改动即可运行；
如需修改模型、切分参数等，在 .env 的「题2」配置段调整。

```bash
python -m pip install -r requirements.txt
```

### 1. 构建知识库（入口一）

```bash
python build_index.py
```

自动加载 `data/` 下全部 PDF → 递归切分 → DashScope 向量化 → FAISS 建库并持久化到 `vector_db/`。
（后续新增制度文档后，重新运行一次即可重建索引。）

### 2. 问答调用（入口二）

```bash
python query.py "财务报销的流程是什么"      # 命令行传入问题
python query.py                            # 交互式输入问题
```

回答以 JSON 格式输出：

```json
{
  "answer": "员工提交报销单 → 部门负责人初审 → 会计核对票据 → 对应财务层级终审 → 出纳打款。",
  "source": ["财务管理文档.pdf"]
}
```

- `answer`：严格基于文档的回答；检索不到相关制度时统一返回「知识库中暂无相关制度信息」；
- `source`：回答依据的真实来源文档名（取自检索到的文档元数据，不会编造）。

## 评测演示建议

1. 运行 `python build_index.py` 截图 —— 展示「加载 → 切分 → 向量化 → 建库持久化」全流程；
2. 运行 `python query.py "财务报销的流程是什么"` 截图 —— 展示命中文档的 JSON 回答；
3. 运行 `python query.py "今天上海天气如何"` 截图 —— 展示无关问题触发固定兜底回复「知识库中暂无相关制度信息」。
