from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="图书管理系统API")
# 允许跨域请求（前后端分离必须）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
books = [
    {"id": 1, "title": "Python编程：从入门到实践", "author": "埃里克·马瑟斯","price": 89.0},
    {"id": 2, "title": "Vue.js设计与实现", "author": "霍春阳", "price": 99.0},
    {"id": 3, "title": "深入理解计算机系统", "author": "布莱恩特", "price": 139.0},
    {"id": 4, "title": "算法导论", "author": "科曼", "price": 128.0},
    {"id": 5, "title": "FastAPI实战", "author": "王五", "price": 79.0},
]
@app.get("/api/books")
async def get_books():
    return {"code":200,"data":books}

@app.get("/api/books/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return {"code": 200, "data": book}
    return {"code": 404, "message": "图书不存在"}