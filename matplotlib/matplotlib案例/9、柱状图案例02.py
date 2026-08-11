# 导包
import matplotlib.pyplot as plt
import numpy as np

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# x轴横向的部门数据
depts = ['2021年', '2022年', '2023年', '2024年', '2025年']

# 多个部门的销售额
y2021 = [200, 350, 220, 160, 160]
y2022 = [200, 350, 220, 160, 160]
y2023 = [200, 350, 220, 160, 160]
y2024 = [300, 450, 200, 180, 160]
y2025 = [420, 500, 280, 220, 160]

# 求解 X 轴柱子的偏移位置
x = np.arange(len(depts))   # [0, 1, 2, 3]
width = 0.15     # 单个柱子的宽度

# 设置画布
plt.figure(figsize=(19, 10))

# 第一组柱子左移 width，第二组柱子不动，第三组柱子右移 width
plt.bar(x - width*2, y2021, width=width, label='2021 年', color='#52b7d2')
plt.bar(x - width, y2022, width=width, label='2022 年', color='#68b9d2')
plt.bar(x, y2023, width=width, label='2023 年', color='#f6d89a')
plt.bar(x + width, y2024, width=width, label='2024 年', color='#87f1a4')
plt.bar(x + width*2, y2025, width=width, label='2025 年', color='#8a31d4')

# 设置标题、标签
plt.title('各部门 2021--2025 年薪资对比', fontsize=14)
plt.xlabel('部门')
plt.ylabel('预算金额 (万元)')
plt.xticks(x, depts) # 刻度替换为中文部门名称
plt.legend(loc='upper left')

# 设置背景
plt.grid(axis='y', alpha=0.3)
plt.show()
