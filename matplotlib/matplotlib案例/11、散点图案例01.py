# 导包
import matplotlib.pyplot as plt
import numpy as np

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 模拟 50 名大一新生的身高 (cm) 与体重 (kg)
# 设置随机数种子，每一次生成相同的随机数
np.random.seed(42)
# 身高数据
heights = np.random.normal(170, 6, 50)
# 体重数据
weights = heights * 0.65 - 35 + np.random.normal(0, 3, 50)

# 设置画布
plt.figure(figsize=(8, 5))

# 绘制散点图
plt.scatter(heights, weights, color='#1f77b4', alpha=0.8, edgecolors='black', s=20)

# 设置标题和标签
plt.title('大一新生（男生）身高与体重分布相关性散点图', fontsize=14)
plt.xlabel('身高 (cm)')
plt.ylabel('体重 (kg)')
# 设置背景
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()
