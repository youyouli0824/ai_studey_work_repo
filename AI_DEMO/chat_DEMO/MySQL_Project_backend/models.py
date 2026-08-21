
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Float, Date, DateTime, Text, UniqueConstraint
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
    # V2.0 新增:登录与角色
    PASSWORD_HASH = Column(String(128), nullable=True, comment="密码哈希")
    ROLE = Column(String(20), nullable=False, default="STAFF", comment="角色:STAFF/MANAGER/PRESIDENT")
    AVATAR = Column(String(255), nullable=True, comment="头像文件路径")


class DepartmentModel(Base):
    """
    部门表 ORM 模型
    对应 MySQL 中的 t_departments 表
    """
    __tablename__ = "t_departments"

    DEPARTMENT_ID = Column(Integer, primary_key=True, index=True, comment="部门ID")
    DEPARTMENT_NAME = Column(String(50), nullable=False, comment="部门名称")
    MANAGER_ID = Column(Integer, nullable=True, comment="部门经理ID")
    LOCATION_ID = Column(Integer, nullable=True, comment="位置ID")


class JobModel(Base):
    """
    职位表 ORM 模型
    对应 MySQL 中的 t_jobs 表
    """
    __tablename__ = "t_jobs"

    JOB_ID = Column(String(20), primary_key=True, index=True, comment="职位ID")
    JOB_TITLE = Column(String(50), nullable=False, comment="职位名称")
    MIN_SALARY = Column(Integer, nullable=True, comment="最低薪资")
    MAX_SALARY = Column(Integer, nullable=True, comment="最高薪资")


class GroupMessageModel(Base):
    """
    群聊消息表 ORM 模型
    对应 MySQL 中的 t_group_messages 表(部门群 + 全员群共用)
    """
    __tablename__ = "t_group_messages"

    MESSAGE_ID = Column(BigInteger, primary_key=True, autoincrement=True, comment="消息ID")
    GROUP_TYPE = Column(String(10), nullable=False, comment="群类型:DEPT部门群/ALL全员群")
    GROUP_ID = Column(Integer, nullable=False, comment="群标识:部门群为部门ID,全员群为0")
    SENDER_ID = Column(Integer, nullable=False, comment="发送者员工ID")
    CONTENT = Column(Text, nullable=False, comment="消息内容")
    CREATED_AT = Column(DateTime, nullable=False, default=datetime.now, comment="发送时间")


class PrivateMessageModel(Base):
    """
    私聊消息表 ORM 模型
    对应 MySQL 中的 t_private_messages 表
    """
    __tablename__ = "t_private_messages"

    MESSAGE_ID = Column(BigInteger, primary_key=True, autoincrement=True, comment="消息ID")
    SENDER_ID = Column(Integer, nullable=False, comment="发送者员工ID")
    RECEIVER_ID = Column(Integer, nullable=False, comment="接收者员工ID")
    CONTENT = Column(Text, nullable=False, comment="消息内容")
    CREATED_AT = Column(DateTime, nullable=False, default=datetime.now, comment="发送时间")


class MuteModel(Base):
    """
    禁言记录表 ORM 模型
    对应 MySQL 中的 t_mutes 表
    """
    __tablename__ = "t_mutes"

    MUTE_ID = Column(BigInteger, primary_key=True, autoincrement=True, comment="禁言记录ID")
    EMPLOYEE_ID = Column(Integer, nullable=False, comment="被禁言员工ID")
    OPERATOR_ID = Column(Integer, nullable=False, comment="操作者员工ID")
    REASON = Column(String(200), nullable=False, comment="禁言原因")
    MUTE_UNTIL = Column(DateTime, nullable=True, comment="禁言截止时间,空为永久")
    CREATED_AT = Column(DateTime, nullable=False, default=datetime.now, comment="禁言时间")


class UnreadModel(Base):
    """
    私聊未读数表 ORM 模型
    对应 MySQL 中的 t_unread 表(每个职员/联系人一行,记录未读私聊数)
    """
    __tablename__ = "t_unread"

    ID = Column(BigInteger, primary_key=True, autoincrement=True, comment="自增ID")
    EMPLOYEE_ID = Column(Integer, nullable=False, comment="所属职员ID")
    CONTACT_ID = Column(Integer, nullable=False, comment="对方职员ID")
    COUNT = Column(Integer, nullable=False, default=0, comment="未读私聊数")
    __table_args__ = (UniqueConstraint("EMPLOYEE_ID", "CONTACT_ID", name="uq_unread_employee_contact"),)