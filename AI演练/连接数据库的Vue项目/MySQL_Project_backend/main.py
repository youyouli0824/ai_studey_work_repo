from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Float, or_
from database import engine, Base, get_db
import models
from models import EmployeeModel, DepartmentModel, JobModel
from schemas import (
    EmployeeCreateSchema,
    EmployeeUpdateSchema,
    EmployeeResponseSchema,
    DepartmentResponseSchema,
    JobResponseSchema,
    EmployeeSearchResponseSchema,
    OverviewResponseSchema,
)
from fastapi.middleware.cors import CORSMiddleware
import time
from collections import Counter

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
    # t_employees 的 EMPLOYEE_ID 是 varchar 主键,无自增/默认值,
    # 因此由后端自动生成:取当前最大编号 + 1。
    # 注意:列在库中为 varchar,聚合前需转数值,否则 MAX 会按字符串比较出错。
    max_id = db.query(
        func.max(cast(EmployeeModel.EMPLOYEE_ID, Float))
    ).scalar() or 0
    next_id = int(max_id) + 1
    # 实例化ORM对象
    db_employee = models.EmployeeModel(
        EMPLOYEE_ID=next_id, **employee_in.model_dump()
    )
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


# 组合条件查询 + 分页(姓名/部门/职位/薪资/入职日期多条件过滤)
@app.get(
    "/api/v1/employees/search",
    response_model=EmployeeSearchResponseSchema,
    summary="组合条件查询员工(分页)",
    tags=["查询信息"]
)
def search_employees(
    keyword: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    department_id: Optional[int] = None,
    job_id: Optional[str] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    hire_date_start: Optional[str] = None,
    hire_date_end: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    # 动态拼接查询条件
    query = db.query(EmployeeModel)
    # 关键字:同时匹配 名/姓/邮箱(OR 语义)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                EmployeeModel.FIRST_NAME.like(like),
                EmployeeModel.LAST_NAME.like(like),
                EmployeeModel.EMAIL.like(like),
            )
        )
    if first_name:
        query = query.filter(EmployeeModel.FIRST_NAME.like(f"%{first_name}%"))
    if last_name:
        query = query.filter(EmployeeModel.LAST_NAME.like(f"%{last_name}%"))
    if department_id is not None:
        query = query.filter(EmployeeModel.DEPARTMENT_ID == department_id)
    if job_id:
        query = query.filter(EmployeeModel.JOB_ID == job_id)
    if min_salary is not None:
        query = query.filter(EmployeeModel.SALARY >= min_salary)
    if max_salary is not None:
        query = query.filter(EmployeeModel.SALARY <= max_salary)
    if hire_date_start:
        query = query.filter(EmployeeModel.HIRE_DATE >= hire_date_start)
    if hire_date_end:
        query = query.filter(EmployeeModel.HIRE_DATE <= hire_date_end)

    # 先统计总数,再分页
    total = query.count()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    employees = (
        query.order_by(EmployeeModel.EMPLOYEE_ID)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return EmployeeSearchResponseSchema(
        total=total,
        page=page,
        page_size=page_size,
        items=employees,
    )


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


# 获取所有部门列表
@app.get(
    "/api/v1/departments",
    response_model=List[DepartmentResponseSchema],
    summary="获取所有部门列表",
    tags=["分类信息"]
)
def read_all_departments(db: Session = Depends(get_db)):
    departments = (
        db.query(DepartmentModel)
        .order_by(DepartmentModel.DEPARTMENT_ID)
        .all()
    )
    return departments


# 获取所有职位列表
@app.get(
    "/api/v1/jobs",
    response_model=List[JobResponseSchema],
    summary="获取所有职位列表",
    tags=["分类信息"]
)
def read_all_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobModel).order_by(JobModel.JOB_ID).all()
    return jobs


# 仪表盘总览统计
@app.get(
    "/api/v1/overview",
    response_model=OverviewResponseSchema,
    summary="仪表盘总览统计",
    tags=["总数据"]
)
def get_overview(db: Session = Depends(get_db)):
    # 基础指标(SALARY 在数据库中为 varchar,聚合前需逐行转为数值,否则会按字符串比较)
    salary_col = cast(EmployeeModel.SALARY, Float)
    total_employees = db.query(func.count(EmployeeModel.EMPLOYEE_ID)).scalar() or 0
    total_departments = db.query(func.count(DepartmentModel.DEPARTMENT_ID)).scalar() or 0
    total_jobs = db.query(func.count(JobModel.JOB_ID)).scalar() or 0
    avg_salary = db.query(func.avg(salary_col)).scalar() or 0
    max_salary = db.query(func.max(salary_col)).scalar() or 0
    min_salary = db.query(func.min(salary_col)).scalar() or 0

    # 部门维度统计(人数 + 平均薪资)
    dept_rows = (
        db.query(
            EmployeeModel.DEPARTMENT_ID,
            func.count(EmployeeModel.EMPLOYEE_ID),
            func.avg(cast(EmployeeModel.SALARY, Float)),
        )
        .group_by(EmployeeModel.DEPARTMENT_ID)
        .all()
    )
    dept_name_map = {
        d.DEPARTMENT_ID: d.DEPARTMENT_NAME for d in db.query(DepartmentModel).all()
    }
    department_stats = []
    for dept_id, cnt, avg_sal in dept_rows:
        department_stats.append({
            "department_id": dept_id,
            "department_name": dept_name_map.get(
                dept_id, "未分配" if dept_id is None else f"部门{dept_id}"
            ),
            "count": cnt,
            "avg_salary": round(avg_sal or 0, 2),
        })
    department_stats.sort(
        key=lambda x: (x["department_id"] is None, x["department_id"] or 0)
    )

    # 职位维度统计(人数)
    job_rows = (
        db.query(EmployeeModel.JOB_ID, func.count(EmployeeModel.EMPLOYEE_ID))
        .group_by(EmployeeModel.JOB_ID)
        .all()
    )
    job_title_map = {j.JOB_ID: j.JOB_TITLE for j in db.query(JobModel).all()}
    job_stats = [
        {"job_id": jid, "job_title": job_title_map.get(jid, jid), "count": cnt}
        for jid, cnt in job_rows
    ]
    job_stats.sort(key=lambda x: -x["count"])

    # 入职年份分布
    all_employees = db.query(EmployeeModel.HIRE_DATE).all()
    year_counter = Counter()
    for (hire_date,) in all_employees:
        if hire_date:
            year_counter[str(hire_date)[:4]] += 1
    hire_year_distribution = [
        {"year": year, "count": cnt} for year, cnt in sorted(year_counter.items())
    ]

    return OverviewResponseSchema(
        total_employees=total_employees,
        total_departments=total_departments,
        total_jobs=total_jobs,
        avg_salary=round(avg_salary or 0, 2),
        max_salary=max_salary or 0,
        min_salary=min_salary or 0,
        department_stats=department_stats,
        job_stats=job_stats,
        hire_year_distribution=hire_year_distribution,
    )


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