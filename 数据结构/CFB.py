for i in range (1,10):
    for j in range(1,i+1):
        print(f"{j}*{i}={i*j}",end="\t")
    print()

print("-------------------------------------")

i=1
while i<10:
    j=1
    while (j<10)&(j<=i):
        print(f"{j}*{i}={i*j}",end="\t")
        j+=1
    print()
    i+=1
        
print("------------------------------------")