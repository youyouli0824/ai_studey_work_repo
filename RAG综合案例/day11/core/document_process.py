# 负责文档的处理：包括文档的分块等操作
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import Docx2txtLoader
import os
import tempfile

# 负责文档的处理：包括文档的加载和分块等操作
class DocumentProcessor:
    def __init__(self, config):
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
            chunk_size=config.CHUNK_SIZE//2,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )

    # 加载文档----》Document对象列表
    def load_document(self,uploaded_file):
        # 拿到上传来的文件，将其转为临时文件，再加载文档，向量化之后将临时文件删除
        # mv.jpg ---->拿到mv.jpg的临时文件路径
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tem_path=tmp_file.name
            print("temp path",tem_path)

        try:
            if uploaded_file.name.endswith(".pdf"):
                loader = PyPDFLoader(tem_path)
            elif uploaded_file.name.endswith(".txt"):
                loader=TextLoader(tem_path,encoding="utf-8")
            elif uploaded_file.name.endswith(".docx"):
                loader=Docx2txtLoader(tem_path)
            else:
                raise ValueError(f"不支持的文件格式：{uploaded_file.name}")

            # 加载文档
            return loader.load()
        except Exception as e:
            print(f"加载文档失败：{e}")
            # 真正开发时，应该把异常信息记录到日志文件中、ELK等日志系统中
        finally:
            # 清除临时文件，避免占用空间过长
            if os.path.exists(tem_path):
                os.remove(tem_path)

# 进行文档切分----父子双层切分
def create_parent_child_chunks(self, documents,fileName):
    # 父文档切分
    parent_docs=self.parent_splitter.split_documents(documents)

    # 遍历每个父文档，对父文档进行切分----》子文档
    for i, parent_doc in enumerate(parent_docs):
        # "西游记_parent_0"
        parent_id=f"{fileName}_parent_{i}"
        # 给父文档添加元数据
        parent_doc.metadata['parent_id']=parent_id
        parent_doc.metadata['doc_type']='parent'

        # 存放子文档的列表
        child_docs=[]

        # 子文档切分
        child_chunks=self.child_splitter.split_documents([parent_doc])
        # 遍历子文档，将子文档和父文档建立映射关系
        for j, child_doc in enumerate(child_chunks):
            # 给子文档添加元数据
            child_doc.metadata['parent_id'] = parent_id
            child_doc.metadata['doc_type'] = 'child'
            parent_doc.metadata['child_id'] = f'child_{i}_{j}'
            parent_doc.metadata['doc_type'] = 'parent'
            # 将每个子文档存入到child_docs列表中
            child_docs.append(child_doc)

    return parent_docs,child_docs





