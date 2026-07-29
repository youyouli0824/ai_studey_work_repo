import random

print("--------1--------")
n1=int(input("请输入一个正整数："))
sum_1_for=0
for i in range(1,n1+1):
    sum_1_for+=i
print(f"for循环得到结果是{sum_1_for}")
sum_1_while=0
num_1=1
while num_1<=n1:
    sum_1_while+=num_1
    num_1+=1
print(f"while循环得到结果是{sum_1_while}")

print("\n--------2--------")
n2=int(input("请输入一个正整数："))
sum_2_for=1
for i in range(1,n2+1):
    sum_2_for*=i
print(f"for循环得到结果是{sum_2_for}")
sum_2_while=1
num_2=1
while num_2<=n2:
    sum_2_while*=num_2
    num_2+=1
print(f"while循环得到结果是{sum_2_while}")

print("\n--------3--------")
for i in range(1,21):
    if i%2==0:
        print(i,end=" ")

print("\n--------4--------")
List_4=[12,35,8,49,27,56]
max_num_4=0
for i in range(len(List_4)):
    if List_4[i]>max_num_4:
        max_num_4=List_4[i]
print(f"列表里的最大值是{max_num_4}")    
            
print("\n--------5-1--------")
for i in range (1,10):
    for j in range(1,i+1):
        print(f"{j}*{i}={i*j}",end="\t")
    print()

print("\n--------5-2--------")
i=1
while i<10:
    j=1
    while (j<10)&(j<=i):
        print(f"{j}*{i}={i*j}",end="\t")
        j+=1
    print()
    i+=1

print("\n--------6--------")
num_6=int(input("请输入一个大于1的整数："))
is_T=True
for i in range(2,num_6):
    if num_6%i==0:
        is_T=False
if is_T:
    print(f"{num_6}是素数")
else:
    print(f"{num_6}不是素数")

print("\n--------7--------")
for i in range(1,9):
    for j in range(1,9):
        if (i+j)%2==0:
            print("■",end=" ")
        else:
            print("□",end=" ")
    print()

print("\n--------8--------")
print("公鸡每只5文钱，母鸡每只3文钱，小鸡3只1文钱。用100文钱买100只鸡，问公鸡、母鸡、小鸡各多少只？")
print("答：\n购买方式为：")
for x in range(101):
    for y in range(101 - x + 1):
        z = 100 - x - y
        if z % 3 == 0 and 5*x + 3*y + z//3 == 100:
            print(f"可以买公鸡{x}只，母鸡{y}只，小鸡{z}只")

print("\n--------9--------")
list_9=["西瓜","水杯","辣条"]
while True:
    do=int(input("您现在要做什么？添加商品请按1；删除商品请按2；查看清单请按3；退出系统请按4。"))
    if do==1:
        add=input("请输入您需要添加的商品名字：")
        list_9.append(add)
        print("添加成功！")
    elif do==2:
        dele=input("请输入您需要删除的商品名字：")
        if dele in list_9:
            list_9.remove(dele)
            print("成功删除商品！")
        else:
            print("您没有购买该商品。")
    elif do==3:
        print("您的购物清单：")
        for i in list_9:
            print(i,end="\t")
        print(f"一共有{len(list_9)}件商品。")
    else:
        print("byebye")
        break

print("\n--------n1--------")
print("斐波那契数列是从0和1开始，后面的每一项都是前两项之和")
count_n1=int(input("请输入一个正整数："))
a=0
b=1
for i in range(count_n1):
    print(a,end=" ")
    temp=a
    a=b
    b+=temp

print("\n--------n2--------")
sum_up=0
sum_low=0
sum_num=0
sum_other=0
str_n2=input("请随意输入一个字符串：")
for i in str_n2:
    code=ord(i)
    print(i)
    print(code)
    if code>=65 and code<=90:
        sum_up+=1
    elif code>=97 and code<=122:
        sum_low+=1
    elif code>=48 and code<=57:
        sum_num+=1
    else:
        sum_other+=1
print(f"大写字母有{sum_up}个，小写字母有{sum_low}个，数字有{sum_num}个，其他字符有{sum_other}个")

print("\n--------n3--------")
n = int(input("请输入菱形的大小（行数的一半）："))
for i in range(n):
    for j in range(n - i - 1):
        print(" ", end="")
    for j in range(2 * i + 1):
        print("*", end="")
    print()
for i in range(n - 1):
    for j in range(i + 1):
        print(" ", end="")
    for j in range(2 * (n - i - 1) - 1):
        print("*", end="")
    print()

print("\n--------n4--------")
a1 = float(input("请输入首项 a1："))
d = float(input("请输入公差 d："))
n = int(input("请输入项数 n："))

# 使用循环累加
sum_n4 = 0
current = a1
for i in range(n):
    sum_n4 += current
    current += d

print(f"等差数列前 {n} 项的和为：{sum_n4}")

print("\n--------n5--------")
print("猜数字，你有8次机会。")
level=int(input("输入数字，选择难度——1：简单（1-50）；2：中等（1-100）；3：困难（1-200）"))
count_n5=8
if level==1:
    n_n5=random.randint(1,50)
elif level==2:
    n_n5=random.randint(1,100)
elif level==3:
    n_n5=random.randint(1,200)
else:
    print("您选择了不存在的选项。")
while count_n5>0:
    num=int(input(f"您有{count_n5}次机会，请输入猜测的数字："))
    if n_n5==num:
        print(f"猜对了，答案就是{n_n5}！")
        break
    elif n_n5>num:
        print("数据偏小哦。")
    else:
        print("数据偏大哦。")
    count_n5-=1
print(f"随机到的数字是{n_n5}")
