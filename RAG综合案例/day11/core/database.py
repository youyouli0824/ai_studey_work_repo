from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# 创建数据库模型基类
Base = declarative_base()

# ORM模型: object-relational mapping
class Document(Base):
    # 指定要创建的表名
    __tablename__ = 'documents'
    # 定义主键
    # 类中的属性名和数据库中的字段名默认是一样的
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content = Column(MEDIUMTEXT, nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now())
    is_active = Column(Boolean, default=True)

    # 一个文档 被 分成了 几个 父块
    # 关联关系：设定一对多，ParentChunk关联模型，back_populates关联字段，cascade级联操作(删除操作)
    parent_chunks = relationship("ParentChunk", back_populates="document", cascade="all, delete-orphan")
    child_chunks = relationship("ChildChunk", back_populates="document", cascade="all, delete-orphan")

# 存储父块的内容
class ParentChunk(Base):
    __tablename__ = 'parent_chunks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    parent_id = Column(String(100), nullable=False, unique=True)  # 父文档唯一标识
    content = Column(Text, nullable=False)
    json_metadata = Column(Text)  # JSON格式存储元数据
    vector_id = Column(String(100))  # Chroma中的向量ID
    created_at = Column(DateTime, default=datetime.now())

    # 关联关系
    document = relationship("Document", back_populates="parent_chunks")
    child_chunks = relationship("ChildChunk", back_populates="parent_chunk", cascade="all, delete-orphan")

    # 索引：提高查询效率，通过树结构快速定位
    __table_args__ = (
        Index('idx_parent_document_id', 'document_id'),
        Index('idx_parent_id', 'parent_id'),
    )

class ChildChunk(Base):
    __tablename__ = 'child_chunks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    parent_chunk_id = Column(Integer, ForeignKey('parent_chunks.id'), nullable=False)
    child_id = Column(String(100), nullable=False)  # 子文档标识
    content = Column(Text, nullable=False)
    json_metadata = Column(Text)  # JSON格式存储元数据
    vector_id = Column(String(100))  # Chroma中的向量ID
    created_at = Column(DateTime, default=datetime.now())

    # 关联关系
    document = relationship("Document", back_populates="child_chunks")
    parent_chunk = relationship("ParentChunk", back_populates="child_chunks")

    # 索引
    __table_args__ = (
        Index('idx_child_document_id', 'document_id'),
        Index('idx_child_parent_id', 'parent_chunk_id'),
        Index('idx_child_id', 'child_id'),
    )

# 存储聊天历史记录
class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    document_ids = Column(String(500))  # 存储使用的文档ID，逗号分隔
    used_chunks = Column(Text)  # JSON格式存储使用的文档块信息
    created_at = Column(DateTime, default=datetime.now())

    # 索引
    __table_args__ = (
        Index('idx_chat_session_id', 'session_id'),
        Index('idx_chat_created_at', 'created_at'),
    )

# 定义数据库管理器类
class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self.init_database()

    def init_database(self):
        # 创建数据库连接
        connection_string = f"mysql+pymysql://{self.config.MYSQL_USER}:{self.config.MYSQL_PASSWORD}@{self.config.MYSQL_HOST}:{self.config.MYSQL_PORT}/{self.config.MYSQL_DATABASE}?charset=utf8mb4"
        try:
            # 创建数据库引擎
            self.engine = create_engine(connection_string, echo=False)
            # 创建所有的表
            Base.metadata.create_all(self.engine)
            # 创建会话工厂
            self.SessionLocal = sessionmaker(bind=self.engine)
            print("数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败: {e}")
            raise

    # 获取数据库会话对象
    def get_session(self):
        return self.SessionLocal()

    # 将document/父块/子块保存到数据库
    # document/父块/子块应该被放在同一个事务中进行实现，确保数据的一致性
    def save_document_with_chunks(self, filename, file_path, content, parent_docs, child_docs, parent_vector_ids,
                                  child_vector_ids):
        """保存文档及其父子文档块"""
        # 会自动开启事务，确保数据的一致性
        session = self.get_session()
        try:
            # 保存主文档
            doc = Document(
                filename=filename,
                file_path=file_path,
                content=content,
                chunk_count=len(child_docs)
            )
            # 实现数据插入----》基于面向对象的思想进行数据插入
            # insert into documents values (?, ?, ?, ?)
            session.add(doc)
            # 只有刷新之后，才能得到文档的id
            session.flush()
            # 获取文档ID
            doc_id = doc.id  # 1

            # 保存父文档块
            parent_chunk_map = {}  # parent_id -> parent_chunk_id 映射
            for i, (parent_doc, vector_id) in enumerate(zip(parent_docs, parent_vector_ids)):
                # 封装父块的数据
                parent_chunk = ParentChunk(
                    document_id=doc_id,
                    parent_id=parent_doc.metadata.get('parent_id', f'parent_{i}'),
                    content=parent_doc.page_content,
                    json_metadata=str(parent_doc.metadata),
                    vector_id=vector_id
                )
                # insert into parent_chunks values (?, ?, ?, ?, ?)
                session.add(parent_chunk)
                session.flush()
                # 父文档存在数据库的id   和   切片之后创建的id进行映射
                parent_chunk_map[parent_chunk.parent_id] = parent_chunk.id

            # 保存子文档块
            for child_doc, vector_id in zip(child_docs, child_vector_ids):
                parent_id = child_doc.metadata.get('parent_id', 'unknown')
                parent_chunk_id = parent_chunk_map.get(parent_id)
                # 封装子块的数据
                child_chunk = ChildChunk(
                    document_id=doc_id,
                    parent_chunk_id=parent_chunk_id,
                    child_id=child_doc.metadata.get('child_id', f'child_{len(child_docs)}'),
                    content=child_doc.page_content,
                    json_metadata=str(child_doc.metadata),
                    vector_id=vector_id
                )
                # insert into child_chunks values (?, ?, ?, ?, ?, ?, ?)
                session.add(child_chunk)

            # 提交事务
            session.commit()
            return doc_id
        except Exception as e:
            # 回滚事务
            session.rollback()
            raise e
        finally:
            # 关闭会话
            session.close()

    # 查询文档与历史信息的方法
    def get_all_documents(self):
        session = self.get_session()
        try:
            # select * from documents where is_active = True
            docs = session.query(Document).filter(Document.is_active == True).all()
            return docs
        finally:
            session.close()

    def get_chat_history(self, session_id, limit=10):
        session = self.get_session()
        try:
            # select * from chat_history where session_id = ? order by created_at desc limit ?
            chats = session.query(ChatHistory).filter(
                ChatHistory.session_id == session_id
            ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
            return list(reversed(chats))
        finally:
            session.close()

    # 保存聊天历史记录
    def save_chat_history(self, session_id, user_message, assistant_message, document_ids=None, used_chunks=None):
        session = self.get_session()
        try:
            chat = ChatHistory(
                session_id=session_id,
                user_message=user_message,
                assistant_message=assistant_message,
                document_ids=document_ids,
                used_chunks=used_chunks
            )
            # insert into chat_history values (?, ?, ?, ?, ?)
            session.add(chat)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
