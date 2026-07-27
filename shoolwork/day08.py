print("--------1--------")
count=0
for i in range(1,1001):
    if i%3==2 and i%5==3 and i%7==2:
        count+=1
        print(i,end=" ")
        if count%5==0:
            print()

print("\n--------2--------")
sum_2=0
for i in range(1,102,2):
    if i%4==1:
        sum_2+=i
    else:
        sum_2-=i
print(f"和为{sum_2}")

print("\n--------3--------")
while True:
    inputINT=int(input("输入一个整数，1——学习Python，2——睡觉，3——退出程序："))
    if inputINT==1:
        print("学习Python")
    elif inputINT==2:
        print("睡觉")
    elif inputINT==3:
        print("程序结束！")
        break
    else:
        print("无效输入，请重新输入！")
        continue

print("\n--------4--------") 
sum_4=0
for i in range(2,101,2):
    sum_4+=i
print("100以内的偶数和为",sum_4)

print("\n--------5--------")
num_head=int(input("请输入笼子里有几个头："))
num_leg=int(input("请输入笼子里有几条腿："))
haveAnswer=False
for chickens_num in range(num_head+1):
    rabbits_num=num_head-chickens_num
    if 2*chickens_num+4*rabbits_num == num_leg:
        print(f"小鸡有{chickens_num}只，小兔有{rabbits_num}只。")
        haveAnswer=True
        break
if haveAnswer==False:
    print("输入的数据无解。")

print("\n--------6--------")
for num in range(100,1000):
    hun=num//100
    ten=(num//10)%10
    one=num%10
    if num ==hun**3+ten**3+one**3:
        print(f"{num}是水仙花数。")

print("\n--------7--------")
print("小写 a-z：")
for i in range(ord('a'), ord('z') + 1):
    print(chr(i), end=" ")
print()
print("大写 Z-A：")
for i in range(ord('Z'), ord('A') - 1, -1):
    print(chr(i), end=" ")

print("\n--------8--------")
sum_7=0
for num in range(1,101):
    if num%2==1:
        sum_7+=(1/num)
    else:
        sum_7-=(1/num)
print(f"和为{sum_7}")

print("--------9--------")
count_9=0
for num in range(20,81):
    if num%3==0:
        print(num,end=" ")
        count_9+=1
        if count_9%5==0:
            print()

print("\n--------10--------")
count_10=0
print("1000-2000年间，闰年有：")
for years in range(1000,2001):
    if (years%4==0 and years%100!=0) or years%400==0:
        print(years,end=" ")
        count_10+=1
        if count_10%4==0:
            print()

print("\n--------难1--------")
days=10
num_end=1
while True:
    days-=1
    if days<0:
        break
    num_end=(num_end+1)*2
    print(f"第{days}天，有{num_end}个桃子")

print("\n--------难2--------")
boom=0
h=200
sumH=0
while True:
    boom+=1
    if boom==1:
        sumH+=h
        h=h/2
    elif boom>1 and boom<10:
        sumH+=(h*2)
        h=h/2
    elif boom==10:
        sumH+=(h*2)
        print(f"到第十次落地了，经历了{sumH}米")
        break

print("\n--------难3--------")
count_n3=0
water=35
while water<150:
    count_n3+=1
    water+=12
print(f"花了{count_n3}天，装满了")
