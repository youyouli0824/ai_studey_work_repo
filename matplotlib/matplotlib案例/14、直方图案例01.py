# 导包
import matplotlib.pyplot as plt
import numpy as np

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 模拟 200 名学生的成绩，均值为 75，标准差为 10
np.random.seed(100)
# 生成随机数
scores = np.random.normal(75, 10, 200)

# 画布
plt.figure(figsize=(8, 5))
# n==每一个柱子中的元素数量，bins=分界数值，patches=每一个bar组成的容器
n, bins, patches = plt.hist(scores, bins=10, color='#1f77b4', edgecolor='white', alpha=0.85)

# 设置标题、标签
plt.title('期末考试成绩频数分布直方图', fontsize=14)
plt.xlabel('分数区间 (分)')
plt.ylabel('学生人数 (人)')

# 设置背景
plt.grid(axis='y', ls='--', alpha=0.5)
plt.show()
