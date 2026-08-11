# 导包
import matplotlib.pyplot as plt
import numpy as np

# 设置字符集
plt.rcParams['font.sans-serif'] = ['SimHei']

# 时间，使用range生成
days = np.arange(1, 31)
# 基础价格
base_price = 100 + np.cumsum(np.random.randn(30) * 2)
# 数据上下边界
lower_bound = base_price - 2
upper_bound = base_price + 2

# 设置画布
plt.figure(figsize=(10, 5))
# 绘制折线
plt.plot(days, base_price, color='#1f77b4', lw=2, label='股票基准价格')

# 填充上下置信波动区间--阴影部分
plt.fill_between(days, lower_bound, upper_bound, color='#1f77b4', alpha=0.2, label='价格波动区间')

# 设置标题
plt.title('某股票近 30 天价格曲线及波动置信区间', fontsize=14)
# 设置x、y轴
plt.xlabel('交易日')
plt.ylabel('价格 (元)')
plt.legend(loc='upper left')
# 设置背景
plt.grid(True, alpha=0.3)
plt.show()
