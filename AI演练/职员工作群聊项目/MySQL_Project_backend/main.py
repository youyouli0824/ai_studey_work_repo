from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request, Header, UploadFile, File
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Float, or_, and_
from database import engine, Base, get_db
import models
from models import (
    EmployeeModel,
    DepartmentModel,
    JobModel,
    GroupMessageModel,
    PrivateMessageModel,
    MuteModel,
    UnreadModel,
)
from schemas import (
    EmployeeCreateSchema,
    EmployeeUpdateSchema,
    EmployeeResponseSchema,
    DepartmentResponseSchema,
    JobResponseSchema,
    EmployeeSearchResponseSchema,
    OverviewResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    UserInfoSchema,
    UpdateProfileSchema,
    UpdatePasswordSchema,
    MessageSendSchema,
    PrivateMessageSendSchema,
    MessageResponseSchema,
    MyGroupsResponseSchema,
    GroupInfoSchema,
    ContactSchema,
    ConversationSchema,
    MarkReadSchema,
    MuteCreateSchema,
    MuteResponseSchema,
    ManagerGrantSchema,
    ManagerResponseSchema,
)
from security import hash_password, verify_password, create_token, verify_token
from fastapi.middleware.cors import CORSMiddleware
import time
import os
from datetime import datetime, timedelta
from collections import Counter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="职员各部门工作交流系统")

# 上传文件静态目录(头像等)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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


# ============================================================
# V2.0 登录鉴权与角色权限
# ============================================================
ROLE_STAFF = "STAFF"          # 普通职员
ROLE_MANAGER = "MANAGER"      # 管理部门职员
ROLE_PRESIDENT = "PRESIDENT"  # 总裁
DEFAULT_PASSWORD = "123456"   # 初始/重置密码


def full_name(emp: EmployeeModel) -> str:
    """职员姓名(账号): 名 + 空格 + 姓"""
    return f"{emp.FIRST_NAME} {emp.LAST_NAME}".strip()


def to_user_info(emp: EmployeeModel) -> dict:
    """构造当前用户信息字典"""
    return {
        "EMPLOYEE_ID": int(emp.EMPLOYEE_ID),
        "name": full_name(emp),
        "FIRST_NAME": emp.FIRST_NAME,
        "LAST_NAME": emp.LAST_NAME,
        "EMAIL": emp.EMAIL,
        "PHONE_NUMBER": emp.PHONE_NUMBER,
        "role": emp.ROLE,
        "avatar": emp.AVATAR,
        "JOB_ID": emp.JOB_ID,
        "DEPARTMENT_ID": int(emp.DEPARTMENT_ID) if emp.DEPARTMENT_ID is not None else None,
    }


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> EmployeeModel:
    """从 Authorization: Bearer <token> 解析当前登录职员"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    uid = verify_token(authorization[7:])
    if uid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已失效，请重新登录")
    emp = db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID == uid).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号不存在")
    return emp


def require_roles(*roles):
    """按角色限制的依赖: 返回一个 FastAPI 依赖,角色不在列表中返回 403"""
    def dep(user: EmployeeModel = Depends(get_current_user)):
        if user.ROLE not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无操作权限")
        return user
    return dep


manager_dep = require_roles(ROLE_MANAGER, ROLE_PRESIDENT)  # 管理层
president_dep = require_roles(ROLE_PRESIDENT)               # 总裁


def check_manage_scope(operator: EmployeeModel, target: EmployeeModel):
    """管理层操作范围校验: 不能操作自己;管理部门职员仅能操作普通职员,总裁可操作管理层以下"""
    if operator.EMPLOYEE_ID == target.EMPLOYEE_ID:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能操作本人")
    allowed = (ROLE_STAFF, ROLE_MANAGER) if operator.ROLE == ROLE_PRESIDENT else (ROLE_STAFF,)
    if target.ROLE not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该角色的职员")


def is_muted(emp_id, db: Session) -> bool:
    """判断职员当前是否处于禁言状态(禁言中或永久禁言)"""
    now = datetime.now()
    m = db.query(MuteModel).filter(
        MuteModel.EMPLOYEE_ID == int(emp_id),
        or_(MuteModel.MUTE_UNTIL.is_(None), MuteModel.MUTE_UNTIL > now),
    ).first()
    return m is not None


def to_message_dict(m, sender) -> dict:
    """消息 -> 展示字典(含发送者姓名/头像)"""
    return {
        "message_id": int(m.MESSAGE_ID),
        "group_type": getattr(m, "GROUP_TYPE", None),
        "group_id": getattr(m, "GROUP_ID", None),
        "sender_id": int(m.SENDER_ID),
        "sender_name": full_name(sender) if sender else "未知职员",
        "sender_avatar": sender.AVATAR if sender else None,
        "receiver_id": getattr(m, "RECEIVER_ID", None),
        "content": m.CONTENT,
        "created_at": m.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S") if m.CREATED_AT else "",
    }


# ---------- 认证接口 ----------

@app.post("/api/v1/auth/login", response_model=LoginResponseSchema, summary="登录", tags=["认证"])
def login(login_in: LoginRequestSchema, db: Session = Depends(get_db)):
    # 账号支持两种: ① 员工编号(如 207); ② 职员姓名(名+空格+姓,英文不区分大小写)
    username = login_in.username.strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号不能为空")
    emp = db.query(EmployeeModel).filter(
        or_(
            EmployeeModel.EMPLOYEE_ID == username,
            func.lower(func.concat(EmployeeModel.FIRST_NAME, " ", EmployeeModel.LAST_NAME))
            == username.lower(),
        )
    ).first()
    if not emp or not emp.PASSWORD_HASH or not verify_password(login_in.password, emp.PASSWORD_HASH):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    token = create_token(emp.EMPLOYEE_ID)
    return LoginResponseSchema(token=token, user=UserInfoSchema(**to_user_info(emp)))


@app.post("/api/v1/auth/logout", summary="退出登录", tags=["认证"])
def logout(user: EmployeeModel = Depends(get_current_user)):
    # token 为无状态签名,退出只需前端清除凭证
    return {"message": "已退出登录"}


@app.get("/api/v1/auth/me", response_model=UserInfoSchema, summary="获取当前登录职员信息", tags=["认证"])
def get_me(user: EmployeeModel = Depends(get_current_user)):
    return UserInfoSchema(**to_user_info(user))


# ---------- 个人中心 ----------

@app.put("/api/v1/me", response_model=UserInfoSchema, summary="修改个人信息", tags=["个人中心"])
def update_me(profile_in: UpdateProfileSchema, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return UserInfoSchema(**to_user_info(user))


@app.put("/api/v1/me/password", summary="修改密码", tags=["个人中心"])
def update_password(pwd_in: UpdatePasswordSchema, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.PASSWORD_HASH or not verify_password(pwd_in.old_password, user.PASSWORD_HASH):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    user.PASSWORD_HASH = hash_password(pwd_in.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@app.post("/api/v1/me/avatar", summary="上传头像", tags=["个人中心"])
def upload_avatar(
    file: UploadFile = File(...),
    user: EmployeeModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 仅允许图片类型
    allowed = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持 JPG/PNG/GIF/WebP 图片")
    # 限制 5MB
    content = file.file.read(5 * 1024 * 1024 + 1)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="图片大小不能超过 5MB")
    ext = allowed[file.content_type]
    filename = f"{user.EMPLOYEE_ID}_{int(time.time())}{ext}"
    file_path = os.path.join(AVATAR_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    # 返回可访问的 URL 路径
    user.AVATAR = f"/uploads/avatars/{filename}"
    db.commit()
    db.refresh(user)
    return {"avatar": user.AVATAR}


# 新增员工
@app.post(
    "/api/v1/employees",
    response_model=EmployeeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="新增一名员工",
    tags=["修改信息"]
)
def create_employee(employee_in: EmployeeCreateSchema, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    # 账号唯一性校验(账号 = 姓名)
    new_name = f"{employee_in.FIRST_NAME} {employee_in.LAST_NAME}".strip().lower()
    dup = db.query(EmployeeModel).filter(
        func.lower(func.concat(EmployeeModel.FIRST_NAME, " ", EmployeeModel.LAST_NAME)) == new_name
    ).first()
    if dup:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"姓名 {new_name} 已存在,账号需唯一")
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
    db_employee.ROLE = ROLE_STAFF
    db_employee.PASSWORD_HASH = hash_password(DEFAULT_PASSWORD)
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
def read_all_employees(skip: int = 0, limit: int = 20, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
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
    user: EmployeeModel = Depends(manager_dep),
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
def read_employee(employee_id: int, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
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
def find_employees(employee_FIRST_NAME: str, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
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
def update_employee(employee_id: int, employee_in: EmployeeUpdateSchema, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    employee = db.query(models.EmployeeModel).filter(
        models.EmployeeModel.EMPLOYEE_ID == employee_id
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    check_manage_scope(user, employee)
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
def delete_employee(employee_id: int, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    employee = db.query(models.EmployeeModel).filter(
        models.EmployeeModel.EMPLOYEE_ID == employee_id
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    check_manage_scope(user, employee)
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
def read_all_departments(user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
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
def read_all_jobs(user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    jobs = db.query(JobModel).order_by(JobModel.JOB_ID).all()
    return jobs


# 仪表盘总览统计
@app.get(
    "/api/v1/overview",
    response_model=OverviewResponseSchema,
    summary="仪表盘总览统计",
    tags=["总数据"]
)
def get_overview(user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
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


# ============================================================
# V2.0 群聊(部门群 + 全员群)
# ============================================================

def _last_group_message(db, group_type: str, group_id: int):
    """群聊最后一条消息"""
    return db.query(GroupMessageModel).filter(
        GroupMessageModel.GROUP_TYPE == group_type,
        GroupMessageModel.GROUP_ID == group_id,
    ).order_by(GroupMessageModel.MESSAGE_ID.desc()).first()


def _group_messages(db, group_type: str, group_id: int, page: int, page_size: int):
    """群聊历史消息(分页,按时间升序返回)"""
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    q = db.query(GroupMessageModel).filter(
        GroupMessageModel.GROUP_TYPE == group_type,
        GroupMessageModel.GROUP_ID == group_id,
    )
    total = q.count()
    rows = (
        q.order_by(GroupMessageModel.MESSAGE_ID.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    rows.reverse()
    sender_ids = {int(m.SENDER_ID) for m in rows}
    senders = {}
    if sender_ids:
        # 注意: t_employees.EMPLOYEE_ID 在库中为 varchar,ORM 读回为 str,统一转 int 作字典键
        senders = {int(e.EMPLOYEE_ID): e for e in db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID.in_(sender_ids)).all()}
    items = [to_message_dict(m, senders.get(int(m.SENDER_ID))) for m in rows]
    return {"total": total, "items": items}


@app.get("/api/v1/groups/my", response_model=MyGroupsResponseSchema, summary="我的群聊列表", tags=["群聊"])
def get_my_groups(user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    dept_id = int(user.DEPARTMENT_ID) if user.DEPARTMENT_ID is not None else None
    groups = []
    # 部门群: 成员为本部门职员
    if dept_id is not None:
        dept = db.query(DepartmentModel).filter(DepartmentModel.DEPARTMENT_ID == dept_id).first()
        dept_members = db.query(EmployeeModel).filter(EmployeeModel.DEPARTMENT_ID == dept_id).count()
        last = _last_group_message(db, "DEPT", dept_id)
        groups.append(GroupInfoSchema(
            group_type="DEPT",
            group_id=dept_id,
            name=f"部门群·{dept.DEPARTMENT_NAME if dept else dept_id}",
            member_count=dept_members,
            last_message=last.CONTENT if last else None,
            last_time=last.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S") if last else None,
        ))
    # 全员群: 成员为全体职员
    total_emp = db.query(EmployeeModel).count()
    last_all = _last_group_message(db, "ALL", 0)
    groups.append(GroupInfoSchema(
        group_type="ALL",
        group_id=0,
        name="全员群聊",
        member_count=total_emp,
        last_message=last_all.CONTENT if last_all else None,
        last_time=last_all.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S") if last_all else None,
    ))
    return MyGroupsResponseSchema(groups=groups)


@app.get("/api/v1/groups/dept/messages", summary="部门群历史消息", tags=["群聊"])
def get_dept_group_messages(page: int = 1, page_size: int = 20, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.DEPARTMENT_ID is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="您未分配部门,无法查看部门群")
    return _group_messages(db, "DEPT", int(user.DEPARTMENT_ID), page, page_size)


@app.post("/api/v1/groups/dept/messages", summary="发送部门群消息", tags=["群聊"])
def send_dept_group_message(msg: MessageSendSchema, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.DEPARTMENT_ID is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="您未分配部门,无法在部门群发言")
    if is_muted(user.EMPLOYEE_ID, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您已被禁言,暂时无法在群聊中发言")
    m = GroupMessageModel(
        GROUP_TYPE="DEPT",
        GROUP_ID=int(user.DEPARTMENT_ID),
        SENDER_ID=int(user.EMPLOYEE_ID),
        CONTENT=msg.content,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"message_id": int(m.MESSAGE_ID), "created_at": m.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S")}


@app.get("/api/v1/groups/all/messages", summary="全员群历史消息", tags=["群聊"])
def get_all_group_messages(page: int = 1, page_size: int = 20, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return _group_messages(db, "ALL", 0, page, page_size)


@app.post("/api/v1/groups/all/messages", summary="发送全员群消息", tags=["群聊"])
def send_all_group_message(msg: MessageSendSchema, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_muted(user.EMPLOYEE_ID, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您已被禁言,暂时无法在群聊中发言")
    m = GroupMessageModel(
        GROUP_TYPE="ALL",
        GROUP_ID=0,
        SENDER_ID=int(user.EMPLOYEE_ID),
        CONTENT=msg.content,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"message_id": int(m.MESSAGE_ID), "created_at": m.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S")}


# ============================================================
# V2.0 私聊
# ============================================================

@app.get("/api/v1/contacts", response_model=List[ContactSchema], summary="可私聊职员列表", tags=["私聊"])
def get_contacts(user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.EMPLOYEE_ID != user.EMPLOYEE_ID)
        .order_by(EmployeeModel.EMPLOYEE_ID)
        .all()
    )
    return [
        ContactSchema(
            EMPLOYEE_ID=int(e.EMPLOYEE_ID),
            name=full_name(e),
            DEPARTMENT_ID=int(e.DEPARTMENT_ID) if e.DEPARTMENT_ID is not None else None,
            role=e.ROLE,
            avatar=e.AVATAR,
        )
        for e in rows
    ]


@app.get("/api/v1/private/messages", summary="与指定职员的私聊消息", tags=["私聊"])
def get_private_messages(contact_id: int, page: int = 1, page_size: int = 20, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    q = db.query(PrivateMessageModel).filter(
        or_(
            and_(PrivateMessageModel.SENDER_ID == user.EMPLOYEE_ID, PrivateMessageModel.RECEIVER_ID == contact_id),
            and_(PrivateMessageModel.SENDER_ID == contact_id, PrivateMessageModel.RECEIVER_ID == user.EMPLOYEE_ID),
        )
    )
    total = q.count()
    rows = (
        q.order_by(PrivateMessageModel.MESSAGE_ID.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    rows.reverse()
    sender_ids = {int(m.SENDER_ID) for m in rows}
    senders = {}
    if sender_ids:
        senders = {int(e.EMPLOYEE_ID): e for e in db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID.in_(sender_ids)).all()}
    items = [to_message_dict(m, senders.get(int(m.SENDER_ID))) for m in rows]
    return {"total": total, "items": items}


@app.post("/api/v1/private/messages", summary="发送私聊消息", tags=["私聊"])
def send_private_message(msg: PrivateMessageSendSchema, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    if msg.receiver_id == user.EMPLOYEE_ID:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能给自己发送私聊")
    receiver = db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID == msg.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="接收者不存在")
    m = PrivateMessageModel(
        SENDER_ID=int(user.EMPLOYEE_ID),
        RECEIVER_ID=msg.receiver_id,
        CONTENT=msg.content,
    )
    db.add(m)
    # 接收方未读数 +1(用于红点提示)
    sender_uid = int(user.EMPLOYEE_ID)
    unread = db.query(UnreadModel).filter(
        UnreadModel.EMPLOYEE_ID == msg.receiver_id,
        UnreadModel.CONTACT_ID == sender_uid,
    ).first()
    if unread:
        unread.COUNT += 1
    else:
        db.add(UnreadModel(EMPLOYEE_ID=msg.receiver_id, CONTACT_ID=sender_uid, COUNT=1))
    db.commit()
    db.refresh(m)
    return {"message_id": int(m.MESSAGE_ID), "created_at": m.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S")}


@app.get("/api/v1/private/conversations", response_model=List[ConversationSchema], summary="私聊会话列表(含未读数,按最近消息置顶)", tags=["私聊"])
def get_private_conversations(user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """我的私聊会话: 每个联系人一行,含最后消息/时间/未读数,按最近活动降序(新消息置顶)"""
    uid = int(user.EMPLOYEE_ID)
    rows = (
        db.query(PrivateMessageModel)
        .filter(or_(PrivateMessageModel.SENDER_ID == uid, PrivateMessageModel.RECEIVER_ID == uid))
        .order_by(PrivateMessageModel.MESSAGE_ID.desc())
        .all()
    )
    # 取每个联系人的最后一条消息
    last_by_contact = {}
    for m in rows:
        other = m.RECEIVER_ID if m.SENDER_ID == uid else m.SENDER_ID
        if other not in last_by_contact:
            last_by_contact[other] = m
    # 未读数
    unread_map = {
        r.CONTACT_ID: r.COUNT
        for r in db.query(UnreadModel).filter(UnreadModel.EMPLOYEE_ID == uid).all()
    }
    emp_map = {}
    if last_by_contact:
        emp_map = {
            int(e.EMPLOYEE_ID): e
            for e in db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID.in_(list(last_by_contact.keys()))).all()
        }
    items = []
    for other_id, m in last_by_contact.items():
        emp = emp_map.get(int(other_id))
        items.append(ConversationSchema(
            EMPLOYEE_ID=int(other_id),
            name=full_name(emp) if emp else f"已删除职员#{other_id}",
            avatar=emp.AVATAR if emp else None,
            role=emp.ROLE if emp else ROLE_STAFF,
            DEPARTMENT_ID=int(emp.DEPARTMENT_ID) if emp and emp.DEPARTMENT_ID is not None else None,
            last_message=m.CONTENT,
            last_time=m.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S") if m.CREATED_AT else "",
            unread_count=unread_map.get(int(other_id), 0),
        ))
    items.sort(key=lambda x: x.last_time or "", reverse=True)
    return items


@app.post("/api/v1/private/read", summary="标记与某职员的私聊已读", tags=["私聊"])
def mark_private_read(body: MarkReadSchema, user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(UnreadModel).filter(
        UnreadModel.EMPLOYEE_ID == int(user.EMPLOYEE_ID),
        UnreadModel.CONTACT_ID == body.contact_id,
    ).first()
    if row:
        db.delete(row)
        db.commit()
    return {"message": "已标记已读"}


@app.get("/api/v1/private/unread-total", summary="未读私聊总数(侧边栏红点)", tags=["私聊"])
def get_unread_total(user: EmployeeModel = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(UnreadModel.COUNT), 0)).filter(
        UnreadModel.EMPLOYEE_ID == int(user.EMPLOYEE_ID)
    ).scalar()
    return {"total": int(total or 0)}


# ============================================================
# V2.0 禁言管理(管理层)
# ============================================================

@app.get("/api/v1/mutes", response_model=List[MuteResponseSchema], summary="禁言列表", tags=["禁言"])
def list_mutes(user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    now = datetime.now()
    rows = (
        db.query(MuteModel)
        .filter(or_(MuteModel.MUTE_UNTIL.is_(None), MuteModel.MUTE_UNTIL > now))
        .order_by(MuteModel.MUTE_ID.desc())
        .all()
    )
    ids = [int(r.EMPLOYEE_ID) for r in rows] + [int(r.OPERATOR_ID) for r in rows]
    emp_map = {}
    if ids:
        emp_map = {int(e.EMPLOYEE_ID): e for e in db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID.in_(ids)).all()}
    items = []
    for r in rows:
        emp = emp_map.get(r.EMPLOYEE_ID)
        op = emp_map.get(r.OPERATOR_ID)
        items.append(MuteResponseSchema(
            mute_id=int(r.MUTE_ID),
            employee_id=int(r.EMPLOYEE_ID),
            employee_name=full_name(emp) if emp else f"已删除职员#{r.EMPLOYEE_ID}",
            operator_id=int(r.OPERATOR_ID),
            operator_name=full_name(op) if op else f"已删除职员#{r.OPERATOR_ID}",
            reason=r.REASON,
            mute_until=r.MUTE_UNTIL.strftime("%Y-%m-%d %H:%M:%S") if r.MUTE_UNTIL else None,
            created_at=r.CREATED_AT.strftime("%Y-%m-%d %H:%M:%S") if r.CREATED_AT else "",
        ))
    return items


@app.post("/api/v1/mutes", summary="禁言", tags=["禁言"])
def create_mute(mute_in: MuteCreateSchema, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    target = db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID == mute_in.employee_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="被禁言职员不存在")
    check_manage_scope(user, target)
    mute_until = None
    if mute_in.mute_minutes:
        mute_until = datetime.now() + timedelta(minutes=mute_in.mute_minutes)
    m = MuteModel(
        EMPLOYEE_ID=int(target.EMPLOYEE_ID),
        OPERATOR_ID=int(user.EMPLOYEE_ID),
        REASON=mute_in.reason,
        MUTE_UNTIL=mute_until,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"mute_id": int(m.MUTE_ID), "message": f"已禁言 {full_name(target)}"}


@app.delete("/api/v1/mutes/{mute_id}", status_code=status.HTTP_204_NO_CONTENT, summary="解除禁言", tags=["禁言"])
def delete_mute(mute_id: int, user: EmployeeModel = Depends(manager_dep), db: Session = Depends(get_db)):
    m = db.query(MuteModel).filter(MuteModel.MUTE_ID == mute_id).first()
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="禁言记录不存在")
    db.delete(m)
    db.commit()
    return None


# ============================================================
# V2.0 总裁管理(管理部门任免 / 管理权限授予撤销)
# ============================================================

@app.get("/api/v1/managers", response_model=List[ManagerResponseSchema], summary="管理部门职员名单", tags=["总裁管理"])
def list_managers(user: EmployeeModel = Depends(president_dep), db: Session = Depends(get_db)):
    rows = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.ROLE.in_([ROLE_MANAGER, ROLE_PRESIDENT]))
        .order_by(EmployeeModel.EMPLOYEE_ID)
        .all()
    )
    return [
        ManagerResponseSchema(
            EMPLOYEE_ID=int(e.EMPLOYEE_ID),
            name=full_name(e),
            role=e.ROLE,
            DEPARTMENT_ID=int(e.DEPARTMENT_ID) if e.DEPARTMENT_ID is not None else None,
        )
        for e in rows
    ]


@app.post("/api/v1/managers", summary="授予管理权限", tags=["总裁管理"])
def grant_manager(mgr: ManagerGrantSchema, user: EmployeeModel = Depends(president_dep), db: Session = Depends(get_db)):
    target = db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID == mgr.employee_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="职员不存在")
    if target.ROLE == ROLE_PRESIDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能对总裁操作")
    if target.ROLE == ROLE_MANAGER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该职员已是管理部门职员")
    target.ROLE = ROLE_MANAGER
    db.commit()
    return {"message": f"已将 {full_name(target)} 授予为管理部门职员"}


@app.delete("/api/v1/managers/{employee_id}", summary="撤销管理权限", tags=["总裁管理"])
def revoke_manager(employee_id: int, user: EmployeeModel = Depends(president_dep), db: Session = Depends(get_db)):
    target = db.query(EmployeeModel).filter(EmployeeModel.EMPLOYEE_ID == employee_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="职员不存在")
    if target.ROLE == ROLE_PRESIDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能撤销总裁的管理权限")
    if target.ROLE != ROLE_MANAGER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该职员不是管理部门职员")
    target.ROLE = ROLE_STAFF
    db.commit()
    return {"message": f"已撤销 {full_name(target)} 的管理权限"}


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