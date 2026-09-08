from langchain_community.embeddings import DashScopeEmbeddings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings  # llamaindex的默认配置模块
#from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.deepseek import DeepSeek
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_BASE_URL")
model = "deepseek-v4-flash"

# 设置默认的LLM
Settings.llm = DeepSeek(model=model,api_key=api_key,api_base=api_base_url,temperature=0.1)
Settings.embed_model=DashScopeEmbeddings(dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
                                    model="text-embedding-v4")

# 加载文档
# input_dir:读取目录中的文档；
# input_files:读取指定文件；
document = SimpleDirectoryReader(input_files=["./人事管理流程.docx"]).load_data()
# [Document(id_='36c3842f-ac80-450b-98fd-089177d0e8c1', embedding=None, metadata={'file_name': '人事管理流程.docx', 'file_path': '人事管理流程.docx', 'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'file_size': 116528, 'creation_date': '2026-09-08', 'last_modified_date': '2026-08-10'}, excluded_embed_metadata_keys=['file_name', 'file_type', 'file_size', 'creation_date', 'last_modified_date', 'last_accessed_date'], excluded_llm_metadata_keys=['file_name', 'file_type', 'file_size', 'creation_date', 'last_modified_date', 'last_accessed_date'], relationships={}, metadata_template='{key}: {value}', metadata_separator='\n', text_resource=MediaResource(embeddings=None, data=None, text='汇视威管理制度\n\n人事管理制度\n\n一、聘用\n\n1、聘用原则\n\n\t\t1.1基础岗位人员任用，由部门主管面试确定。\n\n\t\t1.2管理岗位人员任用，由总经理最终面试确定。\n\n\t\t注：基层岗位：主管岗位以下人员均属于基础岗位\n\n2、聘用程序\n\n\t\t   人员需求部门提前申请      人事行政部核实情况     总经理审批          \n\n\t\t\n\n需求部门初试    人事招聘主管复试（管理岗人事经理复试）     总经理复试（管理岗位）\n\n需求部门初试    人事招聘主管复试（管理岗人事经理复试）     总经理复试（管理岗位）   \n\n\t\t\n\n合格者\n\n合格者\n\n1天内电话回访邀约入职并发送录用offer\n\n1天内电话回访邀约入职并发送录用offer                                               \n\n\t\t\n\n不合格\n\n不合格\n\n1天内发送未录用通知短信\n\n1天内发送未录用通知短信\n\n\t\t\n\n\t\t注：在正常编制范围内的人员，不需要提交《人事需求审批表》，可直接招聘，招聘工作由用人部门与人事行政部共同完成。\n\n二、入职\n\n1、人员入职，人事行政部为新员工办理如下手续：\n\n1.1 入职人员提交资料：身份证、银行卡、毕业证、职业资格证、与原单位解除或终止劳动合同证明（此项没有填写无法提供离职证明承诺书）原件审核、体检报告。\n\n1.2 资料审核无误    入职面谈及安排工位    签订培训告知书   \n\n发放入职指引    办理意外保险    进入培训期(7天) \n\n\n\n通过者\n\n通过者\n\n签订入职承诺书、劳动合同、保密协议与竞业协议；\n\n签订入职承诺书、劳动合同、保密协议与竞业协议；\n\n\n\n结束劳动关系\n\n结束劳动关系\n\n不通过\n\n不通过\n\n   \n\n试用与转正\n\n1、试用与转正流程\n\n\t\t\n\n不合格\n\n不合格\n\n合格者\n\n合格者试用期1-3个月    试用期合格与否用人部门提前7天告知人事行政部        员工填写转正申请走审批流程    人事行政部备案\n\n\t\t员工填写离职申请走审批流程    人事行政部办理离职\n\n\t\t员工申请    主管审批    人事招聘主管审批    抄送人事经理/人事主管\n\n\t\t员工申请（主管岗）   人事经理审批    总经理审批    抄送人事招聘/行政主管\n\n2、凡有以下情形者，均被视为不符合录用条件：\n\n2.1不符合招录条件：提供的学历、个人简历、工作经历、技能证明、体检证明等材料或者填写的《员工登记表》等内容与事实不符或有虚假的或者不按入职要求提供资料的；\n\n2.2 与原用人单位未依法解除、终止劳动合同或劳动关系的；或与原用人单位存在竞业限制约定且在限制范围之内的；\n\n2.3体检不合格者或患有职业病、传染病、精神疾病、其他身体健康条件不符合工作岗位要求的；\n\n2.4被发现在外兼职对本职工作造成影响，经书面通知后仍不纠正的；
#print(document)
# 分块---向量化---索引入库
index=VectorStoreIndex.from_documents(document)

# 检索--查询
query_engine=index.as_query_engine()
# 查询
result=query_engine.query("公司什么时间下班？")

print(result)


