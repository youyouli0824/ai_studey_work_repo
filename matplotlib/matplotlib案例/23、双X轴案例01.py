# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 底部 X 轴：摄氏度
celsius = [0, 10, 20, 30, 40]
# 对应的 Y 轴数据 (水蒸气饱和压 kPA)
pressure = [0.61, 1.23, 2.34, 4.24, 7.38]
# 基于摄氏度计算出华氏度
fahrenheit = [c * 1.8 + 32 for c in celsius]

# 生成主坐标系
fig, ax1 = plt.subplots(figsize=(9, 5))

# 主坐标设置参数
ax1.plot(celsius, pressure, 'b-o')
ax1.set_xlabel('温度 (°C)', color='blue')
ax1.set_ylabel('水蒸气饱和压 (kPa)')

# 顶部 X 轴：共享 Y 轴，显示对应的华氏度 F = C * 1.8 + 32
ax2 = ax1.twiny()

# 设置上部X轴的参数
ax2.set_xlim(ax1.get_xlim()) # 保持坐标范围对齐
ax2.set_xticks(celsius)
ax2.set_xticklabels([f'{f:.1f}°F' for f in fahrenheit])
ax2.set_xlabel('温度 (°F)', color='red')

# 标题
plt.title('温度与水蒸气压关系 (双 X 轴显示)', fontsize=14)
plt.show()
