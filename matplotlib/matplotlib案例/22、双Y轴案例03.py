# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']
# 数据：周、销售额、广告费用
weeks = [f'W{i}' for i in range(1, 9)]
sales = [500, 520, 680, 800, 850, 920, 1100, 1250]
ad_cost = [10, 12, 25, 30, 28, 35, 50, 60]

# 生成主坐标系
fig, ax1 = plt.subplots(figsize=(9, 5))

# 绘制第一根折线图
line1 = ax1.plot(weeks, sales, color='green', marker='o', label='周销量')
# 设置Y轴标签信息
ax1.set_ylabel('销量 (件)', color='green')
# 使用主坐标生成第二根Y轴
ax2 = ax1.twinx()
# 绘制第二条折线图
line2 = ax2.plot(weeks, ad_cost, color='purple', marker='s', ls='--', label='广告费用')
ax2.set_ylabel('广告费用 (万元)', color='purple')

# 合并两轴的图例
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')

# 设置标题
plt.title('产品周销量与广告费用增长趋势图', fontsize=14)
plt.show()
