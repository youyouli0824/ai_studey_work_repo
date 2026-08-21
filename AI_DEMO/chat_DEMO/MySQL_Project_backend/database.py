from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:qscazx0824@127.0.0.1:3306/my-first-sql?charset=utf8mb4"
engine=create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)
# 创建数据库会话类 SessionLocal
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
#创建ORM模型的基类Base
Base=declarative_base()
#依赖函数：获取数据库Session会话
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()