from codecs import getencoder
import json
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
# from langchain.schema import messages_from_dict, messages_to_dict
from langchain_core.messages import messages_from_dict, messages_to_dict
from dotenv import load_dotenv
import os

from pydantic import FilePath
# 加载环境变量（需要包含API_KEY）
load_dotenv()

llm=ChatOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    model="deepseek-v4-flash"
)

prompt=ChatPromptTemplate([
    ("system","你是一个友好可爱的猫娘助手"),
    #历史消息占位符
    MessagesPlaceholder(variable_name="history"),

    ("user","{input}")
])

#构建基础对话链
base_chain=prompt | llm
#全局会话存储字典（key：session_id,Value:ChatMessageHistory实例）
store={}

def get_session_history(session_id):
    """获取或创建会话历史存储对象
    Args:
        session_id: 会话唯⼀标识（⽤于多会话隔离）
    Returns:
        对应会话的聊天历史记录对象
    """
    if session_id not in store:
        store[session_id]=ChatMessageHistory()
    return store[session_id]

#创建支持历史记录的对话链
conversation=RunnableWithMessageHistory(
    base_chain,#基础对话链
    get_session_history=get_session_history,#获取历史记录方法
    input_messages_key="input",#输入文本的键
    history_messages_key="history"#历史记录的键
)

def save_memory(filepath,session_id):
    """保存指定会话的历史记录到⽂件
    Args:
        filepath: ⽂件保存路径（建议使⽤.json扩展名）
        session_id: 要保存的会话ID（默认"default"）
    """
    history=get_session_history(session_id)
    dicts=messages_to_dict(history.messages)
    #写入json文件
    with open(filepath,"w",encoding="utf-8")as f:
        json.dump(dicts,f,ensure_ascii=False)

def load_memory(filepath,session_id):
    """从⽂件加载历史记录到指定会话
    Args:
        filepath: 历史记录⽂件路径
        session_id: 要加载到的会话ID（默认"default"）
    """
    with open(filepath,"r",encoding="utf-8") as f:
        dicts=json.load(f)
    #将字典转换回消息对象列表
    messages=messages_from_dict(dicts)
    #更新全局存储的会话历史
    store[session_id]=ChatMessageHistory(messages=messages)

def legacy_predict(input_text:str,session_id:str="default")->str:
    return conversation.invoke(
        {"input":input_text},#输入参数
        #配置参数
        config={"configurable":{"session_id":session_id}}
    ).content

if __name__ =="__main__":
    #使用默认会话id
    SESSION_ID="default"
    #模拟连续4轮对话
    legacy_predict("hello",SESSION_ID)
    legacy_predict("你是谁，我是liyouyou",SESSION_ID)
    legacy_predict("燃烧的本质是什么？",SESSION_ID)
    last_response=legacy_predict("截至到现在，我们聊了些什么？",SESSION_ID)

    print("最后一次回答：",last_response)

    #持久化保存对话历史（JSON）
    save_memory(r"AI_DEMO\langchain_demo\my_langchain_work\记忆相关\记忆文件保存\memory_new.json",SESSION_ID)

    #模拟重新加载历史记录
    load_memory(r"AI_DEMO\langchain_demo\my_langchain_work\记忆相关\记忆文件保存\memory_new.json",SESSION_ID)

    #验证历史恢复效果
    reload_response=legacy_predict("再次问你，我们之前聊的什么？",SESSION_ID)

    print("\n恢复后的回答：",reload_response)