"""
数据库迁移脚本(V1.0 -> V2.0)
功能:
  1. 为 t_employees 表新增列: PASSWORD_HASH(密码哈希)、ROLE(角色)、AVATAR(头像路径)
  2. 按预置规则初始化角色:
     - 指定总裁账号             -> PRESIDENT(总裁,唯一)
     - 职位为总裁(AD_PRES)的其它员工 -> 视为管理层成员
     - 属于高级管理层(部门90)   -> MANAGER(管理部门职员)
     - 其余                    -> STAFF(普通职员)
  3. 为所有员工写入默认密码 123456 的哈希
说明: 数据库中原有两个 AD_PRES(100 Steven King / 207 鲤悠悠),经确认以
      员工 207 为唯一总裁,Steven King 降为管理部门职员。
用法:  python migrate.py
"""
import sys
from sqlalchemy import text
from database import engine
from security import hash_password

DEFAULT_PASSWORD = "123456"
# 唯一总裁账号(员工编号)
PRESIDENT_EMPLOYEE_ID = "207"


def column_exists(conn, table, column):
    row = conn.execute(
        text(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND COLUMN_NAME = :c"
        ),
        {"t": table, "c": column},
    ).scalar()
    return row > 0


def main():
    with engine.begin() as conn:
        print("== 1. 新增列 ==")
        if not column_exists(conn, "t_employees", "PASSWORD_HASH"):
            conn.execute(text("ALTER TABLE t_employees ADD COLUMN PASSWORD_HASH VARCHAR(128) NULL COMMENT '密码哈希'"))
            print("  + 已添加列 PASSWORD_HASH")
        else:
            print("  = PASSWORD_HASH 已存在,跳过")
        if not column_exists(conn, "t_employees", "ROLE"):
            conn.execute(text("ALTER TABLE t_employees ADD COLUMN ROLE VARCHAR(20) NOT NULL DEFAULT 'STAFF' COMMENT '角色:STAFF/MANAGER/PRESIDENT'"))
            print("  + 已添加列 ROLE")
        else:
            print("  = ROLE 已存在,跳过")
        if not column_exists(conn, "t_employees", "AVATAR"):
            conn.execute(text("ALTER TABLE t_employees ADD COLUMN AVATAR VARCHAR(255) NULL COMMENT '头像文件路径'"))
            print("  + 已添加列 AVATAR")
        else:
            print("  = AVATAR 已存在,跳过")

        print("== 2. 初始化角色 ==")
        # 先全部重置为普通职员,保证脚本可重复执行
        conn.execute(text("UPDATE t_employees SET ROLE='STAFF'"))
        # 唯一总裁: 指定账号(注意 EMPLOYEE_ID/JOB_ID 在库中为 varchar,用字符串比较)
        r = conn.execute(
            text("UPDATE t_employees SET ROLE='PRESIDENT' WHERE EMPLOYEE_ID = :pid"),
            {"pid": PRESIDENT_EMPLOYEE_ID},
        )
        print(f"  - 唯一总裁(员工{PRESIDENT_EMPLOYEE_ID}): 影响 {r.rowcount} 行")
        # 其余 AD_PRES 员工视为管理层成员
        r = conn.execute(text("UPDATE t_employees SET ROLE='MANAGER' WHERE JOB_ID = 'AD_PRES' AND ROLE != 'PRESIDENT'"))
        print(f"  - 其余总裁职位员工(降为管理层): 影响 {r.rowcount} 行")
        # 管理部门职员: 部门 90 且当前仍为 STAFF
        r = conn.execute(text("UPDATE t_employees SET ROLE='MANAGER' WHERE DEPARTMENT_ID = '90' AND ROLE = 'STAFF'"))
        print(f"  - 管理部门职员(部门90): 影响 {r.rowcount} 行")

        print("== 3. 初始化默认密码 ==")
        pwd_hash = hash_password(DEFAULT_PASSWORD)
        r = conn.execute(
            text("UPDATE t_employees SET PASSWORD_HASH = :ph WHERE PASSWORD_HASH IS NULL"),
            {"ph": pwd_hash},
        )
        print(f"  - 写入默认密码哈希(123456): {r.rowcount} 行")

    # 打印角色分布
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT ROLE, COUNT(*) FROM t_employees GROUP BY ROLE")).all()
        print("== 角色分布 ==")
        for role, cnt in rows:
            print(f"  {role}: {cnt}")

    print("迁移完成。")


if __name__ == "__main__":
    sys.exit(main())
