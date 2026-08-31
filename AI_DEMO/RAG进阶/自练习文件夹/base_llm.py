from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_community.embeddings import DashScopeEmbeddings
load_dotenv()

embeddings_model = DashScopeEmbeddings(
    dashscope_api_key=os.getenv('DASHSCOPE_API_KEY'),
    
    model="text-embedding-v1"
)

llm=ChatOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model="deepseek-v4-flash"
)