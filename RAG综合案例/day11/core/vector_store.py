import chromadb
from langchain_chroma import Chroma
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI

# 负责向量化及存储
class VectorStore:
    def __init__(self, config):
        self.config = config
        # 初始化向量化模型
        self.embeddings = DashScopeEmbeddings(dashscope_api_key=config.OPENAI_API_KEY,
                                           model="text-embedding-v4")
        # 初始化向量数据库
        # 初始化Chromadb客户端
        self.chroma_client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR
        )

        # 父文档和子文档使用不同的集合
        self.parent_vectorstore = Chroma(
            client=self.chroma_client,
            collection_name="parent_documents",  # 父文档的向量数据保存在chromadb的parent_documents表中
            embedding_function=self.embeddings
        )

        # 存储子文档向量的表
        self.child_vectorstore = Chroma(
            client=self.chroma_client,
            collection_name="child_documents",  # 子文档的向量数据保存在chromadb的child_documents表中
            embedding_function=self.embeddings
        )

        # 初始化LLM模型
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.MODEL_NAME,
            temperature=0
        )

        # 配置一个上下文压缩器
        self.compressor = LLMChainExtractor.from_llm(self.llm)

    # 文档向量化入库
    def add_documents(self, parent_docs,child_docs,document_id):
        # 为所有文档添加document_id元数据
        for doc in parent_docs + child_docs:
            # 这个元数据的作用，是以后检索时，根据document_id来继续文档过滤
            doc.metadata['document_id'] = str(document_id)
        # 存储父文档向量
        parent_ids=self.parent_vectorstore.add_documents(parent_docs)
        # 存储子文档向量
        child_ids=self.child_vectorstore.add_documents(child_docs)
        return parent_ids,child_ids

    # 获取检索器对象
    def create_retriever(self,use_compressor=True,document_ids=None):
        search_kwargs={
            # 过召回设计
            "k":self.config.TOP_K*2
        }

        # 根据文档id进行过滤,只在我选择的文档中进行检索
        if document_ids:
            # 增加一个过滤参数，根据document_id来过滤子文档
            # 这里的$in表示在document_ids列表中的任意一个元素
            # 类似于sql中的where document_id in (1,2,3,4)
            search_kwargs["filter"] = {"document_id": {"$in": [str(id) for id in document_ids]}}

        child_retriever=self.child_vectorstore.as_retriever(
            search_kwargs=search_kwargs
        )

        # 如果开启了压缩功能，则使用压缩后的检索器，否则直接返回子文档检索器
        if use_compressor:
            compressed_retriever = ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=child_retriever
            )
            return compressed_retriever
        else:
            return child_retriever

    # 根据父id获取父文档
    def get_parent_documents_by_metadata(self,parent_ids):
        # 根据parent_id找父文档
        if not parent_ids:
            return []

        parent_docs=[]
        for parent_id in parent_ids:
            try:
                # 在父向量库中，找带有parent_id元数据的文档
                result=self.parent_vectorstore.get(where={"parent_id": parent_id})
                parent_docs.extend(result['documents'][0])
            except Exception as e:
                print({e})
                continue
        return parent_docs

    # 根据子文档获取父文档----》子块回溯父块
    def get_parent_document(self,child_docs):
        # set的值不能重复，可以去重
        parent_ids=set()
        # "孙悟空与黄风怪是怎么打的？"=---->可能有5个子文档与该问题相关
        for child_doc in child_docs:
            if 'parent_id' in child_doc.metadata:
                parent_ids.add(child_doc.metadata['parent_id'])
        return self.get_parent_documents_by_metadata(list(parent_ids))






