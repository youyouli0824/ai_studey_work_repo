# ParentDocument父子索引检索实现方案，属于RAG索引构建阶段分层分块优化（MultiVector多向量检索实现路线之一）
import json
import os
import warnings
import uuid

from langchain_core.documents import Document

# 屏蔽废弃包警告，消除控制台冗余提示
warnings.filterwarnings("ignore", category=DeprecationWarning)
# 配置网页爬虫UA，解决网页加载阻塞、超时问题
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome 120.0.0.0"
from base_llm import llm, embeddings_model
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.stores import InMemoryByteStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
import pymysql

# 封装一个自定义的MySQL操作类
class MySQLDocStore():
    def __init__(self, host, port, user, password, database):
        # 建立与数据库的连接
        self.conn = pymysql.connect(host=host,
                                    port=port,
                                    user=user,
                                    password=password,
                                    database=database,
                                    cursorclass=pymysql.cursors.DictCursor)
        self._create_table()

    # 定义一个私有的建表方法
    def _create_table(self):
        sql = """
               CREATE TABLE IF NOT EXISTS parent_docs (
                   parent_id VARCHAR(255) PRIMARY KEY,
                   page_content TEXT,
                   meta_info JSON
               )
        """
        with self.conn.cursor() as cursor:
             cursor.execute(sql)
             # 提交事务
             self.conn.commit()

    # 定义一个插入数据的方法
    def batch_save(self,id_doc_paris):
        sql = """
            INSERT INTO parent_docs (parent_id, page_content, meta_info)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE page_content=%s, meta_info=%s
        """
        with self.conn.cursor() as cursor:
            for parent_id,doc in id_doc_paris:
                # 将信息转为json格式
                meta_str = json.dumps(doc.metadata, ensure_ascii=False)
                cursor.execute(sql,(parent_id,doc.page_content,meta_str,doc.page_content,meta_str))
                # 提交事务
                self.conn.commit()

    # 批量查询
    def batch_get(self, id_list):
        if not id_list:
            return []
        # "%s,%s,%s,..."
        placeholders = ",".join(["%s"] * len(id_list))
        # select * from parent_docs where parent_id in (%s,%s,%s,...)
        sql = f"SELECT parent_id, page_content, meta_info FROM parent_docs WHERE parent_id IN ({placeholders})"
        with self.conn.cursor() as cur:
            cur.execute(sql, id_list)
            # 得到查询结果
            # rows: [(parent_id, page_content, meta_info), ...]
            rows = cur.fetchall()
        res_docs = []
        for row in rows:
            # 将json字符串格式化JSON对象
            meta = json.loads(row["meta_info"])
            res_docs.append(Document(page_content=row["page_content"], metadata=meta))
        return res_docs

# 1. 文档加载
url = "https://news.pku.edu.cn/xwzh/687160cb45fc4bb891d8ff384c42d56d.htm"
loader = WebBaseLoader(url)
#["page_content":"网页正文"]
raw_doc=loader.load()

# 2.对原始文本进行清洗
doc = []
for d in raw_doc:
    # " hello world "
    content = d.page_content.strip().replace("\n", "").replace("\r", "")
    # 过滤内容长度不足80的导航/空白文本(网页菜单、页脚、版权、跳转链接等)
    if len(content) > 80:
        d.page_content = d.page_content.strip()
        # [Document(page_id="1", page_content="hello world")]
        doc.append(d)
print("【进度1】网页正文加载+清洗完成，过滤导航空白文本")

# 3. 文本分段
# 3.1 创建一个父文档切分对象
parent_splitter=RecursiveCharacterTextSplitter(chunk_size=800,
                                               chunk_overlap=80,
                                               separators=["\n\n", "。", "！", "？", "\n"])

# 3.2 创建一个子文档切分对象
child_splitter=RecursiveCharacterTextSplitter(chunk_size=350,
                                               chunk_overlap=40,
                                               separators=["\n\n", "。", "！", "？", "\n"])

# 进行父文档切分
parent_docs=parent_splitter.split_documents(doc)
id_key="parent_id"
# 父子关联构建
child_docs = []
parent_id_list = []
for parent_doc in parent_docs:
    pid = str(uuid.uuid4())
    parent_id_list.append((pid, parent_doc))
    # 父块切分成若干个子块
    sub_chunks = child_splitter.split_text(parent_doc.page_content)
    for text in sub_chunks:
        child_doc = Document(page_content=text, metadata={id_key: pid})
        child_docs.append(child_doc)

# 把父文档存入内存库
#store=InMemoryByteStore()
# 存入内存
#store.mset(list(parent_id_map.items()))
# 存入MySQL
mysql_store=MySQLDocStore(host="localhost",port=3306,user="root",password="root",database="rag")
mysql_store.batch_save(parent_id_list)

# 把子文档存入向量库
vector = Chroma(collection_name="my_vector_db", embedding_function=embeddings_model)
if len(child_docs)>0:
    # 把Document对象变向量
    vector.add_documents(child_docs)
    #vector.add_texts(texts=child_docs, metadatas=all_child_meta)

# 进行检索
# 自定义一个检索函数
def custom_retrieve(query: str, k=3):
    # 向量库检索出子片段
    child_docs = vector.similarity_search(query, k=k)
    # 提取父ID
    # parent_ids = set([d.metadata["parent_id"] for d in child_docs])
    parent_ids = list({doc.metadata[id_key] for doc in child_docs})
    # 从内存读取完整父文档
    #parent_docs = store.mget(parent_ids)
    parent_docs = mysql_store.batch_get(parent_ids)
    return [p for p in parent_docs if p is not None]

# 进行检索查询
template = """请根据下面给出的上下文来回答问题:
{context}
问题: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
# {"context":"上下文参考内容--父文档的正文内容","question":"北京大学开了个什么会？"}
chain=RunnableMap({"context":lambda x: custom_retrieve(x["question"],k=3),
             "question":lambda x: x["question"]
             }) | prompt | llm

result=chain.invoke({"question":"北京大学开了个什么会？"})
print("=======最终的检索结果=====")
print(result.content)

