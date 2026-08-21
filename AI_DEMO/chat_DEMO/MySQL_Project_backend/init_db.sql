-- ============================================================================
-- 职员工作群聊系统 · 数据库初始化脚本
-- ----------------------------------------------------------------------------
-- 说明:
--   本脚本根据 backend/MySQL_Project_backend/models.py 中的 ORM 模型生成,
--   用于手动/全新搭建 my-first-sql 数据库,或作为建表结构文档。
--
--   日常启动时后端会自动建表(Base.metadata.create_all),无需手动执行本脚本。
--   本脚本仅在"从零初始化数据库"或"核对表结构"时使用。
--
-- ⚠️ 注意事项:
--   1. 目标库名 my-first-sql 含连字符,所有库名/表名引用必须加反引号 `。
--   2. ORM 模型把 t_employees.EMPLOYEE_ID / t_jobs.JOB_ID 声明为整数,
--      但运行中的实际库里这两个列是 VARCHAR(见 main.py / migrate.py 注释)。
--      如需复刻"现有库"的类型,请把这两列改为 VARCHAR(如 VARCHAR(10))。
--   3. 建表完成后,若员工表已有数据需要登录功能,请再执行 migrate.py
--      追加 PASSWORD_HASH/ROLE/AVATAR 并初始化默认密码。
-- ============================================================================

-- 0. 建库并选中
CREATE DATABASE IF NOT EXISTS `my-first-sql`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `my-first-sql`;

-- ============================================================================
-- 1. 职位表 t_jobs
--    对应 models.py: JobModel
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_jobs` (
  `JOB_ID`     VARCHAR(20) NOT NULL COMMENT '职位ID',
  `JOB_TITLE`  VARCHAR(50) NOT NULL COMMENT '职位名称',
  `MIN_SALARY` INT         NULL     COMMENT '最低薪资',
  `MAX_SALARY` INT         NULL     COMMENT '最高薪资',
  PRIMARY KEY (`JOB_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位表';

-- ============================================================================
-- 2. 部门表 t_departments
--    对应 models.py: DepartmentModel
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_departments` (
  `DEPARTMENT_ID`   INT         NOT NULL COMMENT '部门ID',
  `DEPARTMENT_NAME` VARCHAR(50) NOT NULL COMMENT '部门名称',
  `MANAGER_ID`      INT         NULL     COMMENT '部门经理ID',
  `LOCATION_ID`     INT         NULL     COMMENT '位置ID',
  PRIMARY KEY (`DEPARTMENT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';

-- ============================================================================
-- 3. 员工表 t_employees
--    对应 models.py: EmployeeModel
--    (EMPLOYEE_ID 按 ORM 声明为整数自增;实际运行库中为 VARCHAR,见文件头说明)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_employees` (
  `EMPLOYEE_ID`   INT          NOT NULL AUTO_INCREMENT COMMENT '员工ID',
  `FIRST_NAME`    VARCHAR(50)  NOT NULL COMMENT '名',
  `LAST_NAME`     VARCHAR(50)  NOT NULL COMMENT '姓',
  `EMAIL`         VARCHAR(50)  NOT NULL COMMENT '邮箱',
  `PHONE_NUMBER`  VARCHAR(50)  NOT NULL COMMENT '电话号码',
  `HIRE_DATE`     DATE         NOT NULL COMMENT '入职日期',
  `JOB_ID`        VARCHAR(20)  NOT NULL COMMENT '职位ID',
  `SALARY`        FLOAT        NOT NULL COMMENT '薪资',
  `COMMISSION_PCT` FLOAT       NULL     COMMENT '提成比例',
  `MANAGER_ID`    INT          NULL     COMMENT '上级经理ID',
  `DEPARTMENT_ID` INT          NULL     COMMENT '部门ID',
  -- V2.0 新增: 登录与角色
  `PASSWORD_HASH` VARCHAR(128) NULL     COMMENT '密码哈希',
  `ROLE`          VARCHAR(20)  NOT NULL DEFAULT 'STAFF' COMMENT '角色:STAFF/MANAGER/PRESIDENT',
  `AVATAR`        VARCHAR(255) NULL     COMMENT '头像文件路径',
  PRIMARY KEY (`EMPLOYEE_ID`),
  KEY `idx_employees_job`        (`JOB_ID`),
  KEY `idx_employees_department` (`DEPARTMENT_ID`),
  KEY `idx_employees_manager`    (`MANAGER_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工表';

-- ============================================================================
-- 4. 群聊消息表 t_group_messages  (部门群 + 全员群共用)
--    对应 models.py: GroupMessageModel
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_group_messages` (
  `MESSAGE_ID` BIGINT      NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `GROUP_TYPE` VARCHAR(10) NOT NULL COMMENT '群类型:DEPT部门群/ALL全员群',
  `GROUP_ID`   INT         NOT NULL COMMENT '群标识:部门群为部门ID,全员群为0',
  `SENDER_ID`  INT         NOT NULL COMMENT '发送者员工ID',
  `CONTENT`    TEXT        NOT NULL COMMENT '消息内容',
  `CREATED_AT` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  PRIMARY KEY (`MESSAGE_ID`),
  KEY `idx_group_type_group`   (`GROUP_TYPE`, `GROUP_ID`),
  KEY `idx_group_sender`       (`SENDER_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群聊消息表';

-- ============================================================================
-- 5. 私聊消息表 t_private_messages
--    对应 models.py: PrivateMessageModel
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_private_messages` (
  `MESSAGE_ID` BIGINT   NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `SENDER_ID`  INT      NOT NULL COMMENT '发送者员工ID',
  `RECEIVER_ID` INT     NOT NULL COMMENT '接收者员工ID',
  `CONTENT`    TEXT     NOT NULL COMMENT '消息内容',
  `CREATED_AT` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  PRIMARY KEY (`MESSAGE_ID`),
  KEY `idx_private_sender`   (`SENDER_ID`),
  KEY `idx_private_receiver` (`RECEIVER_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='私聊消息表';

-- ============================================================================
-- 6. 禁言记录表 t_mutes
--    对应 models.py: MuteModel
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_mutes` (
  `MUTE_ID`     BIGINT       NOT NULL AUTO_INCREMENT COMMENT '禁言记录ID',
  `EMPLOYEE_ID` INT          NOT NULL COMMENT '被禁言员工ID',
  `OPERATOR_ID` INT          NOT NULL COMMENT '操作者员工ID',
  `REASON`      VARCHAR(200) NOT NULL COMMENT '禁言原因',
  `MUTE_UNTIL`  DATETIME     NULL     COMMENT '禁言截止时间,空为永久',
  `CREATED_AT`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '禁言时间',
  PRIMARY KEY (`MUTE_ID`),
  KEY `idx_mutes_employee` (`EMPLOYEE_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='禁言记录表';

-- ============================================================================
-- 7. 未读消息表 t_unread  (每个职员/联系人一行,记录未读私聊数)
--    对应 models.py: UnreadModel
-- ============================================================================
CREATE TABLE IF NOT EXISTS `t_unread` (
  `ID`          BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `EMPLOYEE_ID` INT    NOT NULL COMMENT '所属职员ID',
  `CONTACT_ID`  INT    NOT NULL COMMENT '对方职员ID',
  `COUNT`       INT    NOT NULL DEFAULT 0 COMMENT '未读私聊数',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `uq_unread_employee_contact` (`EMPLOYEE_ID`, `CONTACT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='未读私聊数表';

-- ============================================================================
-- 完。如需预置职位/部门/员工示例数据(源自 MySQL employees 示例库),
-- 请另外从该示例库导入,本脚本只负责表结构。
-- ============================================================================
