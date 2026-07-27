print("--------1--------")
count=0
for i in range(1,1001):
    if i%3==2 and i%5==3 and i%7==2:
        count+=1
        print(i,end=" ")
        if count%5==0:
            print()

print("\n--------2--------")
sum=0
for i in range(1,102,2):
    if i%4==1:
        sum+=i
    else:
        sum-=i
print(sum)

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
print(sum_4)

print("\n--------5--------")
num_head=int(input("请输入笼子里有几个头："))
num_foot=int(input("请输入笼子里有几条腿："))
sum_cuk=0
sum_rab=0

