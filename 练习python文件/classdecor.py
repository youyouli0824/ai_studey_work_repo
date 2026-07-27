class SingletonDec:
    def __init__(self,cls):
        self.cls=cls
        self.instance=None

    def __call__(self,*args,**kwargs):
        if self.instance is None:
            self.instance=self.cls(*args,**kwargs)
        return self.instance
@SingletonDec
class MyClass:
    def __init__(self):
        print("初始化")

db1=MyClass()
db2=MyClass()
print(db1 is db2)  # True          