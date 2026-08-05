import numpy as np
arr_a=np.array([1,2,3,4,5,6])
arr_b=np.array([10,20,30,40,50,60])
result=arr_a+arr_b
print(result)
print("===========")
arr_c=np.array([[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12],
               [43,21,4,5]])
print(arr_c.ndim)#维度
print(arr_c.shape)#几行几列
print(arr_c.size)#元素总数
print(arr_c.dtype)#元素类型
print("==========")
a=np.array([[1],
           [2],
           [3]])
b=np.array([10,20,30,40])
print(a+b)
A = np.array([[1, 2],
              [3, 4]])
B = np.array([[5, 6],
              [7, 8]])
print(A @ B)
print("==========")
arr_d = np.array([[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 9]])
print(np.std(arr_d))
print(np.sum(arr_d,axis=0))
print(np.sum(arr_d,axis=1))
