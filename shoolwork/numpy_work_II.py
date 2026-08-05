from tkinter.filedialog import LoadFileDialog

import numpy as np
print("===1===")
arr1 =np.arange(24)
print(arr1.reshape(3,8))
print(arr1.reshape(2,3,4))
arr1_1=arr1.reshape(4,-1)
print(arr1_1)
print(arr1.size==arr1_1.size)


print("===2===")
arr2=np.array([[1,2,3],
               [4,5,6]])
arr2_t=arr2.T
print(arr2_t.shape)
print(arr2.flatten())
print(arr2.ravel())
print(arr2)
arr2_f=arr2.flatten()
arr2_f[0]=100
print(f"arr2_f:{arr2_f}\narr2:{arr2}")
print("说明flatten（）是副本")
arr2_r=arr2.ravel()
arr2_r[0]=200
print(f"arr2_r:{arr2_r}\narr2:{arr2}")
print("说明ravel（）是视图")


print("===3===")
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
V=np.vstack([A,B])
print(V.shape)
VC=np.concatenate([A,B],axis=0)
print(VC)
print("垂直合并要求两个数组的什么维度必须相同？")
print("答案：列数必须相同")


print("===4===")
H=np.hstack([A,B])
HC=np.concatenate([A,B],axis=1)
a=np.array([1,2,3])
b=np.array([4,5,6])
Hab=np.hstack([a,b])
print(Hab)


print("===5===")
arr5=np.arange(12).reshape(3,4)
l,r=np.hsplit(arr5,2)
print(l)
print(r)
t,m,b=np.vsplit(arr5,3)
arr5_1D=arr5.flatten()
arr_split=np.split(arr5_1D,[3,7])
print(arr_split)
print(np.split(np.arange(10),[3,7]))


print("===6===")
data=np.array([[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]])
np.savetxt("shoolwork/data.csv",data,delimiter=","
        ,fmt="%d",header="a,b,c,d",
        comments="")
loaded=np.loadtxt("shoolwork/data.csv",delimiter=",",
                  skiprows=1)
print(loaded)
print(loaded==data)


print("===7===")
np.save("shoolwork/data.npy",data)
load2=np.load("shoolwork/data.npy")
a7=np.array([2,2,3,3])
b7=np.array([3,3,2,2])
np.savez("shoolwork/arrays.npz",a7=a7,b7=b7)
data7=np.load("shoolwork/arrays.npz")
print(data7['a7'],data7['b7'])


print("===8===")
data8=np.arange(60).reshape(20,3)
dataA,dataB=np.split(data8,[16])
print(dataA.shape,dataB.shape)
print(np.mean(dataA,axis=0),np.mean(dataB,axis=0))


print("===9===")
class1=np.array([[85,92,78],
                 [76,81,88],
                 [90,85,72]])
class2=np.array([[65,70,80],
                 [88,95,78]])
class_all=np.vstack([class1,class2])
avg_scores=np.mean(class_all,axis=1)
#np.argsort()函数返回的是数组值从小到大的索引值
#按平均分从高到低对学生排序，并打印排名
avg_scores_desc = avg_scores[np.argsort(avg_scores)[::-1]]
print(np.argsort(avg_scores)[::-1])
for i in range(len(np.argsort(avg_scores_desc))):
    print(f"第{i+1}名的平均分是{avg_scores_desc[i]}")
np.savetxt("shoolwork/class_all_scores.csv",
           class_all,delimiter=",",
           fmt="%d",header="3D_Math,Unity,C#"
           ,comments="")


print("===10===")
tip=["A","B","C"]
sales=np.array([[120,80,200],
                [150,95,180],
                [180,110,220],
                [200,130,250]])
print(f"年销售额：{np.sum(sales)}")
tip_sales=np.sum(sales,axis=0)
print(f"各类型销售额：{tip_sales}")
Q_sales=np.sum(sales,axis=1)
print(f"每个季度的销售额：{Q_sales}")
print(f"第四季度相比第一季度的增长率：{(Q_sales[3]-Q_sales[0])/Q_sales[0]*100}%")
tip_max_index=np.argmax(sales,axis=1)
print(f"每个季度销售额最高的类型：{[tip[i] for i in tip_max_index]}")
print(f"各季度累计销售额：{np.cumsum(Q_sales)}")
