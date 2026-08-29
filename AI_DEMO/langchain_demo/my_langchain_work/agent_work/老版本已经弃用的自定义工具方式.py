from langchain.tools import tool
from numpy import add

@tool
def add_number(a:int,b:int) -> int:
    """add two numbers."""
    return a+b

print(add_number.name)
print(add_number.description)
print(add_number.args)

res=add_number.run({"a":10,"b":20})
print(res)