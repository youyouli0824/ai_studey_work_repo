import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']

income = [38, 42, 55, 60, 78, 35, 32, 48, 52, 70]
expenditure = [24, 28, 36, 39, 48, 22, 21, 31, 34, 43]

plt.figure(figsize=(8, 5))
plt.scatter(income, expenditure, color='#1f77b4', s=70, edgecolors='red', alpha=0.75)

plt.title('各省居民人均可支配收入与消费支出散点图', fontsize=14)
plt.xlabel('人均可支配收入 (千元)')
plt.ylabel('人均消费支出 (千元)')
plt.grid(True, ls='--', alpha=0.5)
plt.show()