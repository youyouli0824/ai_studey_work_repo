import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']

provinces=['江苏省', '广东省', '河南省', '山东省', '四川省', '湖北省']
colleges = [168, 165, 156, 156, 134, 130]
colors = ['#3366cc', '#dc3912', '#ff9900', '#109618', '#990099', '#0099c6']

plt.figure(figsize=(9,5))
bars=plt.bar(provinces,colleges,color=colors,width=0.5,edgecolor="black")

for bar in bars:
    h=bar.get_height()
    plt.text(bar.get_x()+bar.get_width()/2.,h+2, f'{h}所', ha='center', va='bottom')

plt.title('全国普通高等学校数量前六省份对比', fontsize=14)
plt.ylabel('高校数量 (所)')
plt.ylim(0, 200)
plt.grid(axis='y', ls='--', alpha=0.5)
plt.show()