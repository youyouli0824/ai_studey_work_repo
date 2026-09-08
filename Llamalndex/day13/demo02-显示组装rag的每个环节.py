from langchain_community.embeddings import DashScopeEmbeddings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, get_response_synthesizer
from llama_index.core.prompts import PromptTemplate
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers.type import ResponseMode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.deepseek import DeepSeek
from llama_index.core import Settings
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_BASE_URL")
model = "deepseek-v4-pro"

# 设置默认的LLM
Settings.llm = DeepSeek(model=model,api_key=api_key,api_base=api_base_url,temperature=0.1)
Settings.embed_model=DashScopeEmbeddings(dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
                                    model="text-embedding-v4")

# 加载文档
document=SimpleDirectoryReader(input_files=["./人事管理流程.docx"]).load_data()

# 设置切分参数
splitter=SentenceSplitter(chunk_size=512,chunk_overlap=50)
# 将文档切分成节点
nodes=splitter.get_nodes_from_documents(document)

# 向量化并入库
index=VectorStoreIndex(nodes)

# 设置检索时的召回数量
retriever=index.as_retriever(similarity_top_k=5)
#retriever.query("公司什么时间下班？")

# 文本问答模板
text_qa_template= PromptTemplate(
    "背景信息如下：\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "请结合背景回答：{query_str}\n"
    "注意：如果背景没提到，请直说不知道。"
)

# 响应合成器
response_synthesizer=get_response_synthesizer(
    # 压缩模式
    response_mode=ResponseMode.COMPACT,
    # 文本问答模板
    text_qa_template=text_qa_template
)

# 对检索到的结果进行排序
reranker=SentenceTransformerRerank(model=os.getenv("RERANK_MODEL_PATH"),top_n=5)

# 创建查询引擎
query_engine=RetrieverQueryEngine.from_args(
    retriever=retriever,
    # 响应合成器
    response_synthesizer=response_synthesizer,
    # 响应后处理
    node_postprocessors=[reranker]
)

print(query_engine.query("公司的转正流程是怎样的？"))


