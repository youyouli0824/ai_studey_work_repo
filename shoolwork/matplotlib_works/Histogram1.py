import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']

np.random.seed(42)
income_data=np.random.normal(6.5,2.0,1000)

plt.figure(figsize=(8,5))
plt.hist(income_data,bins=15,color="#1f77b4",
         edgecolor="white",alpha=0.85)

plt.title("某地区居民人均收入频数分布直方图",fontsize=14)
plt.xlabel('年收入 (万元)')
plt.ylabel('户数 (户)')
plt.grid(axis='y', ls='--', alpha=0.5)
plt.show()