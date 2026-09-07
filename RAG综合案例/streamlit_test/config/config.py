import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    OPENAI_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

    MODEL_NAME = os.getenv("MODEL_NAME")
        # MySQL配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PWD", "qscazx0824")
    MYSQL_DATABASE = os.getenv("MYSQL_DB", "new_streamlit")
        # Chroma配置
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "../core/chroma_db")
    #EMBED_MODEL_PATH = os.getenv("EMBED_MODEL_PATH")
        # 其他配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K = int(os.getenv("TOP_K", 5))