# pip install chromadb openai python-dotenv
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载密钥配置
load_dotenv()

# 初始化大模型客户端（替换成你正在使用的厂商，这里以通义百炼为例）
llm_client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# 内存向量库
#client = chromadb.Client()
# 持久化向量库
client = chromadb.PersistentClient(path='./chroma_db')
# 集合(Collection)可以理解成向量数据库里的「数据表」。
# 不同的业务知识库建议分开创建不同的集合，例如医疗知识库、法律知识库可以各自独立collection。
# 如果客户端中已经存在名为 `my_db` 的集合 → 直接获取现有集合；
# 如果不存在 `my_db` → 自动新建一个名称为 `my_db` 的集合；
coll_client = client.get_or_create_collection(name='my_db')

# 添加向量
coll_client.add(
    documents=["Article by john", "Article by Jack", "Article by Jill"],
    embeddings=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    ids=["1", "2", "3"]
)

# 语义检索(测试用固定向量，真实场景要替换成Embedding生成的向量)
print("===================")
res = coll_client.query(
    query_embeddings=[4,5,6],
    n_results=2
)
docs_list = res.get("documents")[0]
print(docs_list)

# 拼接提示词，扁平化检索结果
#query = "什么是感知机"
query="有没有Jack相关的内容？"

prompt = f"""你是知识库问答助手，仅根据参考内容回答用户问题。
参考知识库内容：{docs_list}
用户问题：{query}
如果参考内容无相关信息，直接回答暂无相关资料。"""

# 正确调用：使用实例chat.completions.create，不存在llm.invoke方法
response = llm_client.chat.completions.create(
    model="qwen3.7-max", # 换成对话模型：qwen3.7-max
    messages=[{"role":"user", "content": prompt}],
    temperature=0
)
print(response.choices[0].message.content)