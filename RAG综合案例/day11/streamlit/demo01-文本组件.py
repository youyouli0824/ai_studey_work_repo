import streamlit as st
import pandas as pd

#<html><head><title>文本组件</title></head></html>

st.title("百度一下,你就知道")
st.write("这是一个段落")
st.title("这是一个主标题")
st.header("这是一个大标题")
st.subheader("这是一个小标题")
st.text("这是一个文本")
st.markdown("## 这是一个二级标题")
# 数据表格组件
st.dataframe(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
# 表格组件
st.table([1,2,3])
# JSON组件
st.json({"a": 1, "b": 2})
