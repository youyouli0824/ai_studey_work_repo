import matplotlib.pyplot as plt

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据月份
months = [f'{i}月' for i in range(1, 13)]
# 折线产品A的数据
sales_A = [120, 135, 150, 160, 190, 210, 240, 220, 200, 180, 160, 150]
# 折线产品B的数据
sales_B = [80, 95, 110, 130, 140, 150, 160, 170, 190, 210, 230, 250]
# 折线产品C的数据
sales_C = [60, 105, 100, 110, 120, 140, 150, 170, 170, 200, 220, 230]
sales_C = [80, 95, 110, 130, 140, 150, 160, 170, 190, 210, 230, 250]
# 设置画布
plt.figure(figsize=(10, 5))

# 两根折线
plt.plot(months, sales_A, color='blue', marker='o', label='经典款 A 销量')
plt.plot(months, sales_B, color='green', marker='s', ls='--', label='新品款 B 销量')
plt.plot(months, sales_C, color='red', marker='^', ls='-', label='新品款 C 销量')

# 设置标题、x轴、y轴名称
plt.title('产品 A/B/C 全年各月销量趋势对比', fontsize=14)
plt.xlabel('月份')
plt.ylabel('销量 (台)')
plt.legend(loc='best')
# 设置背景
plt.grid(True, alpha=0.4)
plt.show()
