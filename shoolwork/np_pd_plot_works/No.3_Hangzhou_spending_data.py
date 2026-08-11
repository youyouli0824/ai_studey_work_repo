import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']     
plt.rcParams['axes.unicode_minus'] = False 

spending_data = pd.read_csv(r"shoolwork\np_pd_plot_works\杭州市各区县每日旅游消费数据.csv", encoding='utf-8-sig')

avg_person_num = spending_data.groupby("区县")["消费人数_人次"].mean()
print("平均每日消费人数\n", avg_person_num)
avg_spend_num = spending_data.groupby("区县")["消费金额_万元"].mean()
print("平均每日消费金额\n", avg_spend_num)
avg_ruzhulv_num = spending_data.groupby("区县")["酒店入住率_%"].mean()
print("平均酒店入住率\n", avg_ruzhulv_num)

# ---------- 柱状图：各区县平均消费金额排名 ----------
avg_spend_sorted = avg_spend_num.sort_values(ascending=False)
x_labels = avg_spend_sorted.index.tolist()
y_values = avg_spend_sorted.values

plt.figure(figsize=(12, 7))
bars = plt.bar(x_labels, y_values, color='steelblue', edgecolor='black')
plt.xlabel('区县')
plt.ylabel('平均消费金额（万元）')
plt.title('各区县平均消费金额排名')
plt.xticks(rotation=45)

for bar, val in zip(bars, y_values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{val:.1f}', ha='center', va='bottom', fontsize=8)
plt.tight_layout()
plt.show()

# ---------- 箱线图：各区县酒店入住率分布 ----------
# 不要提前创建 figure，直接让 boxplot 创建
spending_data.boxplot(column='酒店入住率_%', by='区县', figsize=(12, 5))
plt.title('各区县酒店入住率分布')
plt.suptitle('')                  # 去除自动副标题
plt.xlabel('区县')
plt.ylabel('酒店入住率（%）')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()