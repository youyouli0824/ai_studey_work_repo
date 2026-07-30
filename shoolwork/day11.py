print("-----1-----")
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    for i in range(2,n):
        if n % i == 0:
            return False
    return True


while True:
    user_input = input("请输入一个正整数：")
    try:
        num = int(user_input)
        if num <= 0:
            print("请输入一个正整数！")
            continue
        if is_prime(num):
            print(f"{num} 是素数")
        else:
            print(f"{num} 不是素数")
        break
    except ValueError:
        print("输入无效，请输入一个正整数！")

print("\n-----2-----")
try:
    s=input("请输入一句字符串：")
    s_new="".join(reversed(s))
except:
    print("输入的字符串错误")
else:
    print(s_new)

print("\n-----3-----")
list_3=[12,22,33,43,13,56,99,76,57,23,45,67]
list_new = list(filter(lambda x: x > 50, list_3))
print(list_new)

print("\n-----4-----")
def sum_4(n):
    if n == 0:
        return 0
    else:
        return n + sum_4(n - 1)
try:
    sum=sum_4(int(input("输入一个正整数，计算从1开始的累加和：")))
except:
    print("输入有误")
else:
    print(f"和为：{sum}")

print("\n-----5-----")
def count_chars(text):
    letters = 0
    digits = 0
    spaces = 0
    
    for ch in text:
        if ch.isalpha():
            letters += 1
        elif ch.isdigit():
            digits += 1
        elif ch.isspace():
            spaces += 1
    
    return letters, digits, spaces


try:
    text = input("请输入一句话：")
    letter_count, digit_count, space_count = count_chars(text)
        
    print("\n统计结果：")
    print(f"字母: {letter_count} 个")
    print(f"数字: {digit_count} 个")
    print(f"空格: {space_count} 个")
        
except Exception as e:
    print(f"程序出错：{e}")

