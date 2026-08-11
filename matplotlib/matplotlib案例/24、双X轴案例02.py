# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据
months = [1, 2, 3, 4, 5, 6]
values = [10, 25, 18, 30, 45, 50]
date_recount = ['150天前', '120天前', '90天前', '60天前', '30天前', '当前']

# 生成主坐标系
fig, ax1 = plt.subplots(figsize=(9, 7))

# 主坐标设置参数
ax1.plot(months, values, color='green', marker='^')
ax1.set_xlabel('2026年 相对月份 (1~6月)')
ax1.set_ylabel('指标数值')

# 使用主坐标系生成另一根X轴
ax2 = ax1.twiny()

# 设置上部X轴的参数
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(months)
ax2.set_xticklabels(date_recount)
ax2.set_xlabel('倒计时里程碑节点')

# 标题
plt.title('业务指标按月份及里程碑倒计时对照图', fontsize=14)
plt.show()
