#为了防止前端传过来非法的恶劣数据
# （例如：图书标题为空、图书价格为负数 `-999` 元、作者名字太长），
# 我们可以使用 Pydantic 提供的 `Field` 为每个字段添加精细化约束！
import re
from typing import Optional, List
from fastapi import FastAPI, HTTPException,Body,Form
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse

app = FastAPI()
books_db: List[dict] = []   # 用内存列表模拟数据库，保存创建成功的图书

'''
class BookCreate(BaseModel):
    title: str               # 必填项，字符串类型
    author: str              # 必填项，字符串类型
    price: float             # 必填项，浮点数类型
    is_published: bool = True # 可选项，默认值为 True
    description: Optional[str] = None # 可选项，默认为 None
'''
class Author(BaseModel):
    name:str=Field(...,min_length=2,
                   max_length=10,
                   description="作者姓名")
    email:str=Field(...,description="作者邮箱")

class BookAdvancedCreate(BaseModel):
    title:str=Field(...,
                    min_length=2,
                    max_length=50,
                    description="图书标题",
                    example="FastAPI基础教程")
    price:float=Field(...,
                      gt=0,
                      le=10000,
                      description="图书价格，必须大于0元且小于等于10000元",
                      example=88.5)
    tags:List[str]=Field(default=[],
                         max_length=5,
                         description="图书标签（最多5个）")
    author_info:Author=Field(...,
                             description="作者信息")

@app.post("/v2/books",summary="添加图书")
def create_book_v2(book:BookAdvancedCreate):
    book_id = len(books_db) + 1
    book_data = book.model_dump()
    book_data["id"] = book_id
    books_db.append(book_data)
    return {
        "code":200,
        "msg":"数据结构校验通过",
        "book_id":book_id,
        "received_data":book_data
    }

@app.get("/books/{book_id}",
         summary="根据 id 查找图书",
         tags=["图书管理"])
def find_book(book_id:int):
    for book in books_db:
        if book["id"] == book_id:
            return {
                "code":200,
                "msg":"查找成功",
                "data":book
            }
    raise HTTPException(status_code=404, detail=f"未找到 id 为 {book_id} 的图书")

@app.put("/books/{book_id}",
         summary="修改图书信息",
         tags=["图书管理"])
def update_book(book_id:int,book:BookAdvancedCreate):
    """
    FastAPI 区分规则:
    1. 匹配路径中 {book_id} 的参数 -> 识别为路径参数
    2. 继承自 BaseModel 的参数 -> 自动识别为请求体 (Request Body)
    """
    for index, old_book in enumerate(books_db):
        if old_book["id"] == book_id:
            new_data = book.model_dump()
            new_data["id"] = book_id
            books_db[index] = new_data
            return {
                "code":200,
                "message":f"成功更新id为{book_id}的图书",
                "updated_data":new_data
            }
    raise HTTPException(status_code=404, detail=f"未找到 id 为 {book_id} 的图书")

@app.put("/books/{book_id}/status",
         summary="综合参数修改接口")
def update_book_status(
    book_id:int,
    book:BookAdvancedCreate,
    notify_user:bool=False,   # 2. 查询参数 (来自 URL 问号后的 ?notify_user=true)
):
    return {
        "book_id":book_id,
        "notify_user":notify_user,
        "book":book
    }

@app.post("/items/importance",summary="更新物品重要性等级")
def update_importance(
    importance:int=Body(...,
                        embed=True,
                        ge=1,
                        le=5)
):
    """
    embed=True 表示要求 JSON 请求体必须带外层 key:
    {
       "importance": 5
    }
    """
    return {"msg": f"重要性等级已更新为: {importance}"}

@app.post("/submit_feedback",
          summary="提交读者留言",
          tags=["读者互动"])
def submit_feedback(
    username: str = Form(..., description="读者姓名"),
    content: str = Form(..., min_length=5, description="留言内容")
):
    return {
        "status": "success",
        "username": username,
        "content_length": len(content),
        "message": "留言发表成功！"
    }


@app.get("/welcome", response_class=HTMLResponse, summary="返回 HTML 渲染页面")
def get_welcome_page():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>FastAPI 欢迎页</title>
        </head>
        <body>
            <h1 style="color: blue;">🎉 欢迎大一新生学习 FastAPI 课程！</h1>
            <p>这是直接由 FastAPI 后端渲染返回的网页内容。</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

