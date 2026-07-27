score=int(input("请输入一个成绩："))
s=score//10
match s:
    case 6:
        print("成绩及格")
        
    case 7:
        print("成绩中等")
        
    case 8:
        print("成绩良好")
        
    case 9 | 10:
        print("成绩优秀") 

    case s if (s<6)&(s>=0):
        print("成绩不及格")

    case _:
        print("您输入的成绩不在有效范围内，请重新输入")     
    