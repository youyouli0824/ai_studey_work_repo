import matplotlib.pyplot as plt
import numpy as np

# 1. 基础配置 (防中文乱码)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 2. 准备数据 ( 2026年 1~5 月某产品销售额 )
months = ['1月', '2月', '3月', '4月', '5月']
sales = np.array([15, 28, 35, 22, 42])
# 3. 创建画布并绘制折线图
plt.figure(figsize=(8, 4.5), dpi=100) # 创建 8x4.5 英寸、100 DPI 的画布
plt.plot(months, np.abs(sales-np.amax(sales)+np.amin(sales))+12, marker='o', color="#d4212d", linewidth=2, label='销售额(万元)')
plt.plot(months, (sales+32)/3, marker='^', color="#6c1be5", linewidth=2, label='销售额(万元)')
plt.plot(months, np.sqrt(((sales+32)*3*2.5)+28), marker='s', color="#15c735", linewidth=2, label='销售额(万元)')
# 4. 添加修饰
plt.title('2026 年 1~5 月产品销售额走势图', fontsize=14, pad=15)
plt.xlabel('月份', fontsize=12)
plt.ylabel('金额 (万元)', fontsize=12)
plt.grid(True, linestyle='-.', alpha=0.5)
plt.legend(loc='upper left')
# 5. 展示图形 (在 PyCharm 中会弹出一个独立的交互窗口)
plt.show()