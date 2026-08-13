from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI(title="Pydantic 请求体示例")

#定义数据模型
class BookCreate(BaseModel):
    title:str
    author:str
    price:float
    is_published:bool=True
    description:Optional[str]=None

# 2. 在路径操作函数中将模型作为参数声明
@app.post("/books",
          summary="创建新图书",
          status_code=201,
          tags=["图书管理"])
def create_book(book:BookCreate):
    """
    当函数参数被声明为 BaseModel 的子类时，
    FastAPI 会自动执行以下 4 步操作:
    1. 从请求体中读取 JSON 数据
    2. 将 JSON 数据转换为对应的 Python 数据类型
    3. 校验数据格式是否符合类型定义 (如 price 是否为数字)
    4. 将数据封装进 book 对象中供后续代码使用
    """
    print(f"接收到图书:{book.title},价格:{book.price}")
    book_dict=book.model_dump()#转化成字典
    book_dict["id"]=101

    return {
        "code":200,
        "message":"图书创建成功",
        "data":book_dict
    }
