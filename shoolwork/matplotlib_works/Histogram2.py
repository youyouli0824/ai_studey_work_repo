import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']

np.random.seed(66666)
math_scores=np.random.normal(115,12,500)

plt.figure(figsize=(9, 5))
count, bins, _ = plt.hist(math_scores, bins=20, density=True,
                           color='#2ca02c',
                           edgecolor='black', alpha=0.6,
                           label='实际成绩密度')
pdf=(1/(12*np.sqrt(2*np.pi)))*np.exp(-0.5*((bins-115)/12)**2)
plt.plot(bins,pdf,color="red",lw=2.5,label="理论正态曲线")
plt.title('新生高考数学成绩分布概率密度曲线拟合', fontsize=14)
plt.xlabel('数学成绩 (分)')
plt.ylabel('概率密度')
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)
plt.show()