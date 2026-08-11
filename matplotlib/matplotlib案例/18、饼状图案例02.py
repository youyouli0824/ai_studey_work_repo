# 导包
import matplotlib.pyplot as plt
# 字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 数据
brands = ['品牌A', '品牌B', '品牌C', '品牌D', '其它']
shares = [35, 25, 18, 12, 10]
# 将最大的品牌A (第1个) 向外突出爆破 0.1 距离
explode = [0.05, 0.05, 0.05, 0.05, 0.05]

# 画布
plt.figure(figsize=(7, 7))

# 绘制饼状图
plt.pie(shares, labels=brands, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)

# 设置标题
plt.title('国内手机市场品牌份额 (重点品牌突出显示)', fontsize=14)
plt.show()
