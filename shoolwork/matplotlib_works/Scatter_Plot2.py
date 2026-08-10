import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']

colleges = np.array([12, 25, 35, 45, 60, 80, 95])
research_funds = colleges * 3.5 + np.random.normal(0, 10, 7)
innovation_index = [60, 68, 72, 78, 85, 90, 96]

plt.figure(figsize=(9, 5))
sc = plt.scatter(colleges, research_funds,
                  c=innovation_index, cmap='viridis',
                    s=100, edgecolors='gray')
cbar = plt.colorbar(sc)
cbar.set_label('城市创新满意度指数')

plt.title('城市高校数量 vs 科研经费 (颜色映射创新指数)', fontsize=14)
plt.xlabel('高校数量 (所)')
plt.ylabel('科研经费 (亿元)')
plt.grid(True, alpha=0.3)
plt.show()