import streamlit as st

username = st.text_input("请输入用户名")
password = st.text_input("请输入密码")
age=st.number_input("请输入年龄")
date=st.date_input(label="请选择日期",min_value="1900-01-01",max_value="2028-12-31")
time=st.time_input(label="请选择时间")
st.checkbox("同意协议")
st.radio("请选择性别",["男","女"])
st.slider("请设置身高",0,200,5)
btn=st.button("提交")
file=st.file_uploader("请上传文件")
