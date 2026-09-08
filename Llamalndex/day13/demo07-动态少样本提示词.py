import os
from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.prompts import RichPromptTemplate
from llama_index.core.schema import TextNode
from llama_index.llms.deepseek import DeepSeek

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_BASE_URL")
model = "deepseek-v4-pro"

# 设置默认的LLM
Settings.llm = DeepSeek(model=model,api_key=api_key,api_base=api_base_url,temperature=0.1)
Settings.embed_model=DashScopeEmbeddings(dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
                                    model="text-embedding-v4")

# 准备部分案例，添加样本的文档节点
example_nodes = [
    TextNode(
        text="Query: 请生成一个小红帽的故事，输出20字符\n小红帽去看奶奶，遇到大灰狼，被骗了，最后猎人救了她们。"
    ),
    TextNode(
        text="Query: 请生成一个白雪公主的故事，输出20字符\n白雪公主被后妈害，七矮人救她，王子吻醒了她。"
    )
]

# 把样本案例进行向量化入库
index=VectorStoreIndex(nodes=example_nodes)
retriever=index.as_retriever(similarity_top_k=3)

# 根据用户的问题，检索向量库，找到最相关的3个样本案例
def get_examples_fn(**kwargs):
    # 在提示词模板中获取用户的问题
    query=kwargs["query_str"]
    examples=retriever.retrieve(query)
    #如果返回了3个样本，用"\n\n"把这3个样本连接起来
    return "\n\n".join(node.text for node in examples)

prompt_template="""
你是一个故事生成专家
下面是一些例子：
示例：
{{ examples }}

现在轮到你了.
问题: {{ query_str }}
答案: 
"""

template=RichPromptTemplate(prompt_template,
                   function_mappings={"examples":get_examples_fn})
prompt=template.format(query_str="请生成一个黑猫警长的故事")
print(prompt)

# 调用llm，按提示词生成故事
response=Settings.llm.complete(prompt)
print("response:",response)
