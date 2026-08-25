import chromadb
from httpx2 import query
from openai import OpenAI
from dotenv import load_dotenv
import os

from transformers import LlamaModel

load_dotenv()
#初始化大模型
llm_client=OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)
#持久化向量库
client=chromadb.PersistentClient(path=r'AI_DEMO\RAG\RAG基础学习\my_study\chromadb')
coll_client=client.get_or_create_collection(name='my_db')

#添加向量
coll_client.add(
    documents=["hi li youyou","hello yu lin","oi you jiang"],
    embeddings=[[1,2,3],[4,5,6],[7,8,9]],
    ids=["1","2","3"]
)
# 语义检索(测试用固定向量，真实场景要替换成Embedding生成的向量)
res=coll_client.query(
    query_embeddings=[1,2,3],
    n_results=2
)
docs_list=res.get("documents")[0]
print(docs_list)
print("======")

query="有没有“you”这个字符串相关的内容？"

prompt=f"""你是一只知识库问答猫娘助手，根据参考内容回答用户的问题。
对话结尾加“喵”。
参考知识库内容：{docs_list}
用户问题：{query}
如果参考内容无相关学习，回答没有资料"""

#正确调用
response=llm_client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role":"user","content":prompt}],
    temperature=0.2
)
print(response.choices[0].message.content)