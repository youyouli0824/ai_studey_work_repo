from functools import reduce
def change(a):
    print(id(a))
    a=10
    print(id(a))
    a=18
    print(id(a))

a=2
print(id(a))
change(a)
print("\n--------------\n--------------")
my_list=[1,2,3,4]
def change_list(my_list):
    my_list.append([2,5,6])
    print("函数内部",my_list)
    print(id(my_list))
    return

change_list(my_list)
print("函数外部",my_list)  
print(id(my_list))
print("\n--------------\n--------------")
def printInfo(name,age=18):
    print(f"name:{name},age:{age}")
    return
printInfo(age=28,name="liyouyou")
print("\n--------------\n--------------")
def longerV(v1,v2,*var):
    print(v1)
    print(v2)
    #会以元组形式输出
    print(var)
    print("把元组中的元素遍历输出：")
    for i in var:
        print(i,end="\t")
    return

longerV(1,2,3,4,5,6)
print("\n--------------\n--------------")
def longerV2(v1,v2,**var):
    print("**var会以字典形式输出")
    print(v1)
    print(v2)
    print(var)

longerV2(1,2,a=1,b=2,c=3,list1=[1,2,3,4],tuple1=(1,2,3,4),dict1={"key1":"value1","key2":"value2"})
print("\n--------------\n--------------")
DEF_lamba=lambda a:(a-15)**a
print(DEF_lamba(20))
sum_lamba=lambda v1,v2: v1+v2
print(sum_lamba(10,20))

def func(x):
    return lambda y:y**x
funcx=func(2)
print(funcx(3))

print("\n--------------\n--------------")
numlist=[1,2,3,4,5,6,7,8,9,10]
squ=list(map(lambda x:x**2,numlist))
print(squ)
eve=list(filter(lambda x :x%2==0,numlist))
print(eve)
prod=reduce(lambda x,y:x*y,numlist)
prod2=reduce(lambda x,y:x**y,numlist)
print(prod,prod2)
print("\n--------------\n--------------")
def my_decorator(func):
    def wrapper():
        print("start")
        func()
        print("end")
    return wrapper
@my_decorator
def say():
    print("--call--speaking--")
say()
def my_decorator2(func):
    def wrapper(*args,**kwargs):
        print("start")
        func(*args,**kwargs)
        print("end")
    return wrapper
@my_decorator2
def greet(name,phone):
    print(f"hello {name},my sister's phone number is {phone}")
greet("liyouyou","18888888888")
def repeat(num):
    def my_decorator3(func):
        def wrapper(*args,**kwargs):
            for i in range(num):
                print(f"第{i+1}次调用")
                func(*args,**kwargs)
        return wrapper
    return my_decorator3
@repeat(5)
def speak(salary,days):
    print(f"my salary is {salary},and I work {days} days")
speak(10000,20)

