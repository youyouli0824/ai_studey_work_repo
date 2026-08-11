# 导包
import matplotlib.pyplot as plt
import numpy as np
# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 随机数
data = np.random.normal(0, 1, 1000)

# 画布
plt.figure(figsize=(9, 5))

# density=True 绘制概率密度直方图
count, bins, ignored = plt.hist(data, bins=30, density=True, color='#2ca02c', edgecolor='black', alpha=0.6, label='数据密度直方图')

# 叠加理论正态分布密度曲线公式
pdf = (1 / (np.sqrt(2 * np.pi))) * np.exp(-0.5 * bins**2)

# 绘制折线图
plt.plot(bins, pdf, color='red', linewidth=2.5, label='理论正态概率密度曲线')

# 设置标题、标签
plt.title('概率密度直方图与正态分布拟合曲线', fontsize=14)
plt.xlabel('数值')
plt.ylabel('概率密度')
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.show()
