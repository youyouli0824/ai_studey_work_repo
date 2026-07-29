students=[]

def add_student():
    name=input("请输入学生姓名：")
    age=int(input("请输入学生年龄："))
    score=float(input("请输入学生成绩："))
    students.append({"name":name,"age":age,"score":score})
    print(f"成功添加了学生{name}")

def view_students():
    if not students:
        print("没有任何学生信息。")
        return
    print("\n-----学生情况-----")
    for i,student in enumerate(students,1):
        print(f"{i}. 姓名: {student['name']}, 年龄: {student['age']}, 成绩: {student['score']}")

def search_student():
    name = input("请输入要查找的学生姓名: ")
    for student in students:
        if student["name"] == name:
            print(f"找到学生： 姓名: {student['name']}, 年龄: {student['age']}, 成绩: {student['score']}")
            return
        print(f"未找到学生: {name}")

def delete_student():
    name = input("请输入要删除的学生姓名: ")
    for i, student in enumerate(students):
        if student["name"] == name:
            del students[i]
            print(f"已删除学生: {name}")
            return
    print(f"未找到学生: {name}")

while True:
    print("\n===== 学生信息管理系统 =====")
    print("1. 添加学生")
    print("2. 查看学生")
    print("3. 查找学生")
    print("4. 删除学生")
    print("5. 退出系统")
    
    choice = input("请输入选择: ")
    
    if choice == "1":
        add_student()
    elif choice == "2":
        view_students()
    elif choice == "3":
        search_student()
    elif choice == "4":
        delete_student()
    elif choice == "5":
        print("感谢使用学生信息管理系统！")
        break
    else:
        print("输入错误，请重新输入")