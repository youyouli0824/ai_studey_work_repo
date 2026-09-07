import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ===================== 页面全局配置 =====================
st.set_page_config(
    page_title="交互式数据分析看板",
    page_icon="📈",
    layout="wide",   # 宽屏布局
    initial_sidebar_state="expanded"
)

st.title("📊 Streamlit综合数据分析工具")
st.markdown("""
功能清单：
1. 上传CSV数据文件
2. 数据预览、统计描述
3. 条件筛选数据
4. 多类型交互式图表
5. 导出筛选后数据
""")

# ===================== 缓存装饰器：避免重复读取文件 =====================
@st.cache_data
def read_csv(file_obj):
    """读取csv，缓存加速，重复上传不会重复IO"""
    return pd.read_csv(file_obj)

# ===================== 侧边栏区域 =====================
with st.sidebar:
    st.header("🔧 参数配置")
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])

    # 没有上传文件时，生成模拟演示数据
    if uploaded_file is None:
        st.warning("未上传文件，使用内置模拟数据演示")
        df = pd.DataFrame({
            "地区": np.random.choice(["华东","华北","华南","西南"], size=300),
            "产品": np.random.choice(["A产品","B产品","C产品"], size=300),
            "销售额": np.random.randint(1000, 20000, size=300),
            "利润": np.random.randint(100,5000,size=300)
        })
    else:
        df = read_csv(uploaded_file)

    st.divider()
    st.subheader("数据筛选")
    # 获取数值列
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    filter_col = st.selectbox("选择数值筛选字段", num_cols)
    min_val = float(df[filter_col].min())
    max_val = float(df[filter_col].max())
    selected_range = st.slider("数值区间", min_val, max_val, (min_val, max_val))

# ===================== 数据过滤逻辑 =====================
df_filtered = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]

# ===================== 主页面：多标签页布局 =====================
tab1, tab2, tab3, tab4 = st.tabs(["数据概览", "统计分析", "可视化绘图", "导出结果"])

with tab1:
    st.subheader("原始数据预览")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("筛选后数据")
    st.info(f"原始行数：{len(df)} ｜筛选后行数：{len(df_filtered)}")
    st.dataframe(df_filtered, use_container_width=True)

with tab2:
    st.subheader("数值字段统计信息")
    st.write(df_filtered.describe())

    if len(cat_cols) > 0:
        st.subheader("分类字段计数")
        cat_sel = st.selectbox("选择分类列", cat_cols)
        st.write(df_filtered[cat_sel].value_counts())

with tab3:
    st.subheader("交互式绘图(Plotly)")
    col_a, col_b = st.columns(2)
    with col_a:
        x_axis = st.selectbox("X轴", df_filtered.columns)
    with col_b:
        y_axis = st.selectbox("Y轴", num_cols)

    chart_type = st.radio("图表类型", ["柱状图","散点图","箱线图","直方图"], horizontal=True)

    if chart_type == "柱状图":
        fig = px.bar(df_filtered, x=x_axis, y=y_axis)
    elif chart_type == "散点图":
        fig = px.scatter(df_filtered, x=x_axis, y=y_axis)
    elif chart_type == "箱线图":
        fig = px.box(df_filtered, x=x_axis, y=y_axis)
    else:
        fig = px.histogram(df_filtered, x=x_axis)

    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("下载筛选后的数据集")
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 下载CSV文件",
        data=csv_bytes,
        file_name="filtered_data.csv",
        mime="text/csv"
    )
    st.code(df_filtered.head(10).to_csv(index=False), language="csv")
