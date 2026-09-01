from base_llm import llm, embeddings_model
from typing import List
from langchain_core.stores import InMemoryByteStore
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 多向量检索核心组件
from langchain_classic.retrievers import MultiVectorRetriever
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
# 结构化输出约束
from pydantic import BaseModel, Field
import uuid

# 1. 加载问题
textloader = TextLoader('deepseek介绍.txt',encoding='utf-8')
docs=textloader.load()

# 2.文本分割
splitter=RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=100)
chunks=splitter.split_documents(docs)

# 3.把假设性问题进行向量入库
# 让llm对分段的文本进行推理，让llm站在用户的角度，看看该段文本可能会提出哪些问题----》假设性问题

# 提示词：要求读取文本，输出规范JSON数组
prompt = ChatPromptTemplate.from_template(
    """请基于以下文档生成3个假设性问题(必须使用JSON格式):
    {doc}
    要求：
    1. 输出必须为合法的JSON格式，包含questions字段
    2. questions字段的值是包含3个问题的数组
    3. 使用中文提问
    示例格式：
    {{
        "questions": ["问题1", "问题2", "问题3"]
    }}"""
)

# 假设性问题数据约束模型
class HypotheticalQuestions(BaseModel):
    # 假设性问题列表，questions字段的值是一个包含了3个问题的数组
    questions: List[str] = Field(..., description="基于文档生成3条假设性中文问题")

# 生成假设性问题链路
chain = (
    {"doc":lambda x:x.page_content}
    | prompt
    | llm.with_structured_output(HypotheticalQuestions)
    | (lambda x:x.questions)
)

# 得到分段的假设性问题
chunk_questions=chain.batch(chunks,{"max_concurrency":5})
# [['如果DeepSeek没有在2023年成立初期获得幻方量化提供的万张A100芯片硬件支持，那么其后续发布的DeepSeek-V2、V3等模型的研发进度和性能表现可能会受到怎样的影响？', '假设澳大利亚政府在2025年2月6日并未以', '如果DeepSeek在2024年12月选择继续保密而非公开回应所谓'], ...]
print(chunk_questions)

# 准备一个向量库
vectorstore = Chroma(collection_name="my_db",embedding_function=embeddings_model)
store = InMemoryByteStore()
# 绑定关联元数据key：用来匹配问句和对应原文块
id_key = "doc_id"
# 实例化多向量检索器，关联向量库、内存库
retriever = MultiVectorRetriever(
    vectorstore = vectorstore,
    byte_store = store,
    id_key=id_key
)

# 把假设性问题与原文建立关联
doc_ids = [str(uuid.uuid4()) for _ in chunks]
# 存放的是假设性问题及对应的原文块id
# [Document(page_content="问题1",metadata={"doc_id":"123"}), ...]
questions_docs = []
for i,chunks_question_list in enumerate(chunk_questions):
    # 循环生成的3个问句，将每条问句封装为一个向量文档对象
    questions_docs.extend(
        [Document(page_content=question,metadata={id_key:doc_ids[i]}) for question in chunks_question_list]
    )

# 把假设性问题进行向量入库
retriever.vectorstore.add_documents(questions_docs)
# 把分段的原文及对应的id进行关联
retriever.docstore.mset(list(zip(doc_ids,chunks)))

# 进行检索
query="deepseek是先进的大语言模型吗？"
# 回答提示词模板
prompt1 = ChatPromptTemplate.from_template("根据下面的文档回答问题:\n\n{doc}\n\n问题: {question}")
# 问答链路：用户问题→检索匹配相似假设问句→拉取完整原文→LLM生成答案
qa_chain = RunnableMap({
    "doc": lambda x: retriever.invoke(x["question"]),
    "question": lambda x: x["question"]
}) | prompt1 | llm | StrOutputParser()

result = qa_chain.invoke({"question":query})
print(result)

