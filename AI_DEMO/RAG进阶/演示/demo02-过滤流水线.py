from base_llm import llm, embeddings_model
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter, LLMChainFilter
from langchain_classic.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_community.document_transformers import EmbeddingsRedundantFilter

# 1. 加载文档
doc=TextLoader("deepseek介绍.txt",encoding="utf-8").load()

# 2. 分割文档
text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,
                                             chunk_overlap=100)
texts=text_splitter.split_documents(doc)

# 3. 向量入库
chroma=Chroma.from_documents(
    documents=texts,
    embedding=embeddings_model,
    persist_directory="./chroma_db",
)

# 4. 得到一个检索器
retriver=chroma.as_retriever()

print("===========过滤前的效果=============")
doc_result=retriver.invoke("deepseek的发展历程")
print("基础检索召回的文档数量：",len(doc_result))
if len(doc_result) == 0:
    print("警告：基础检索没有召回任何文档！检查文本内容与查询是否相关")
else:
    for d in doc_result:
        print("-" * 50)
        print(d.page_content)

print("===========过滤后的效果=============")
# 该过滤器内部关联了大模型，内部会有一个提示词：“问题：{query}，文档：{document}，请判断文档是否与问题相关，该出True或False的判断结果”
# llm_filter=LLMChainFilter.from_llm(llm)

# 将片段和片段进行余弦相似度对比，判断出两个片段的相似程度，当两个片段的相似度大于0.95时，认为是冗余的重复的
redundant_filter=EmbeddingsRedundantFilter(embeddings=embeddings_model,similarity_threshold=0.95)
# 把用户提的问题和检索的片段进行对比，如果问题向量和文档向量相似度超过0.7，则保留该片段；否则，过滤掉该片段
embedding_filter=EmbeddingsFilter(embeddings=embeddings_model,similarity_threshold=0.7)
# 5. 过滤流水线---多级过滤器，先进行冗余过滤，再进行向量过滤
pipeline=DocumentCompressorPipeline(
    transformers=[redundant_filter,embedding_filter]
)

compressed_retriver=ContextualCompressionRetriever(
    #base_compressor=llm_filter,
    #base_compressor=embedding_filter,
    base_compressor=pipeline,
    base_retriever=retriver
)

compressed_result=compressed_retriver.invoke("deepseek的发展历程")
print("过滤后的检索器召回的文档数量：",len(compressed_result))
for d in compressed_result:
    print("-" * 50)
    print(d.page_content)


