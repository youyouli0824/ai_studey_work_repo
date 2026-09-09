from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader

#模拟一个文本列表
text_list=["deepseek","qwen"]
document=[Document(text=t,metadata={"name":t}) for t in text_list]
print(document)

#返回文件名
def filename_fn(filename : str):
    return {
        "filename":filename
    }
#读取文件
document2=SimpleDirectoryReader(input_dir=r"C:\shoolwork\my_python_work_myself\Llamalndex\练习\数据",file_metadata=filename_fn).load_data()
print(document2)