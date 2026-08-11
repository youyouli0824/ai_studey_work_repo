# 导包
import matplotlib.pyplot as plt
import numpy as np

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 模拟一班与二班成绩
class1 = np.random.normal(70, 8, 150)
class2 = np.random.normal(80, 7, 150)
class3 = np.random.normal(90, 7, 150)

# 设置画布
plt.figure(figsize=(9, 5))

# 绘制1班的直方图
plt.hist(class1, bins=15, alpha=0.5, color='blue', label='一班成绩分布', edgecolor='black')
# 绘制2班的直方图
plt.hist(class2, bins=15, alpha=0.5, color='orange', label='二班成绩分布', edgecolor='black')
plt.hist(class3, bins=15, alpha=0.5, color='pink', label='三班成绩分布', edgecolor='black')

# 设置标题、坐标标签
plt.title('一班与二班期末成绩分布重叠对比图', fontsize=14)
plt.xlabel('成绩')
plt.ylabel('频数')
plt.legend(loc='upper left')
# 背景
plt.grid(True, alpha=0.3)
plt.show()
