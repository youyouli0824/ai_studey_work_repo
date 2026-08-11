# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据
categories = ['云服务', '硬件销售', '软件授权', '咨询服务']
revenue = [45, 30, 15, 100]
colors = ['#3366cc', '#dc3912', '#ff9900', '#109618']

# 设置画布
plt.figure(figsize=(7, 7))
# 通过 wedgeprops 控制中心镂空宽度 width=0.4
plt.pie(revenue, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=dict(width=0.4, edgecolor='white'))

# 设置标题
plt.title('科技公司营收来源结构环形图', fontsize=14)
plt.show()
