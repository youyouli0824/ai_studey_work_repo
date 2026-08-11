import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建画布
fig = plt.figure(figsize=(8, 5), dpi=100)

# 1. 创建主坐标系 (占据画布绝大部分空间)
ax_main = fig.add_axes([0.1, 0.1, 0.8, 0.8])

# 2. 创建嵌入的小坐标系 (位于主坐标系的右上角)
ax_inset = fig.add_axes([0.55, 0.55, 0.3, 0.3])

# 主坐标系绘制全天气温走势
x = np.linspace(0, 24, 100)
y = 15 + 10 * np.sin(x / 4)
ax_main.plot(x, y, color='blue', label='全天气温趋势')
ax_main.set_title('全天 24 小时气温变化（含局部放大图）', fontsize=14)
ax_main.set_xlabel('时间 (小时)')
ax_main.set_ylabel('气温 (°C)')
ax_main.grid(True, linestyle=':')

# 小坐标系绘制局部峰值放大（如 5~10 点）
x_sub = np.linspace(5, 10, 50)
y_sub = 15 + 10 * np.sin(x_sub / 4)
ax_inset.plot(x_sub, y_sub, color='red', linewidth=2)
ax_inset.set_title('早高峰温升细节', fontsize=10)
ax_inset.grid(True)

plt.show()
