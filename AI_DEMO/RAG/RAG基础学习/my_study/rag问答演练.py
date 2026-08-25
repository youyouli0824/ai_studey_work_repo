from pathlib import Path
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from sentence_transformers import SentenceTransformer

# 路径都相对于本脚本所在目录，避免换了工作目录就跑不起来
BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR.parent / "lesson_demo" / "财务管理文档.pdf"
# DeepSeek 官方接口没有 embedding 能力，向量化改用本地 BGE 中文模型（离线可用）
EMBED_MODEL_PATH = BASE_DIR.parent.parent / "RAG_shoolwork" / "myProject" / "models" / "BAAI" / "bge-large-zh-v1.5"


#知识库类
class MyVectorDBConnector:
    def __init__(self,collection_name):
        self.embedder = SentenceTransformer(str(EMBED_MODEL_PATH), local_files_only=True)
        chroma_client=chromadb.PersistentClient(path=str(BASE_DIR / "chromadb"))
        self.collection=chroma_client.get_or_create_collection(name=collection_name)

    #把文档/查询变成向量
    def get_embedding(self,texts,is_query=False):
        # BGE 官方建议：检索用的短查询加上这句前缀效果更好；入库文档不用加
        if is_query:
            texts = ["为这个句子生成表示以用于检索相关文章：" + t for t in texts]
        return self.embedder.encode(texts, normalize_embeddings=True).tolist()

    #变成向量后，添加到向量数据库（upsert 保证重复运行不会因为 id 重复报错）
    def add_document(self,documents):
        embeddings=self.get_embedding(documents)
        self.collection.upsert(embeddings=embeddings,
                               documents=documents,
                               ids=[f"id{i}" for i in range(len(documents))])

    #从向量数据库查询
    def search(self,query,top_n):
        #把查询文本转成向量
        query_embedding=self.get_embedding([query],is_query=True)
        results=self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_n
        )
        return results

#按照滑动窗口切割文档
def sliding_window_chunks(text,chunk_size,stride):
    return [text[i:i+chunk_size] for i in range(0,len(text),stride)]

#从pdf文件里提取文字片段
def extract_text_from_pdf(filename,page_numbers=None):
    #从pdf文件按指定页码提取文字
    full_text=''
    #extract_pages(filename)会返回一个列表，每个元素是一个页面的布局对象
    for i,page_layout in enumerate(extract_pages(filename)):
        if page_numbers is not None and i not in page_numbers:
            continue
        #遍历当前页面里所有元素
        for element in page_layout:
            #判断当前元素是否是文本类型
            if isinstance(element,LTTextContainer):
                full_text+=element.get_text().replace("\n","").replace(" ","")
    text_chunks=sliding_window_chunks(full_text,250,100)
    return text_chunks

#全局固定提示词模板
prompt_template="""
你是一个问答猫娘助手。
每一小句话结尾都要加“喵”，语气柔和。
任务是根据下面给定的已知信息回答用户的问题。
确保你的回复完全依据下述已知信息，不要编造答案。
如果已知信息不足以回答用户的问题，请直接回复“人家回答不出这个问题喵。”

已知信息：
__INFO__

用户问题：
__QUERY__

请使用中文回答用户的问题。
"""

#封装一个大模型的聊天机器人的类
class MyChatBot:
    def __init__(self,vector_db,n_results=2):
        self.vector_db=vector_db
        self.n_results=n_results
        self.openai=OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                           base_url=os.getenv("DEEPSEEK_BASE_URL"))

    #把提示词给大模型，让大模型回答
    def get_chat_completion(self,prompt,model="deepseek-v4-flash"):
        messages=[{"role":"user","content":prompt}]
        response=self.openai.chat.completions.create(model=model,messages=messages,temperature=0.4)
        return response.choices[0].message.content

    #接收用户的问题，大模型根据用户的问题，最终生成对应的答案
    def chat(self,user_query):
        #把用户的问题转化成向量
        search_results=self.vector_db.search(user_query,self.n_results)
        #拼接检索上下文
        context="\n".join(search_results['documents'][0])
        prompt=prompt_template.replace("__INFO__",context).replace("__QUERY__",user_query)
        #print("prompt",prompt)
        return self.get_chat_completion(prompt)

if __name__ == "__main__":
    # Windows 控制台默认 GBK 编码，PDF 里可能有 GBK 表示不了的字符，先切到 UTF-8 避免打印时崩溃
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    load_dotenv(BASE_DIR / ".env")

    #创建一个RAG知识库，封装一个类管理向量库
    vector_db=MyVectorDBConnector("mytest")
    #加载原始文档，分段
    documents=extract_text_from_pdf(str(PDF_PATH))
    #print(documents)
    vector_db.add_document(documents)

    user_query="财务管理权限划分？"

    result=vector_db.search(user_query,3)
    #print(result)
    bot=MyChatBot(vector_db)
    response=bot.chat(user_query)

    print(response)
