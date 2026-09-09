from langchain_community.embeddings import DashScopeEmbeddings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, get_response_synthesizer
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.llms.deepseek import DeepSeek
from llama_index.core import Settings
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
)
import os
import asyncio

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_BASE_URL")
model = "deepseek-v4-flash"

# 配置LLM
Settings.llm = DeepSeek(model=model,api_key=api_key,api_base=api_base_url,temperature=0.1)
# 配置向量模型embeddings
Settings.embed_model = DashScopeEmbeddings(dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
                                    model="text-embedding-v4")

# 1. 加载文档
document=SimpleDirectoryReader(input_files=[r"C:\shoolwork\my_python_work_myself\Llamalndex\day13\人事管理流程.docx"]).load_data()

# 2. 设置分割器
splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50,separator=" ")

# 3. 分割文档
nodes=splitter.get_nodes_from_documents(document)

# 4. 给每段话提取标题
# num_workers: 并发数，默认1,设置为5个线程
# nodes=5，不是节点的数量,会参考5个节点的内容生成标题
title_extractor=TitleExtractor(nodes=5,node_template="请为以下文档生成一个简洁的标题: {context_str}",num_workers=5)

# 5. 生成问答对
# 提示词模版
question_prompt_template = """
以下是参考内容：
{context_str}
请根据上述上下文信息，生成 {num_questions} 个该内容能够具体回答的问题，这些问题的答案最好是该内容独有的，不容易在其他地方找到。
你也可以参考上下文中可能提供的更高层次的总结信息，结合这些总结，尽可能生成更优质、更具有针对性的问题。请用中文输出！
"""
qa_extractor=QuestionsAnsweredExtractor(questions=3,prompt_template=question_prompt_template,num_workers=5)

# 6. 主函数
async def main():
    # 6. 提取标题
    # 以同步的方式进行提取
    #titles=title_extractor.extract(nodes)
    # 以异步的方式进行提取
    titles= await title_extractor.aextract(nodes)

    # 7. 生成问答对
    # qa_extractor.extract(nodes)
    qas= await qa_extractor.aextract(nodes)

    # 8.把标题和问答对关联到每个节点的元数据中
    for node, t, q in zip(nodes, titles, qas):
        # 直接把标题和问答对更新到元数据中
        node.metadata.update(t)
        node.metadata.update(q)

    # 输出节点的元数据
    for node in nodes:
        print(node.metadata)
        print("="*50)
        print(node)
        print("="*50)

    # 等给node附加了元数据之后，再创建索引----》检索
    #index = VectorStoreIndex.from_nodes(nodes)

if __name__ == "__main__":
    asyncio.run(main())
