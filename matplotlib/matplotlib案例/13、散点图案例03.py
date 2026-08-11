# 导包
import matplotlib.pyplot as plt

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据
cities = ['城市A', '城市B', '城市C', '城市D', '城市E', '城市F']
gdp = [12000, 8500, 15000, 6000, 4500, 9800] # GDP (亿元)
income = [8.5, 6.2, 9.8, 5.1, 4.5, 7.3]      # 人均收入 (万元)
population = [1500, 900, 2200, 600, 400, 1100] # 人口 (万人)，控制气泡大小

# 设置画布
plt.figure(figsize=(9, 5.5))

# 将人口映射为气泡的大小 s (乘以 0.5 调整视觉比例)
plt.scatter(gdp, income, s=[p for p in population], color='#ff7f0e', alpha=0.6, edgecolors='red', linewidth=1.5)

# 标注城市名字
for i, txt in enumerate(cities):
    plt.annotate(f'{txt}\n({population[i]}万人)', (gdp[i], income[i]), ha='center', va='center', fontsize=9)

# 设置标题、标签
plt.title('各城市 GDP vs 人均收入气泡图 (气泡大小表示人口数量)', fontsize=14)
plt.xlabel('城市 GDP (亿元)')
plt.ylabel('人均年收入 (万元)')

# 设置背景
plt.grid(True, ls=':', alpha=0.5)
plt.show()
