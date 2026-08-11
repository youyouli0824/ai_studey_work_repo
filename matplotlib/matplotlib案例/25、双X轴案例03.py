# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据
km = [0, 50, 100, 150, 200]
fuel_consumed = [0, 4.2, 8.5, 12.8, 17.0]   # 油耗 (L)

# 生成主坐标系
fig, ax1 = plt.subplots(figsize=(9, 7))

# 设置主坐标系参数
ax1.plot(km, fuel_consumed, color='darkorange', marker='s')
ax1.set_xlabel('行驶里程 (公里/km)', color='darkorange')
ax1.set_ylabel('累计耗油量 (升/L)')

# 实验主坐标生成另一根X轴
ax2 = ax1.twiny()
# 设置上部X轴参数
ax2.set_xlim(ax1.get_xlim())
ax2.set_xticks(km)
# 1 公里 ≈ 0.621371 英里
ax2.set_xticklabels([f'{k * 0.6214:.1f} mi' for k in km])
ax2.set_xlabel('行驶里程 (英里/miles)', color='purple')

# 标题
plt.title('汽车行程油耗双单位参照图', fontsize=14)
plt.show()
