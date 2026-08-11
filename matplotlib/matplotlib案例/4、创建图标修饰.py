import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 模拟某科技公司 2025 年 4 个季度的营收与利润 (单位: 万元)
quarters = ['2025-Q1', '2025-Q2', '2025-Q3', '2025-Q4']
revenue = [1200, 1800, 2100, 2600]
profit = [300, 500, 650, 900]

# 设置画布参数
plt.figure(figsize=(10, 5.5), dpi=100, facecolor='#fafafa')

# 绘制两条线
plt.plot(quarters, revenue, color='#1f77b4', ls='-', lw=2.5, marker='o', ms=8, label='营业收入')
plt.plot(quarters, profit, color='#ff7f0e', ls='--', lw=2.5, marker='s', ms=8, label='净利润')

# 1. 标题与标签美化
plt.title('某科技股份公司 2025 年度财务表现趋势图', fontsize=16, fontweight='bold', pad=20, color='#333333')
# 设置x轴的标记
plt.xlabel('季度', fontsize=12, labelpad=10)
# 设置Y轴的标记
plt.ylabel('金额 (万元)', fontsize=12, labelpad=10)

# 2. 坐标轴范围与刻度美化
plt.ylim(0, 3000)
plt.yticks(np.arange(0, 3500, 500))     # 0 到 3000 每隔 500 标注一个刻度

# 3. 网格线设置 (仅保留 Y 轴水平网格)
plt.grid(visible=True, axis='both', linestyle='--', alpha=0.8, color='#cccccc')

# 4. 图例美化 (右上角，带阴影和白底边框)
plt.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='#cccccc', shadow=True, fontsize=11)

# 5. 在数据点上标注具体数值 (plt.text 增强体验)
for i in range(len(quarters)):
    plt.text(quarters[i], revenue[i] + 80, f'{revenue[i]}万', ha='center', va='bottom', fontsize=10, color='#1f77b4')
    plt.text(quarters[i], profit[i] + 80, f'{profit[i]}万', ha='center', va='bottom', fontsize=10, color='#ff7f0e')

plt.tight_layout() # 自动调整边距防止标签被遮挡
plt.show()
