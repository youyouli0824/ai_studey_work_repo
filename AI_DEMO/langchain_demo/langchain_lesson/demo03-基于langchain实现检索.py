# create_stuff_documents_chain：文档合并链，作用：把检索出来的文档片段全部塞到prompt上下文，交给大模型生成答案（stuff模式：全部文档一次性塞入prompt）
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# ChatPromptTemplate：聊天提示词模板，用来定义给大模型的prompt格式，支持占位符变量填充
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
# create_retrieval_chain：创建完整RAG检索链，串联【检索器】和【文档合并生成链】，完成完整RAG流水线
from langchain_classic.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
# DashScopeEmbeddings：阿里云百炼的Embedding向量化模型，把文本转为向量
from langchain_community.embeddings import DashScopeEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

# 1. 得到一个向量模型， 必须与之前文档的向量模型一致
emb_model=DashScopeEmbeddings(dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
                    model="text-embedding-v4")

# 2.利用Faiss加载本地的向量数据库
vector=FAISS.load_local("faiss_store",
                        emb_model,
                        # pkl是本地的一个序列化文件，在反序列化时可能会有危险。该操作建议只在开发阶段使用。允许危险的反序列化操作，否则会报错
                        allow_dangerous_deserialization=True)

# 用户的提问，RAG要回答的业务问题
input = '什么是分级诊疗协同机制'

# FAISS.from_documents(input,emb_model)
# 3. 检索器：根据用户提问，从向量数据库中检索出最相关的文档片段
#docs=vector.similarity_search(input)
# [Document(id='98e8f32a-2e30-40e6-9cfe-150edd020d0b', metadata={'source': 'https://www.gov.cn/zhengce/content/202604/content_7065030.htm'}, page_content='务下沉和基层能力提升，推动医疗卫生服务资源高效配置，加快建设分级诊疗体系，提出如下措施。一、以紧密型医联体为抓手完善分级诊疗协同机制（一）优化医疗卫生机构功能定位和结构布局。统筹行政区划调整、人口变化'), Document(id='c718e88b-bb4e-4701-ace0-99dd57833833', metadata={'source': 'https://www.gov.cn/zhengce/content/202604/content_7065030.htm'}, page_content='牵头组建紧密型医联体。到2030年，以紧密型医联体为抓手的分级诊疗协同机制基本建立，医疗卫生服务同质化水平和便利性、可及性进一步提高，就医秩序更加合理规范。（三）加强紧密型医联体内医疗资源共享。统筹现'), Document(id='8d2b227b-93a3-47cb-8338-6444eba7f91c', metadata={'source': 'https://www.gov.cn/zhengce/content/202604/content_7065030.htm'}, page_content='由基层医疗卫生机构自主确定，按规定报医保部门备案。（十三）加强宣传引导。积极宣传分级诊疗有关政策措施和基层医疗卫生服务能力建设成效，普及看病就医指引指南、慢性病防控知识，宣传家庭医生签约服务的作用和效'), Document(id='09c98b93-4f08-4b00-94f0-3da25edda8c8', metadata={'source': 'https://www.gov.cn/zhengce/content/202604/content_7065030.htm'}, page_content='步建立全国统一的医保医疗服务项目目录和医用耗材目录。四、完善分级诊疗多元保障措施（十）加快完善紧密型医联体发展保障政策。按规定落实对符合区域卫生规划的医疗卫生机构的财政补助政策。落实“两个允许”要求，')]
#print(docs)

# 得到聊天大模型
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    model="qwen3.7-plus"
)

# 聊天提示词模板
prompt = ChatPromptTemplate.from_template(
"""仅根据提供的上下文回答以下问题:
<context>
{context}
</context>
问题: {input}"""
)

# 3. 从向量库中得到一个检索器，用来根据用户提问，从向量数据库中检索出最相关的文档片段
retriver=vector.as_retriever()

# 4. 文档合并链：把检索出来的文档片段全部塞到prompt上下文，交给大模型生成答案
docs_chain=create_stuff_documents_chain(llm,prompt)

# 5. 创建检索器链: 串联【检索器】和【文档合并生成链】
retriver_chain=create_retrieval_chain(retriver,docs_chain)

# 6. 执行检索器链,把用户的问题作为参数，得到检索结果
# ValueError: The input to RunnablePassthrough.assign() must be a dict.
# input=什么是分级诊疗协同机制
# 根据问题去本地的向量库进行检索----会得到相关的文档片段：[Document(id='98e8f32a-2e30-40e6-9cfe-150edd020d0b....]
# 把检索到的相关片段，作为上下文context----拼接到prompt中
# 把prompt传递给llm，最终生成答案
res=retriver_chain.invoke({"input":input})
print(res)


