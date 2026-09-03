from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_neo4j import Neo4jGraph
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

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "qscazx0824" 
# 连接Neo4j
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)