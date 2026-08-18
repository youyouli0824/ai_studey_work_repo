from typing import Optional, List
from datetime import date
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