import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取杭州市GDP数据（1949-2024年）
data_path = r"C:\shoolwork\my_python_work_myself\shoolwork\np_pd_plot_works\t1.csv"
df = pd.read_csv(data_path, encoding="utf-8-sig")

# 列名
year_col = '年份'
gdp_col = '地区生产总值_亿元'

# 数据清洗：去除缺失值，将GDP列转换为数值类型
df = df.dropna(subset=[year_col, gdp_col])
df[gdp_col] = pd.to_numeric(df[gdp_col], errors='coerce')
df = df.dropna(subset=[gdp_col])

# 提取数据（全部年份）
years = df[year_col].astype(str)
gdp = df[gdp_col]

# ========== 1. 选取改革开放后（1978年至今）的子集 ==========
df_1978 = df[df[year_col] >= 1978].copy()
gdp_1978 = df_1978[gdp_col].values
years_1978_num = df_1978[year_col].values

# 计算复合年均增长率（CAGR）: (末值/初值)^(1/年数) - 1
start_gdp = gdp_1978[0]
end_gdp = gdp_1978[-1]
n_years = years_1978_num[-1] - years_1978_num[0]
cagr = (end_gdp / start_gdp) ** (1 / n_years) - 1

print(f"1978年GDP: {start_gdp:.2f} 亿元")
print(f"2024年GDP: {end_gdp:.2f} 亿元")
print(f"改革开放后年均复合增长率 (1978-2024): {cagr*100:.2f}%")

# ========== 2. 找出关键突破点 ==========
thresholds = [1000, 5000, 10000]
breakthrough_points = {}  # {阈值: (年份, GDP值)}
for th in thresholds:
    match = df[df[gdp_col] >= th]
    if not match.empty:
        row = match.iloc[0]
        breakthrough_points[th] = (row[year_col], row[gdp_col])
        print(f"GDP首次突破 {th} 亿元: {row[year_col]}年 ({row[gdp_col]:.2f}亿元)")
    else:
        print(f"GDP未突破 {th} 亿元")

# ========== 3. 绘制折线图 ==========
plt.figure(figsize=(14, 5))
plt.plot(years, gdp, color='#1f77b4', marker='o', markersize=3, lw=1.5, label='杭州市GDP')

# 关键节点标注
for th, (yr, val) in breakthrough_points.items():
    # 找到该年份在图表中的横坐标索引
    idx = df[df[year_col] == yr].index[0]
    # 使用annotate标注，带箭头
    plt.annotate(
        f'{yr}年\n突破{th}亿',
        xy=(idx, val),
        xytext=(idx, val + 2000),
        arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
        fontsize=9,
        color='red',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7)
    )

# 横轴刻度：每5年显示一次
tick_indices = range(0, len(years), 5)
plt.xticks(ticks=tick_indices, labels=years.iloc[tick_indices], rotation=45)

# 标题、轴标签、网格
plt.title('杭州市GDP增长趋势（1949-2024年）', fontsize=16)
plt.xlabel('年份')
plt.ylabel('GDP（亿元）')
plt.grid(True, ls=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()