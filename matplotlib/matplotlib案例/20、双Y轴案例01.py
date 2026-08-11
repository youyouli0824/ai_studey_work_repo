# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']
# 数据
months = [f'{i}月' for i in range(1, 13)]
rainfall = [20, 35, 55, 80, 120, 180, 240, 210, 130, 70, 40, 25] # 降水量 (mm)
temp = [3, 6, 12, 18, 23, 27, 30, 29, 24, 18, 11, 5]            # 气温 (°C)

# 生成主坐标系ax1
fig, ax1 = plt.subplots(figsize=(10, 5))

# 绘制第一个 Y 轴 (左侧)：降水量柱状图
ax1.bar(months, rainfall, color='#99ccff', alpha=0.7, label='月降水量')
ax1.set_xlabel('月份')
ax1.set_ylabel('降水量 (mm)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# 创建共享 X 轴的第二个 Y 轴 (右侧)
ax2 = ax1.twinx()
ax2.plot(months, temp, color='red', marker='o', lw=2.5, label='平均气温')
ax2.set_ylabel('气温 (°C)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# 标题
plt.title('某地区全年各月降水量与平均气温组合图', fontsize=14)
plt.show()
