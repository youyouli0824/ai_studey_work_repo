import chromadb

#chroma_client = chromadb.Client()

# 持久化客户端
client=chromadb.PersistentClient('./chroma_db')
# 在数据库中创建一个集合：可以理解成是MySQL中的表
# 如果集合不存在，会自动创建；如果已存在，会返回已存在的集合
collection = client.get_or_create_collection(name='my_collection')

# 将向量存入集合中
collection.add(documents=["Article by john", "Article by Jack", "Article by Jill"],
    embeddings=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    ids=["1", "2", "3"])

# select * from my_collection where documents like '%john%'
results2 = collection.get(include=['embeddings'],where_document={'$contains':'john'})
print(results2)

# 修改向量:在更新向量时，要求必须指定要更新的向量的id；更改的是向量
# collection.update(documents=["Article by john", "Article by Jack", "Article by Jill"],
#     embeddings=[[10, 20, 30], [4, 5, 6], [7, 8, 9]],
#     ids=["1", "2", "3"])

# 把id为1的向量删除掉
#collection.delete(ids=["1"])

# 全量查询-
results = collection.get(include=['embeddings'])
print(results)

# 查询向量，返回距离最近的2个向量
res=collection.query(query_embeddings=[4, 5, 6],n_results=2)
print(res.get('documents')[0])






