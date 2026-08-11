# 导包
import matplotlib.pyplot as plt
import numpy as np

# 设置字符集防止乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
# 生成等宽数列
x = np.linspace(0, 10, 20)

# 生成画布
plt.figure(figsize=(9, 5))
# 生成折线，设置折线的参数颜色、大小、样式宽度、标记
plt.plot(x, x, color='red', linestyle='-', linewidth=2, marker='o', label="实线 + 圆点 ('-o')")
plt.plot(x, x + 2, color='blue', linestyle='--', linewidth=2, marker='s', markerfacecolor='yellow', label="虚线 + 黄心方块 ('--s')")
plt.plot(x, x + 4, color='green', linestyle='-.', linewidth=2, marker='^', ms=10, label="点划线 + 大三角 ('-.^')")
plt.plot(x, x + 6, color='purple', linestyle=':', linewidth=2.5, marker='*', mec='black', label="点线 + 虚边星号 (':*')")

# 设置标题
plt.title('Matplotlib 常用线型与 Marker 演示', fontsize=14)
# 标记显示位置
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)
plt.show()
