file_read=open("练习python文件\example_2.txt","r",encoding="utf-8")
file_write=open("练习python文件\example.txt","a",encoding="utf-8")

lines=file_read.readlines()
file_write.writelines(lines)
file_read.close()
file_write.close()

jpg_read=open(r"练习python文件\Lulu.jpg","rb")
jpg_write=open(r"练习python文件\text.jpg","wb")
info=jpg_read.read()
jpg_write.write(info)
jpg_read.close()
jpg_write.close()
