# 导包，按照行业惯例设置简称为plt
import matplotlib.pyplot as plt

# 1. 基础配置 (防中文乱码)，模块默认不支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 2. 准备数据 ( 2026年 1~5 月某产品销售额 )
# 月份，x轴数据
months = ['1月', '2月', '3月', '4月', '5月']
# 销售额，y轴数据
sales = [15, 28, 35, 22, 42]

# 3. 创建画布并绘制折线图
plt.figure(figsize=(8, 4.5), dpi=100)  # 创建 8x4.5 英寸、100 DPI 的画布

# 使用plot方法绘制折线图，图中的数据第一个month显示在x轴，第二个数据sales显示在y轴
# marker表示标记，o==圆形，s==方形，^==表示三角形
# color表示颜色，使用RGB方式表示：R==Red，G==Green，B==Blue，范围是00~FF
# linewidth表示线的宽度
# 图标左上角对的标签：upper left
plt.plot(months, sales, marker='^', color='#0000FF', linewidth=2, label='月度销售额 (万元)')

# 4. 添加修饰
# 整个图表的标题，fontsize表示字体大小
plt.title('2026 年 1~5 月产品销售额走势图', fontsize=14, pad=15)
# 设置x轴的标记
plt.xlabel('月份', fontsize=12)
# 设置y轴的标记
plt.ylabel('金额 (万元)', fontsize=12)
# 背景网格线,-表示实线，--表示虚线，:点，-。组合
plt.grid(True, linestyle='-.', alpha=0.5)
# label显示的位置
plt.legend(loc='upper left')

# 5. 展示图形 (在 PyCharm 中会弹出一个独立的交互窗口)
plt.show()
