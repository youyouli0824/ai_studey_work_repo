print("\n-------------------------")
List_list=["a","b","c","d","end"]

it = iter(List_list)
for i in it:
    print(i,end="_")

print("\n-------------------------")

while True:
    try:
        print(next(it))
    except StopIteration:
        print("End of iteration")
        break
expression = iter(List_list)
with open("example.txt", "r") as files:
    print("\n-------------------------")
    test_f=files.read()

print(test_f)

print("\n-------------------------")

with open("example.txt", "r") as file1,open("example_2.txt","w") as file2:
    test_f1=file1.read()
    file2.write(test_f1.upper())
with open("example_2.txt", "r") as file3:
    test_f2=file3.read()
print(test_f2)

print("\n-------------------------")
