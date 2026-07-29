'''
基础编程题 
1. 创建列表并操作
创建一个包含10个整数的列表，计算列表的和、平均值、最大值、最小值。
2. 列表去重
给定列表 
[1, 2, 2, 3, 3, 3, 4, 5, 5]，去除重复元素。
3. 字典操作
创建一个字典存储你的个人信息（姓名、年龄、爱好），然后修改年龄并添加新的键值对。
4. 集合运算
给定两个列表 
list1 = [1, 2, 3, 4, 5] 和 list2 = [4, 5, 6, 7, 8]，求它们的交集、并集、差集。
5. 元组操作
创建一个包含5个元素的元组，遍历并打印每个元素。
6. 列表推导式
使用列表推导式生成1到100的所有奇数。
'''
print("--------1--------")
list_1=[12,33,2,13,21,22,78,1,45,67]
sum_1=avg_1=max_1=0
min_1=999
for i in list_1:
    sum_1+=i
    if i>max_1:
        max_1=i
    if i<min_1:
        min_1=i
avg_1=float(sum_1/10)
print(f"和为{sum_1}，平均值为{avg_1}，最大值为{max_1}，最小值为{min_1}。")

print("\n--------2--------")
list_2=[1,2,2,3,3,3,4,5,5]
list_2_new=list(set(list_2))
print(list_2_new)

print("\n--------3--------")
dic_3={"name":"liyouyou","age":"21","like":"fufu"}
dic_3["age"]=20
dic_3["gender"]="plane"
print(dic_3)

print("\n--------4--------")
list_4_1=[1,2,3,4,5]
list_4_2=[4,5,6,7,8]
print("交集：",set(list_4_1)&set(list_4_2))
print("并集：",set(list_4_1)|set(list_4_2))
print("差集：",set(list_4_1)-set(list_4_2))

print("\n--------5--------")
tuple_5=(1,2,3,4,5)
for i in tuple_5:
    print(i,end="\t")
print()

print("\n--------6--------")
list_6=[x for x in range(1,101) if x%2==1]
print(list_6)

'''
中级编程题 
1. 购物清单升级版
在购物清单管理系统中添加"清空清单"和"统计商品数量"功能。
2. 学生成绩统计
创建一个学生成绩字典列表，计算平均分、最高分、最低分，并找出不及格的学生。
3. 二维列表操作
创建一个3×3的矩阵，计算矩阵的对角线元素之和。
4. 字典排序
根据字典的值对字典进行排序。
5. 集合应用
找出两个班级的共同学生、只在第一个班级的学生、只在第二个班级的学生。
6. 深浅拷贝练习
创建一个包含嵌套列表的列表，分别使用赋值、浅拷贝、深拷贝，验证修改的影响。
'''
print("--------n1--------")
list_n1=["西瓜","水杯","辣条"]
while True:
    do=int(input("您现在要做什么？添加商品请按1；删除商品请按2；查看清单请按3；退出系统请按4；清空清单请按5。"))
    if do==1:
        add=input("请输入您需要添加的商品名字：")
        list_n1.append(add)
        print("添加成功！")
    elif do==2:
        dele=input("请输入您需要删除的商品名字：")
        if dele in list_n1:
            list_n1.remove(dele)
            print("成功删除商品！")
        else:
            print("您没有购买该商品。")
    elif do==3:
        print("您的购物清单：")
        for i in list_n1:
            print(i,end="\t")
        print(f"一共有{len(list_n1)}件商品。")
    elif do==5:
        print("已清空购物车！")
        list_n1.clear()
    else:
        print("byebye")
        break

print("\n--------n2--------")
student_n2_list=[{"name":"塞巴斯蒂安","score":96},{"name":"莉亚","score":79},{"name":"文森特","score":56},{"name":"潘姆","score":21}]
max_n2=sum_n2=0
min_n2=100
for i in range(len(student_n2_list)):
    sum_n2+=student_n2_list[i]["score"]
    if max_n2<student_n2_list[i]["score"]:
        max_n2=student_n2_list[i]["score"]
    if min_n2>student_n2_list[i]["score"]:
        min_n2=student_n2_list[i]["score"]
    if student_n2_list[i]["score"]<60:
        print(student_n2_list[i]["name"],"不及格，要好好学习。")
avg_n2=float(sum_n2/len(student_n2_list))
print(f"最高分是{max_n2}，最低分是{min_n2}，平均分是{avg_n2}")

print("\n--------n3--------")
sum_n3=0
list_n3=[[1,2,3],[4,5,6],[7,8,9]]
for i in range(len(list_n3)):
    for j in range(len(list_n3[i])):
        if i==j:
            sum_n3+=list_n3[i][j]
print("对角线累加值为：",sum_n3)

print("\n--------n4--------")
score_dict={"数学":95,"英文":81,"计算机基础":91,"数据结构":58}
sorted_dict = dict(sorted(score_dict.items(), key=lambda x: x[1]))
print(sorted_dict)

print("\n--------n5--------")
class_A_n5={"Sobarsdia","Liya","Amily","Luice","Une"}
class_B_n5={"Liya","Amily","liyouyou","Tom"}
print("AB班的共同学生：",class_A_n5&class_B_n5)
print("A班独有学生：",class_A_n5-class_B_n5)
print("B班独有学生：",class_B_n5-class_A_n5)

print("\n--------n6--------")
import copy
list_n6=[10086,10010]
list_n6_SP=[110,120,119,list_n6]
print("浅拷贝：")
list_test_copy=copy.copy(list_n6_SP)
print("修改前：")
print("list_n6_SP:",list_n6_SP,"\nlist_test_copy:",list_test_copy)
list_test_copy[3][0]=999
print("修改后：")
print("list_n6_SP:",list_n6_SP,"\nlist_test_copy:",list_test_copy)
print("list_n6被改变了！")
list_n6=[10086,10010]
list_n6_SP=[110,120,119,list_n6]
print(">>>>>>>>>>>\n深拷贝：")
list_test_deepcopy=copy.deepcopy(list_n6_SP)
print("修改前：")
print("list_n6_SP:",list_n6_SP,"\nlist_test_deepcopy:",list_test_deepcopy)
list_test_deepcopy[3][0]=999
print("修改后：")
print("list_n6_SP:",list_n6_SP,"\nlist_test_deepcopy:",list_test_deepcopy)
print("list_n6没有被改变！")