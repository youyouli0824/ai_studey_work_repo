from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    """员工公共字段"""
    FIRST_NAME: str = Field(..., min_length=1, max_length=50, description="名")
    LAST_NAME: str = Field(..., min_length=1, max_length=50, description="姓")
    EMAIL: str = Field(..., min_length=1, max_length=50, description="邮箱")
    PHONE_NUMBER: str = Field(..., min_length=1, max_length=50, description="电话号码")
    HIRE_DATE: date = Field(..., description="入职日期")
    JOB_ID: str = Field(..., min_length=1, max_length=20, description="职位ID")
    SALARY: float = Field(..., gt=0, description="薪资")
    COMMISSION_PCT: Optional[float] = Field(None, ge=0, description="提成比例")
    MANAGER_ID: Optional[int] = Field(None, description="上级经理ID")
    DEPARTMENT_ID: Optional[int] = Field(None, description="部门ID")


class EmployeeCreateSchema(EmployeeBase):
    """创建员工请求模型"""
    pass


class EmployeeUpdateSchema(BaseModel):
    """更新员工请求模型(所有字段可选)"""
    FIRST_NAME: Optional[str] = Field(None, min_length=1, max_length=50)
    LAST_NAME: Optional[str] = Field(None, min_length=1, max_length=50)
    EMAIL: Optional[str] = Field(None, min_length=1, max_length=50)
    PHONE_NUMBER: Optional[str] = Field(None, min_length=1, max_length=50)
    HIRE_DATE: Optional[date] = None
    JOB_ID: Optional[str] = Field(None, min_length=1, max_length=20)
    SALARY: Optional[float] = Field(None, gt=0)
    COMMISSION_PCT: Optional[float] = Field(None, ge=0)
    MANAGER_ID: Optional[int] = None
    DEPARTMENT_ID: Optional[int] = None


class EmployeeResponseSchema(EmployeeBase):
    """员工返回响应模型"""
    EMPLOYEE_ID: int
    ROLE: str = Field(default="STAFF", description="角色:STAFF/MANAGER/PRESIDENT")
    AVATAR: Optional[str] = Field(None, description="头像文件路径")
    model_config = ConfigDict(from_attributes=True)


class DepartmentResponseSchema(BaseModel):
    """部门返回响应模型"""
    DEPARTMENT_ID: int
    DEPARTMENT_NAME: str
    MANAGER_ID: Optional[int] = None
    LOCATION_ID: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class JobResponseSchema(BaseModel):
    """职位返回响应模型"""
    JOB_ID: str
    JOB_TITLE: str
    MIN_SALARY: Optional[int] = None
    MAX_SALARY: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class EmployeeSearchResponseSchema(BaseModel):
    """员工组合查询 + 分页 响应模型"""
    total: int = Field(..., description="符合条件的总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    items: List[EmployeeResponseSchema] = Field(..., description="当前页员工列表")


class OverviewResponseSchema(BaseModel):
    """仪表盘总览统计响应模型"""
    total_employees: int = Field(..., description="员工总数")
    total_departments: int = Field(..., description="部门总数")
    total_jobs: int = Field(..., description="职位总数")
    avg_salary: float = Field(..., description="平均薪资")
    max_salary: float = Field(..., description="最高薪资")
    min_salary: float = Field(..., description="最低薪资")
    department_stats: List[dict] = Field(..., description="部门维度统计")
    job_stats: List[dict] = Field(..., description="职位维度统计")
    hire_year_distribution: List[dict] = Field(..., description="入职年份分布")


# ============ V2.0 新增:登录 / 个人中心 ============

class LoginRequestSchema(BaseModel):
    """登录请求模型(账号为姓名,英文不区分大小写)"""
    username: str = Field(..., min_length=1, max_length=100, description="账号(姓名)")
    password: str = Field(..., min_length=1, max_length=100, description="密码")


class UserInfoSchema(BaseModel):
    """当前登录用户信息"""
    EMPLOYEE_ID: int
    name: str = Field(..., description="姓名(账号)")
    FIRST_NAME: str
    LAST_NAME: str
    EMAIL: Optional[str] = None
    PHONE_NUMBER: Optional[str] = None
    role: str = Field(..., description="角色")
    avatar: Optional[str] = None
    JOB_ID: Optional[str] = None
    DEPARTMENT_ID: Optional[int] = None


class LoginResponseSchema(BaseModel):
    """登录响应"""
    token: str
    user: UserInfoSchema


class UpdateProfileSchema(BaseModel):
    """修改个人信息(仅联系信息,姓名/角色/部门不可自行修改)"""
    EMAIL: Optional[str] = Field(None, min_length=1, max_length=50)
    PHONE_NUMBER: Optional[str] = Field(None, min_length=1, max_length=50)


class UpdatePasswordSchema(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=1, max_length=100)


# ============ V2.0 新增:群聊 / 私聊 ============

class MessageSendSchema(BaseModel):
    """发送消息请求"""
    content: str = Field(..., min_length=1, max_length=2000, description="消息内容")


class PrivateMessageSendSchema(BaseModel):
    """发送私聊请求"""
    receiver_id: int = Field(..., description="接收者员工ID")
    content: str = Field(..., min_length=1, max_length=2000, description="消息内容")


class MessageResponseSchema(BaseModel):
    """消息返回模型"""
    message_id: int
    group_type: Optional[str] = None
    group_id: Optional[int] = None
    sender_id: int
    sender_name: str
    sender_avatar: Optional[str] = None
    receiver_id: Optional[int] = None
    content: str
    created_at: str


class GroupInfoSchema(BaseModel):
    """群聊信息"""
    group_type: str
    group_id: int
    name: str
    member_count: int
    last_message: Optional[str] = None
    last_time: Optional[str] = None


class MyGroupsResponseSchema(BaseModel):
    """我的群聊列表"""
    groups: List[GroupInfoSchema]


class ContactSchema(BaseModel):
    """可私聊联系人"""
    EMPLOYEE_ID: int
    name: str
    DEPARTMENT_ID: Optional[int] = None
    role: str
    avatar: Optional[str] = None


class ConversationSchema(BaseModel):
    """私聊会话(按最近消息排序,含未读数)"""
    EMPLOYEE_ID: int
    name: str
    avatar: Optional[str] = None
    role: str
    DEPARTMENT_ID: Optional[int] = None
    last_message: Optional[str] = None
    last_time: Optional[str] = None
    unread_count: int = 0


class MarkReadSchema(BaseModel):
    """标记会话已读请求"""
    contact_id: int = Field(..., description="对方员工ID")


# ============ V2.0 新增:禁言 / 总裁管理 ============

class MuteCreateSchema(BaseModel):
    """禁言请求"""
    employee_id: int = Field(..., description="被禁言员工ID")
    reason: str = Field(..., min_length=1, max_length=200, description="禁言原因")
    mute_minutes: Optional[int] = Field(None, ge=1, description="禁言时长(分钟),为空表示永久")


class MuteResponseSchema(BaseModel):
    """禁言记录返回"""
    mute_id: int
    employee_id: int
    employee_name: str
    operator_id: int
    operator_name: str
    reason: str
    mute_until: Optional[str] = None
    created_at: str


class ManagerGrantSchema(BaseModel):
    """授予/撤销管理权限请求"""
    employee_id: int = Field(..., description="目标员工ID")


class ManagerResponseSchema(BaseModel):
    """管理部门职员信息"""
    EMPLOYEE_ID: int
    name: str
    role: str
    DEPARTMENT_ID: Optional[int] = None