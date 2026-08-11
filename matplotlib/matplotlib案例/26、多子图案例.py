# 导包
import matplotlib.pyplot as plt

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 生成主坐标系，子图2*2，画布10*7
fig, axes = plt.subplots(2, 2, figsize=(10, 7))

# 子图 1: 折线图
axes[0, 0].plot([1, 2, 3], [4, 5, 6], color='red')
axes[0, 0].set_title('子图 1: 折线图')

# 子图 2: 柱状图
axes[0, 1].bar(['A', 'B'], [10, 20], color='blue')
axes[0, 1].set_title('子图 2: 柱状图')

# 子图 3: 散点图
axes[1, 0].scatter([1, 2, 3], [3, 1, 5], color='green')
axes[1, 0].set_title('子图 3: 散点图')

# 子图 4: 饼图
axes[1, 1].pie([30, 70], labels=['X', 'Y'], autopct='%1.0f%%')
axes[1, 1].set_title('子图 4: 饼图')

# 设置标题
plt.tight_layout() # 自动紧凑排列

# 保存为高清 PNG 图片 (注意：savefig 必须写在 plt.show() 之前，否则会保存一张空白图！)
plt.savefig('output_chart.png', dpi=300, bbox_inches='tight', transparent=False)

plt.show()
