import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']     
plt.rcParams['axes.unicode_minus'] = False

# ========== 1. 读取数据 ==========
df = pd.read_csv(
    r"C:\shoolwork\my_python_work_myself\shoolwork\np_pd_plot_works\三次产业结构占比演变.csv",
    encoding='utf-8-sig'
)
print( df.head())
# ========== 2. 重塑为长格式（melt），便于后续分析 ==========
# 将 第一/第二/第三产业占比 从宽表转为长表
df_long = pd.melt(
    df,
    id_vars=['年份'],                           # 保留“年份”列不动
    value_vars=['第一产业占比_%', '第二产业占比_%', '第三产业占比_%'],  # 要融化的列
    var_name='产业',                              # 新列名：原来的列名存入此列
    value_name='占比_%'                            # 新列名：原来的值存入此列
)


# ========== 3. 绘制堆叠面积图 ==========
plt.figure(figsize=(12, 6))

# 堆叠面积图需要的 X 轴（年份）和 Y 轴（各产业分别一列）
years = df['年份'].values
y1 = df['第一产业占比_%'].values   # 底层的值
y2 = df['第二产业占比_%'].values   # 中间层的值
y3 = df['第三产业占比_%'].values   # 顶层的值

# stackplot：从上到下依次堆叠，先画第三产业，再画第二产业，最后画第一产业（底层）
colors = ['#66c2a5', '#fc8d62', '#8da0cb']  # 绿、橙、蓝
plt.stackplot(years, y1, y2, y3,
              labels=['第一产业', '第二产业', '第三产业'],
              colors=colors,
              alpha=0.8)

plt.xlabel('年份')
plt.ylabel('占比（%）')
plt.title('杭州市三次产业结构演变（2000‑2024）', fontsize=14)
plt.legend(loc='upper left')         # 图例放在左上角，不影响数据区域
plt.grid(True, linestyle=':', alpha=0.4, axis='y')   # 仅 Y 轴网格
plt.tight_layout()
plt.show()

# ========== 4. 选取 2024 年绘制饼图 ==========
df_2024 = df[df['年份'] == 2024]
if df_2024.empty:
    print("未找到 2024 年数据！")
else:
    sizes = [df_2024['第一产业占比_%'].values[0],
             df_2024['第二产业占比_%'].values[0],
             df_2024['第三产业占比_%'].values[0]]
    labels = ['第一产业', '第二产业', '第三产业']

    plt.figure(figsize=(7, 7))
    # 突出显示第三产业（explode 参数）
    explode = (0, 0, 0.08)  # 第三产业稍微分离
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',        # 显示百分比，保留一位小数
        startangle=90,           # 从 90° 开始画
        explode=explode,
        colors=['#66c2a5', '#fc8d62', '#8da0cb'],
        pctdistance=0.75,        # 百分比标签距离圆心距离
        textprops={'fontsize': 12}
    )

    plt.title('2024 年杭州市三次产业结构占比', fontsize=14)
    # 在外侧追加带百分比的图例（可选，美化）
    plt.tight_layout()
    plt.show()