import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']

months = [f'{i}月' for i in range(1, 13)]
price = np.array([22, 21.5, 23, 25, 27, 28, 26.5, 25, 24, 23.5, 24.5, 26])
lower = price - 2.0
upper = price + 2.0
plt.figure(figsize=(10,4.5))
plt.plot(months, price, color='#d62728', lw=2, marker='o', label='猪肉月度平均价格')
plt.plot(months,lower,upper,color="#d62728",alpha=0.2,label="价格合理波动区间")

plt.title('全国猪肉月度平均价格及波动范围', fontsize=14)
plt.xlabel('月份')
plt.ylabel('价格 (元/公斤)')
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3)
plt.show()