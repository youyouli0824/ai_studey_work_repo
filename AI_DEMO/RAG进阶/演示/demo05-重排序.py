from langchain_chroma import Chroma
from base_llm import llm, embeddings_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# 测试文本数据集
texts = [
    "人工智能在医疗诊断中的应用。",
    "人工智能如何提升供应链效率。",
    "NBA季后赛最新赛况分析。",
    "传统法式烘焙的五大技巧。",
    "红楼梦人物关系图谱分析。",
    "人工智能在金融风险管理中的应用。",
    "人工智能如何影响未来就业市场。",
    "人工智能在制造业的应用。",
    "今天天气怎么样",
    "人工智能伦理：公平性与透明度。"
]

vectorstore = Chroma.from_texts(texts, embedding=embeddings_model)
retriever = vectorstore.as_retriever()

# 将单个问题转换为多个相关的问题
prompt = PromptTemplate(
    input_variables=["original_query"],
    template="""You are a helpful assistant that generates multiple search queries based on a single input query.
Generate multiple search queries related to: {original_query}
Output 4 related search queries separated by newlines, no extra text."""
)

# prompt_chain = prompt | llm | StrOutputParser()
# result=prompt_chain.invoke({"original_query": "人工智能的应用"})
# print(result)

# 构建多查询生成链路
generate_queries = (
    prompt | llm | StrOutputParser() | (lambda x: x.split("\n"))
)

# 编写重排序算法
# [[Document(id='001', metadata={}, page_content='人工智能在医疗诊断中的应用。'),Document(id='002', metadata={}, page_content='人工智能在医疗诊断中的应用222。')],[],[],[]]
def reciprocal_rank_fusion(results: list[list], k=60):
    print("====各查询单独检索结果====")
    print(results)
    # {"001":0.05,"002":0.7,...}
    fused_scores = {}
    # {"001":Document(id='001', metadata={}, page_content='人工智能在医疗诊断中的应用。'),"002":Document(id='002', metadata={}, page_content='人工智能在医疗诊断中的应用222。'),...}
    doc_id_map = {}  # id映射原始文档，替代序列化

    # 遍历每个检索结果列表（每个查询对应的结果）
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_id = doc.id
            doc_id_map[doc_id] = doc
            # 如果文档是第一次出现，初始化分数为0
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
            # 如果文档不是第一次出现，根据排名更新分数
            fused_scores[doc_id] += 1 / (rank + k)

    # 按融合分数降序排序
    sorted_items = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    # 还原文档对象，不再使用loads
    reranked = [(doc_id_map[doc_id], score) for doc_id, score in sorted_items]
    return reranked

original_query = "人工智能的应用"
# 完整链路：多查询生成 -> 批量检索 -> RRF重排
chain = generate_queries | retriever.map() | reciprocal_rank_fusion
result_list = chain.invoke({"original_query": original_query})

# 循环打印重排后的文档与分数
for doc, score in result_list:
    print(f"融合分数：{score:.4f} | 文档内容：{doc.page_content}")