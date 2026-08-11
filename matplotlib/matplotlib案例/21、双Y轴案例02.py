# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据
# x轴年份
years = ['2021年', '2022年', '2023年', '2024年', '2025年']
# 左侧Y轴的销售额
revenue = [1000, 1300, 1700, 2200, 3000]
# 右侧Y轴的增速
growth = [15.0, 30.0, 30.7, 29.4, 36.3] # 增速 (%)

# 生成主坐标
fig, ax1 = plt.subplots(figsize=(9, 5))

# 主坐标系设置左侧Y轴参数和
ax1.bar(years, revenue, color='#1f77b4', width=0.4, label='营业收入')
ax1.set_ylabel('营业收入 (万元)', color='#1f77b4')
ax1.set_xlabel('年份')

# 使用主坐标生成右侧Y轴
ax2 = ax1.twinx()
# 设置右侧Y轴参数
ax2.plot(years, growth, color='#ff7f0e', marker='D', lw=2, label='同比增速')
ax2.set_ylabel('增速 (%)', color='#ff7f0e')

# 设置标题
plt.title('公司历年营业收入及同比增速柱线组合图', fontsize=14)
plt.show()
