# 导包
import matplotlib.pyplot as plt

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# x轴的坐标数据
depts = ['华东部', '华北区', '华南部', '华中区', '西南区', '西北区']
# 营业额，柱状图柱子的高度数据
performance = [450, 320, 580, 550, 290, 180]
# 每一根柱子的颜色
colors = ['#1f77b4', '#aec7e8', '#fff70e', '#ff7f0e', '#ffbb78', '#2ca02c']

# 设置画布
plt.figure(figsize=(8, 5))

# 柱子对象，柱子的数量和x==y的数量相同，width=0.5表示默认宽度减半
bars = plt.bar(depts, performance, color=colors, width=0.3, edgecolor='black', alpha=0.85)

# print("柱子的数量：", len(bars))

# 在每个柱子顶部自动添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 10, f'{height}万', ha='center', va='bottom', fontsize=10)

# 设置标题
plt.title('2025 年第四季度各区域部门销售业绩对比', fontsize=14)
# 设置y轴的标题
plt.ylabel('销售额 (万元)')
plt.ylim(0, 700)
# 背景
plt.grid(axis='y', ls='--', alpha=0.5)
plt.show()
