def log_class(cls):
    class Wrapper:
        def __init__(self,*args,**kwargs):
            self.wrapped=cls(*args,**kwargs)
        def __getattr__(self,name):
            return getattr(self.wrapped,name)

        def display(self):
            print("start")
            self.wrapped.display()
            print("end")
    return Wrapper

@log_class
class MyClass:
    def display(self):
        print("This is MyClass display method.")

obj=MyClass()
obj.display()        
        