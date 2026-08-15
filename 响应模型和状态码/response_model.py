from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

#数据库里的完整的模型
class UserInDB(BaseModel):
    id:int
    username:str
    email:str
    hashed_password:str

#返回给前端展示的安全用户响应模型
class UserPublicResponse(BaseModel):
    id:int
    username:str
    email:str

@app.get(
    "/user/{user_id}",
    response_model=UserPublicResponse,#指定响应过滤输出模型
    summary="获取公开信息"
)
def get_user_profile(user_id:int):
    user_in_db=UserInDB(
        id=user_id,
        username="student_zhang",
        email="zhang@university.edu.cn",
        hashed_password="qscazx0824"
    )
    return user_in_db