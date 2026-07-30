'''
while True:
    try:
        x=int(input("输入一个数字："))
        break
    except ValueError:
        print("输入的不是数字，请重新输入!")
print(x)        
'''
import sys

try:
    f = open(r"异常处理\myfile.txt")
    s = f.readline()
    i = int(s.strip())
except OSError as err:
    print("OS error: {0}".format(err))
except ValueError:
    print("Could not convert data to an integer.")
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
else:
    print(s,i)
finally:
    print("OVER")