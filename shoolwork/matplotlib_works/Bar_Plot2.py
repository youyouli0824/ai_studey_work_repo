import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']

provinces = ['广东省', '江苏省', '浙江省']
rev_2024 = [13900, 9900, 8600]
rev_2025 = [14500, 10400, 9100]
x=np.arange(len(provinces))
width=0.35
plt.figure(figsize=(8,5))
plt.bar(x-width/2,rev_2024,width=width,label="2024年",color="#1f77b4")
plt.bar(x + width/2, rev_2025, width=width, label='2025 年', color='#ff7f0e')

plt.title('主要经济大省地方一般公共预算收入对比', fontsize=14)
plt.xticks(x, provinces)
plt.ylabel('财政收入 (亿元)')
plt.legend(loc='upper right')
plt.grid(axis='y', alpha=0.3)
plt.show()