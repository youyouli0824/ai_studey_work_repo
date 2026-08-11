# 导包
import matplotlib.pyplot as plt

# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 横向标记--产品类型
products = ['手机', '电脑', '平板', '耳机']

# 不同渠道的销售额
online_sales = [500, 300, 250, 400]
offline_sales = [200, 150, 100, 120]

# 设置画布
plt.figure(figsize=(8, 5))

# 绘制下层柱子 (线上)
bars_online = plt.bar(products, online_sales, width=0.4, label='线上渠道销量', color='#1f77b4')

# 绘制上层柱子 (线下)，核心：bottom=online_sales
bars_offline = plt.bar(products, offline_sales, width=0.4, bottom=online_sales, label='线下渠道销量', color='#ff7f0e')

height_phone = height_computer = height_pad = height_head_phone = 0

for bar in bars_online:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height - height/2, f'{height}万', ha='center', va='bottom', fontsize=10)

# for bar in bars_offline:
#     height = bar.get_height()
#     plt.text(bar.get_x() + bar.get_width()/2., height + 300, f'{height}万', ha='center', va='bottom', fontsize=10)

# for bar_online, bar_offline in (bars_online, bars_offline):
#     print(bar_online, bar_offline)

for i in range(len(bars_online)):
    bar_online = bars_online[i]
    bar_offline = bars_offline[i]
    print(bar_online, bar_offline)
    bar_online_height = bar_online.get_height()
    bar_offline_height = bar_offline.get_height();
    height = bar_online_height + bar_offline_height
    plt.text(bar_offline.get_x() + bar_offline.get_width() / 2., bar_online_height + bar_offline_height - bar_offline_height/2, f'{bar_offline_height}万', ha='center', va='bottom',
             fontsize=10)

# 设置标题和标签
plt.title('各产品线上与线下渠道销量堆叠图', fontsize=14)
plt.ylabel('销量 (台)')
plt.legend(loc='upper right')
# 设置背景
plt.grid(axis='y', ls=':', alpha=0.5)
plt.show()
