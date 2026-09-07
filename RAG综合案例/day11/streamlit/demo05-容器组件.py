import streamlit as st

container1=st.container(width="stretch",height="content",horizontal=False,horizontal_alignment="left", vertical_alignment="top", gap="small")
container1.write("这是一个容器组件")
container1.write(st.button("提交"))
container1.table([1, 2, 3])

container2 = st.container(border=None, key=None, width="stretch", height="content", horizontal=False, horizontal_alignment="left", vertical_alignment="top", gap="small")
container2.write(st.file_uploader("upload111"))
container2.write(st.button("确认111"))
