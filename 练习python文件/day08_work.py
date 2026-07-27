print("\n-----------1--------------")
num=int(input("请输入一个整数："))
if num%2==0:
    print("您输入的整数是偶数")
else:
    print("您输入的整数是奇数")

print("\n-----------2--------------")
year=int(input("请输入一个年份："))
if (year%4==0 and year%100!=0) or (year%400==0):
    print("您输入的年份是闰年")
else:
    print("您输入的年份不是闰年")

print("\n-----------3--------------")
score=int(input("请输入一个成绩："))
if score>=0 and score<=59:
    print("成绩不及格")
elif score>=60 and score<=69:
    print("成绩及格")
elif score>=70 and score<=79:
    print("成绩良好")
elif score>=80 and score<=89:
    print("成绩优秀")
elif score>=90 and score<=100:
    print("成绩非常优秀")
else:
    print("您输入的成绩不在有效范围内，请重新输入")     

print("\n-----------4--------------")
l1=float(input("请输入三角形的一条边长："))
l2=float(input("请输入三角形的另一条边长："))
l3=float(input("请输入三角形的第三条边长："))
if l1**2+l2**2==l3**2 or l1**2+l3**2==l2**2 or l2**2+l3**2==l1**2:
    print("您输入的三角形是直角三角形")
elif l1==l2 or l1==l3 or l2==l3:
    if l1==l2 and l1==l3:
        print("您输入的三角形是等边三角形")
    #判断等腰直角三角形    
    elif (l1==l2 and l1**2+l2**2==l3**2)or (l1==l3 and l1**2+l3**2==l2**2) or (l2==l3 and l2**2+l3**2==l1**2):
        print("您输入的三角形是等腰直角三角形")
    else:
        print("您输入的三角形是等腰三角形")
else:
    print("您输入的三角形是普通三角形")

print("\n-----------5--------------")
H=float(input("请输入你的身高(m)："))
W=float(input("请输入你的体重(kg)："))
BMI=W/(H**2)
print("您的BMI指数是：%.2f"%BMI)
    
