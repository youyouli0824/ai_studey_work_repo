import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig=plt.figure(figsize=(10,5),dpi=100,facecolor='#f5f5f5',
               edgecolor='black')
plt.bar([1,2,3],[4,5,6])
plt.title("画布参数")
plt.show()
