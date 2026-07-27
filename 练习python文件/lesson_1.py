name="liyouyou"
age=18
#格式化输出
print(f"name:{name},age:{age}")
print("\n-------------------------")

ATK=input("请输入你的攻击力：")
def get_ATK(ATK):
    
    try:
        atk_int=int(ATK)
        print(f"你的攻击力是：{int(ATK)}")
    except ValueError:
        ATK=input("攻击力只能是整数，请输入一个整数：")
        get_ATK(ATK)

get_ATK(ATK)

input_str=input("请输入一个字符：")
match input_str:
    case "a":
        print("你输入的是a")
    case "b":
        print("你输入的是b")
    case "c":
        print("你输入的是c")
    case _:
        print("你输入的不是a,b,c中的任何一个")
        
