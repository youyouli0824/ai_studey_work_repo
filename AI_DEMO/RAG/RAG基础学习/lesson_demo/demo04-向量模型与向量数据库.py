import chromadb
from base_llm import client
import json

# 向量数据库连接器
# 负责与向量数据库交互，包括创建集合、添加文档、查询文档等
class MyVectorDBConnector:
    def __init__(self,collection_name):
        # 持久化向量数据库，数据保存到./chromadb文件夹
        db_client = chromadb.PersistentClient(path='./chromadb')
        # 创建/获取集合（集合=向量数据表）
        self.collection = db_client.get_or_create_collection(
            name=collection_name,
            #metadata={"hnsw:space": "cosine"} # 余弦相似度开关，默认欧式距离
        )

    # 文本批量转向量（调用云端在线模型）
    def get_embeddings(self,texts):
        data = client.embeddings.create(input=texts,model='text-embedding-v4').data
        # 将data中的每个元素的embedding字段提取出来，组成一个新的列表返回
        return [x.embedding for x in data]

    # 批量入库：问题向量化，答案作为文档存储
    def add_documents(self,questions,answers):
        # 问题向量化
        emb = self.get_embeddings(questions)
        # 将问题向量写入向量数据库
        self.collection.add(
            documents=answers,
            embeddings=emb,
            # 为每个文档生成一个唯一的ID
            # 格式：id0,id1,id2...
            ids=[f'id{i}' for i in range(len(answers))]
        )

    # 用户提问语义检索
    def search(self,query):
        result = self.collection.query(
            # 将向量化结果作为查询参数
            query_embeddings=self.get_embeddings([query]),
            # 返回2条最相似的问答
            n_results=2
        )
        return result

if __name__ == '__main__':
    # 读取行式JSON问答数据集
    with open('train_zh.json',encoding='utf-8') as f:
        # 读取文件中的每一行，将每一行解析为JSON对象，组成一个新的列表返回
        data = [json.loads(line) for line in f]
        #print(data)

    # 提取data中的前10条问题
    instructions = [entry['instruction'] for entry in data[0:10]]
    # 提取data中的前10条答案
    outputs = [entry['output'] for entry in data[0:10]]
    # 初始化向量数据库连接
    # collection_name：向量数据库名qa_demo
    vector_db = MyVectorDBConnector("qa_demo")
    # 批量写入问答向量
    vector_db.add_documents(instructions,outputs)
    # 模拟用户提问检索
    query = "得了白癜风怎么办"
    # 检索2条最相似的问答
    results = vector_db.search(query)
    print(results)