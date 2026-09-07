from openai import OpenAI
import streamlit as st

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")
if "messages" not in st.session_state:
    # 会话状态管理,用于存储用户和助手的对话记录
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    # 显示用户和助手的对话记录
    st.chat_message(msg["role"]).write(msg["content"])

# 从对话输入框获取用户输入的内容
if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # 关联大模型
    response = client.chat.completions.create(model="deepseek-v4-flash", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    # 存储助手的回复
    st.session_state.messages.append({"role": "assistant", "content": msg})
    # 保存本次聊天记录
    st.chat_message("assistant").write(msg)