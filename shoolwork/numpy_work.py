#1
import numpy as np
#2
print("=====")
arr1=np.array([10,20,30,40,50])
arr2=np.arange(0,10,2)
arr3=np.zeros((3,4))
arr4=np.random.randint(0,100,(2,3))
#3
print("=====")
arr5=np.array([[1,2,3,4],[5,6,7,8],[9,10,11,12]])
print(arr5.ndim,"维度",arr5.shape,"几行几列",arr5.size,"元素总数",arr5.dtype,"元素类型")
#4
print("======")
arr6 = np.array([10, 20, 30, 40, 50, 60, 70, 80])
print(arr6[0])
print(arr6[-1])
print(arr6[2:5])
print(arr6[::2])
print(arr6[::-1])
#5
print("=====")
arr7=np.arange(12).reshape(3,4)
print(arr7)
print(arr7[1,2])
print(arr7[0])
print(arr7[:,1])
print(arr7[0:2,0:2])
#6
print("=====")
arr8 = np.array([85, 92, 45, 78, 55, 95, 60, 38])
print(arr8[arr8>=60])
print(arr8[arr8>=80])
print(arr8[(arr8>=60)&(arr8<=80)])
print(len(arr8[arr8<60]))
#7
print("=====")
a=np.array([1,2,3,4])
b=np.array([10,20,30,40])
print(a+b)
print(a*b)
print(b/a)
print(a+100)
print(a**2)
#8
print("=====")
weight=np.array([55,70,85])
height=np.array([1.6,1.75,1.8])
BMI=weight/(height**2)
r=[]
for i in BMI:
    if i<18.5:
        r.append("偏廋")
    elif i<24 and i>=18.5:
        r.append("正常")
    elif i>=24:
        r.append("偏胖")
    else:
        r.append("错误")
print(r)
#9
print("=====")
scores = np.array([[85, 92, 78, 88],
                   [76, 81, 95, 70],
                   [90, 85, 72, 95]])
print(scores-[60,60,60,60])
print(scores+[5,5,5,5])
mean=np.mean(scores,axis=0)
std=np.std(scores,axis=0)
normalized=(scores-mean)/std
print(normalized)
#10
print("=====")
import time
t1=time.time()
list1=list(range(1000000))
t2=time.time()
print(t2-t1)
t3=time.time()
list2=np.arange(1000000)
t4=time.time()
print(t4-t3)
t5=time.time()
sum1=sum(list1)
t6=time.time()
print(sum1,t6-t5)
t7=time.time()
sum2=np.sum(list1)
t8=time.time()
print(sum2,t8-t7)
print((t2-t1)/(t4-t3))