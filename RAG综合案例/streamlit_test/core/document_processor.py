from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import Docx2txtLoader
import os
import tempfile

# 分段
# 向量化
# 存储
class DocumentProcessor:
    def __init__(self,config):
        self.config = config
        # 基础分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

        # 父文档分割器
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE*2,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？"]
        )
        # 子文档分割器
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE //2,
            chunk_overlap=config.CHUNK_OVERLAP//2,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )


    # 用户上传文件，获得文件内容（Document对象）
    def load_document(self, uploaded_file):
        """加载上传的文档"""
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            # 上传的文件全部内容以 bytes 形式取出来
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        print(tmp_path)
        try:
            # 根据文件类型选择加载器
            if uploaded_file.name.endswith('.pdf'):
                loader = PyPDFLoader(tmp_path)
            elif uploaded_file.name.endswith('.docx'):
                loader = Docx2txtLoader(tmp_path)
            elif uploaded_file.name.endswith('.txt'):
                loader = TextLoader(tmp_path, encoding='utf-8')
            else:
                raise ValueError(f"不支持的文件类型: {uploaded_file.name}")

            documents = loader.load()
            return documents
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # 传入文档（上传的文档），获得所有的父文档和所有的子文档，并且每个子文档的元数据中有父文档的id
    def create_parent_child_chunks(self, documents, fileName):
        """创建父子文档块"""
        parent_docs = self.parent_splitter.split_documents(documents)
        # 存放所有的子文档
        child_docs = []

        for i, parent_doc in enumerate(parent_docs):
            # 为每个父文档创建唯一ID
            parent_id = f"{fileName}_parent_{i}" # 西游记.txt_parent_0
            parent_doc.metadata['parent_id'] = parent_id
            parent_doc.metadata['doc_type'] = 'parent'
            #  parent_doc.metadata={"parent_id":"西游记.txt_parent_0","doc_type":"parent"}

            # 从父文档创建子文档
            child_chunks = self.child_splitter.split_documents([parent_doc])
            for j, child_doc in enumerate(child_chunks):
                child_doc.metadata['parent_id'] = parent_id # 西游记.txt_parent_0
                child_doc.metadata['child_id'] = f"child_{i}_{j}" # child_0_1
                child_doc.metadata['doc_type'] = 'child'
                child_docs.append(child_doc)

        return parent_docs, child_docs