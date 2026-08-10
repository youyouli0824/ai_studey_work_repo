from cProfile import label

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

months=["25年9月","10月","11月","12月","26年1月","2月"]
binjiang=[4.8, 4.85, 4.9, 4.92, 4.95, 5.0]
future_city = [3.5, 3.52, 3.6, 3.65, 3.7, 3.75]
wenjiao = [4.2, 4.22, 4.25, 4.28, 4.3, 4.32]
plt.figure(figsize=(9,5))
plt.plot(months,binjiang,color="red",marker="o",label="滨江区")
plt.plot(months,future_city,color="green",marker="s",ls="--",label="未来科技城")
plt.plot(months,wenjiao,color="yellow",marker="^",ls="-.",label="文教区")
plt.title("杭州市三大核心板块二手房均价走势对比",fontsize=14)
plt.xlabel("月份")
plt.ylabel("均价(万元/平方米)")
plt.grid(True,alpha=0.4)
plt.legend(loc='upper left')
plt.show()