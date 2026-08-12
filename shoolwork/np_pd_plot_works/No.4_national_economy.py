import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']     
plt.rcParams['axes.unicode_minus'] = False

economy_data=pd.read_csv(r"C:\shoolwork\my_python_work_myself\shoolwork\np_pd_plot_works\国民经济主要指标人均水平.csv",encoding='utf-8-sig')
#print(economy_data)
economy_data.set_index("年份",inplace=True)
print(economy_data.head())
print(economy_data.dtypes)

indicators = [
    ('人均GDP_元', '人均GDP'),
    ('人均可支配收入_元', '人均可支配收入'),
    ('人均消费支出_元', '人均消费支出'),
    ('人均储蓄存款_元', '人均储蓄存款')
]
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()                 # 2×2 平铺，方便用下标遍历

years = economy_data.index.values     # 年份（整数）

for i, (col, title) in enumerate(indicators):
    ax = axes[i]
    # 绘制折线图
    ax.plot(years, economy_data[col].values,
            marker='o', linestyle='-', color='steelblue', linewidth=1.5)
    ax.set_title(title, fontsize=12)
    ax.set_ylabel('元')
    ax.grid(True, linestyle=':', alpha=0.5)
    # X 轴显示所有年份并旋转避免重叠
    ax.set_xticks(years)
    for label in ax.get_xticklabels():
        label.set_rotation(45)

# 总标题
plt.suptitle('国民经济主要指标人均水平变化趋势（2017‑2024）', fontsize=14, y=0.98)
plt.tight_layout()
plt.show()