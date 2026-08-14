
from sqlalchemy import Column, Integer, String, Float, Date
from database import Base


class EmployeeModel(Base):
    """
    员工表 ORM 模型
    对应 MySQL 中的 t_employees 表
    """
    __tablename__ = "t_employees"

    EMPLOYEE_ID = Column(Integer, primary_key=True, index=True, comment="员工ID")
    FIRST_NAME = Column(String(50), nullable=False, comment="名")
    LAST_NAME = Column(String(50), nullable=False, comment="姓")
    EMAIL = Column(String(50), nullable=False, comment="邮箱")
    PHONE_NUMBER = Column(String(50), nullable=False, comment="电话号码")
    HIRE_DATE = Column(Date, nullable=False, comment="入职日期")
    JOB_ID = Column(String(20), nullable=False, comment="职位ID")
    SALARY = Column(Float, nullable=False, comment="薪资")
    COMMISSION_PCT = Column(Float, nullable=True, comment="提成比例")
    MANAGER_ID = Column(Integer, nullable=True, comment="上级经理ID")
    DEPARTMENT_ID = Column(Integer, nullable=True, comment="部门ID")