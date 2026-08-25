from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import os
import dotenv

# 定义一个RAG知识库类，负责管理向量库的增删改查
class MyVectorDBConnector:
    # 构造方法：在构造方法中进行初始化
    def __init__(self, collection_name):
        self.openai = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"),
                             base_url=os.getenv("DASHSCOPE_BASE_URL"))
        chroma_client=chromadb.PersistentClient("./chroma_db")
        self.collection_name = chroma_client.get_or_create_collection(name=collection_name)

    # 负责把文档变成向量
    def get_embedding(self,text, model_name="text-embedding-v4"):
        # 获取一个embedding模型，用该模型将text转为向量
        data = self.openai.embeddings.create(input=text, model=model_name).data
        return [x.embedding for x in data]

    # 将文档变成向量，并添加到向量库
    def add_document(self, documents):
        embeddings = self.get_embedding(documents)
        self.collection_name.add(embeddings=embeddings,
            documents=documents,
            # 为每个文档生成一个唯一的ID
            ids=[f"id{i}" for i in range(len(documents))])

    # 从向量库中查询
    def search(self,query,top_n):
        # 将查询文本转换为向量
        query_embedding = self.get_embedding([query])
        results = self.collection_name.query(
            query_embeddings=query_embedding,
            n_results=top_n
        )
        return results

# 按照滑动窗口切割文档
def sliding_window_chunks(text, chunk_size, stride):
    # 挑选固定字符长度的文本片段
    return [text[i:i + chunk_size] for i in range(0, len(text), stride)]

# 从PDF文件中提取文字片段
def extract_text_from_pdf(filename, page_numbers=None):
    '''从PDF文件中（按指定页码）提取文字'''
    full_text = ''
    # extract_pages(filename)会返回一个列表，每个元素是一个页面的布局对象
    for i, page_layout in enumerate(extract_pages(filename)):
        # 跳过指定页码外的页面
        if page_numbers is not None and i not in page_numbers:
            continue
        # 遍历当前页中的所有元素
        for element in page_layout:
            # 判断当前元素是否为文本类型
            if isinstance(element, LTTextContainer):
                # 去除文本中的换行符和空格，拼接成连续的字符串
                full_text += element.get_text().replace("\n", "").replace(" ", "")
    text_chunks = sliding_window_chunks(full_text, 250, 100)
    return text_chunks

# 全局固定提示词模板（解决类内无法读取的作用域bug）
prompt_template = """
你是一个问答机器人。
你的任务是根据下述给定的已知信息回答用户的问题。
确保你的回复完全依据下述已知信息，不要编造答案。
如果下述已知信息不足以回答用户的问题，请直接回复"我无法回答您的问题"。

已知信息:
__INFO__

用户问题：
__QUERY__

请用中文回答用户的问题。
"""

#封装一个大模型的聊天机器人类
class MyChatBot:
    def __init__(self, vector_db, n_results=2):
        self.vector_db = vector_db
        self.n_results = n_results
        self.openai = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"),
                             base_url=os.getenv("DASHSCOPE_BASE_URL"))

    # 将提示词丢给大模型，大模型回答
    def get_chat_completion(self,prompt,model="qwen-plus"):
        messages = [{"role": "user", "content": prompt}]
        response=self.openai.chat.completions.create(model=model,messages=messages,temperature=0)
        # 从大模型中提取第一个答案
        return response.choices[0].message.content

    #接收用户的问题，大模型根据用户的问题，最终生成对应的答案
    def chat(self,user_query):
        # 把用户的问题向量化，根据该向量查询向量库中的文档
        search_results=self.vector_db.search(user_query,self.n_results)

        # 拼接检索上下文，每个文档之间用换行符隔开
        context = "\n".join(search_results['documents'][0])
        # print('context', context)
        # 填充模板
        prompt = prompt_template.replace("__INFO__", context).replace("__QUERY__", user_query)
        print("prompt",prompt)
        return self.get_chat_completion(prompt)

if __name__ == "__main__":
    load_dotenv()

    # 创建一个RAG知识库，封装一个类进行向量库的管理
    vector_db = MyVectorDBConnector("demo03")
    #加载原始文档，并分段
    documents = extract_text_from_pdf("财务管理文档.pdf")
    #print(documents)
    vector_db.add_document(documents)

    user_query = "财务管理权限划分?"
    result=vector_db.search(user_query,3)
    #print(result)

    bot=MyChatBot(vector_db)
    response=bot.chat(user_query)
    print("最终结果",response)
