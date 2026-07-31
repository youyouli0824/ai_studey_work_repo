
class Rectangle:
    def __init__(self,L=4,S=3):
        self.L=L
        self.S=S

    def Area(self):
        print(f"面积是{(self.L*self.S)}")

    def Perimeter(self):
        print(f"周长是{2*(self.L+self.S)}")

R1=Rectangle(8,6)
R1.Area()
R1.Perimeter()
    
print("=========================")
class Animal:
    def __init__(self,name):
        self.name=name

    def eat(self):
        print("吃东西")

    def show(self):
        print("这是我家的",self.name)

class Dog(Animal):
    def eat(self):
        print(self.name,"在吃骨头")

    def bark(self):
        print("汪汪")

class Cat(Animal):
    def eat(self):
        print(self.name,"吃老鼠")

    def meow(self):
        print("喵")

Animal1=Dog("大狗")
Animal2=Cat("哈吉米")
Animal1.eat()
Animal1.bark()
Animal2.eat()
Animal2.meow()
Animal2.show()

print("=========================")

class Book:
    def __init__(self,name,author,ISBN):
        self.name=name
        self.author=author
        self.ISBN=ISBN

    def __str__(self):
        return f"书名：{self.name},作者：{self.author},ISBN：{self.ISBN}"

class Library:
    def __init__(self):
        self.books=[]

    def add_book(self):
        name=input("请输入书名：")
        author=input("请输入作者姓名：")
        ISBN=input("请输入该书的ISBN：")
        self.books.append(Book(name,author,ISBN))
        print(f"已成功添加《{self.name}》!")

    def search_book(self):
        name=input("请输入你要查找的书名：")
        for book in self.books:
            if book.name==name:
                print(book)
                return
        print(f"没有找到《{name}》")

    def view_books(self):
        if not self.books:
            print("无馆藏")
            return
        for book in self.books:
            print(book)

panel_main=Library()
while True:
    print("\n==图书馆管理系统==")
    print("输入1，添加新书")
    print("输入2，查找指定书")
    print("输入3，看馆藏情况")
    print("输入4，退出系统")
    choice=int(input("========\n请输入选择："))
    if choice==1:
        panel_main.add_book()
    elif choice==2:
        panel_main.search_book()
    elif choice==3:
        panel_main.view_books()
    elif choice==4:
        print("感谢使用，BYEBYE!!")
        break
    else:
        print("输入有误，请重新输入选择") 
        