import re

text="电话：123-4567"
pattern=r"\d{3}-\d{4}"
result=re.findall(pattern,text)
print(result)