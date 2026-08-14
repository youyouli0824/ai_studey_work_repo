from typing import Optional
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