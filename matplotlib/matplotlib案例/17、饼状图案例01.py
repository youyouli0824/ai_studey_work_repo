# 导包
import matplotlib.pyplot as plt
# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 准备数据
expenses = ['餐饮', '购物', '娱乐', '学习书籍', '其它']
amounts = [1200, 500, 300, 200, 150]
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']

# 设置画布
plt.figure(figsize=(7, 7))

# 绘制饼状图
plt.pie(amounts, labels=expenses, autopct='%1.1f%%', startangle=90, colors=colors)

# 设置标题
plt.title('大学生月度消费开支占比结构图', fontsize=14)
plt.show()
