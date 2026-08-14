from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from schemas import EmployeeCreateSchema, EmployeeUpdateSchema, EmployeeResponseSchema
from fastapi.middleware.cors import CORSMiddleware
import time

Base.metadata.create_all(bind=engine)

app = FastAPI(title="员工管理系统(MySQL数据库版)")

# 添加 CORS 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有来源(开发阶段可放开)
    allow_credentials=False,   # allow_origins 为 "*" 时,credentials 必须为 False
    allow_methods=["*"],       # 允许所有 HTTP 方法(GET/POST/PUT/DELETE 等)
    allow_headers=["*"],       # 允许所有请求头
)


# 全局异常处理器:统一处理 HTTPException(如 404)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
        },
    )


# 全局异常处理器:请求参数校验失败(如字段类型错误)统一返回 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "code": 422,
            "message": "请求参数校验失败",
            "detail": exc.errors(),
        },
    )


# 全局异常处理器:兜底捕获所有未处理的异常,统一返回 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc),
        },
    )


# 新增员工
@app.post(
    "/api/v1/employees",
    response_model=EmployeeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="新增一名员工",
    tags=["修改信息"]
)
def create_employee(employee_in: EmployeeCreateSchema, db: Session = Depends(get_db)):
    # 实例化ORM对象
    db_employee = models.EmployeeModel(**employee_in.model_dump())
    db.add(db_employee)  # 把对象添加到会话
    db.commit()  # 提交事务保存到MySQL
    db.refresh(db_employee)  # 刷新获取数据库中的最新数据
    return db_employee


# 查询所有员工
@app.get(
    "/api/v1/employees",
    response_model=List[EmployeeResponseSchema],
    summary="获取所有员工列表",
    tags=["总数据"]
)
def read_all_employees(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    employees = db.query(models.EmployeeModel).offset(skip).limit(limit).all()
    return employees


# 根据ID查询单个员工
@app.get(
    "/api/v1/employees/{employee_id}",
    response_model=EmployeeResponseSchema,
    summary="根据ID获取员工",
    tags=["查询信息"]
)
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.EmployeeModel).filter(
        models.EmployeeModel.EMPLOYEE_ID == employee_id
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    return employee

#根据模糊名字查找（多个）员工信息
@app.get(
    "/api/v1/find/{employee_FIRST_NAME}",
    response_model=List[EmployeeResponseSchema],
    summary="姓名模糊查找员工",
    tags=["查询信息"]
)
def find_employees(employee_FIRST_NAME: str, db: Session = Depends(get_db)):
    employees = db.query(models.EmployeeModel).filter(
        models.EmployeeModel.FIRST_NAME.like(f"%{employee_FIRST_NAME}%")
    ).all()
    return employees

# 更新员工
@app.put(
    "/api/v1/employees/{employee_id}",
    response_model=EmployeeResponseSchema,
    summary="更新员工信息",
    tags=["修改信息"]
)
def update_employee(employee_id: int, employee_in: EmployeeUpdateSchema, db: Session = Depends(get_db)):
    employee = db.query(models.EmployeeModel).filter(
        models.EmployeeModel.EMPLOYEE_ID == employee_id
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    # 只更新请求中实际传入的字段
    update_data = employee_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


# 删除员工
@app.delete(
    "/api/v1/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除员工",
    tags=["修改信息"]
)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.EmployeeModel).filter(
        models.EmployeeModel.EMPLOYEE_ID == employee_id
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    db.delete(employee)
    db.commit()
    return None

origins=[
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "*"
]


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    # ① 请求进入时:记录开始时间
    start = time.time()
    print(f"收到请求: {request.method} {request.url.path}")

    # ② 交给下一个中间件/路由函数处理
    response = await call_next(request)

    # ③ 响应返回时:计算耗时
    duration = time.time() - start
    print(f"响应完成,耗时: {duration:.4f} 秒")
    return response