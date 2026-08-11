# 导包
import matplotlib.pyplot as plt
# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# x轴数据，列表，范围0~24，步长为2
hours = [f'{h}:00' for h in range(0, 24, 2)]
# y轴数据，温度，靠近中午前后温度较高
temperatures = [14, 13, 12, 11, 15, 20, 24, 26, 25, 21, 18, 15]

# 设置画图
plt.figure(figsize=(10, 4.5))
# 绘制折线图，数据源，折线颜色，标记样式，线宽
plt.plot(hours, temperatures, color='#d62728', marker='o', lw=2)
# 设置标题
plt.title('某市 24 小时连续气温监控曲线', fontsize=14)
# x、y轴名称
plt.xlabel('时间点')
plt.ylabel('气温 (°C)')
# 设置背景网格
plt.grid(True, ls=':', alpha=0.6)
plt.show()
