# 职员各部门工作交流系统

基于 **Vue 3 + Vite + Element Plus + ECharts** 的前端，配合 **FastAPI + MySQL** 后端的
职员办公交流平台。在原「职工信息管理系统」（员工 CRUD / 查询 / 统计）基础上升级而来：
新增登录鉴权、三级角色权限、部门群聊 / 全员群聊 / 职员私聊、个人中心与头像、禁言管理、总裁管理。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3（组合式 API）、Vite 7、Vue Router 4、Element Plus、Axios、ECharts |
| 后端 | Python 3.14、FastAPI、SQLAlchemy、PyMySQL（`MySQL_Project_backend/`） |
| 数据库 | MySQL（`my-first-sql` 库，`t_employees` 107 条数据） |

## 角色权限

| 角色 | 权限 |
|---|---|
| 普通职员 | 个人中心、修改密码、上传头像、部门群聊（仅同部门）、全员群聊、职员私聊 |
| 管理部门职员 | 普通职员全部功能 + 员工管理（对普通职员增删改查）、信息面板（仪表盘/统计）、禁言管理 |
| 总裁 | 管理部门职员全部功能 + 管理部门任免（授予/撤销管理权限） |

**登录**：账号为**职员姓名**（英文不区分大小写）或**员工编号**（如 `207`），初始密码 `123456`。
**预置**：总裁 = 员工 207「鲤悠悠」；管理部门职员 = 员工 100/101/102；其余为普通职员。

## 目录结构

```
职员各部门工作群聊项目/
├── MySQL_Project_backend/   # FastAPI 后端
│   ├── main.py              # 全部接口（登录/角色/群聊/私聊/禁言/总裁管理/员工管理/统计）
│   ├── models.py            # ORM 模型（员工 + 群聊消息/私聊消息/禁言表）
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── security.py          # 密码哈希(PBKDF2) + 登录 token(HMAC 签名)
│   ├── migrate.py           # 数据库迁移（加列 + 角色预置 + 默认密码）
│   └── uploads/avatars/     # 上传的头像文件
├── index.html
├── package.json
├── vite.config.js           # @ 别名、/api 与 /uploads 代理到 8000
├── public/
├── 分析类文件/              # 需求文档 / 开发问题文档 / 接口文档
└── src/
    ├── main.js              # 入口（Element Plus 中文 locale + 路由）
    ├── style.css            # 全局主题
    ├── store/auth.js        # 登录状态（token + 用户信息，localStorage 持久化）
    ├── router/              # 路由 + 登录/角色守卫
    ├── api/index.js         # Axios 封装（自动携带 token、401 跳转）+ 全部接口函数
    ├── utils/               # 格式化工具 + 中文映射字典
    ├── components/ChartBox.vue
    ├── layout/MainLayout.vue     # 角色化侧边栏 + 顶栏用户信息
    └── views/
        ├── Login.vue            # 登录页
        ├── Profile.vue          # 个人中心（信息/密码/头像）
        ├── GroupChat.vue        # 群聊（部门群 + 全员群，5 秒轮询）
        ├── PrivateChat.vue      # 职员私聊
        ├── MuteManagement.vue   # 禁言管理（管理层）
        ├── PresidentManage.vue  # 总裁管理（管理层任免）
        ├── Dashboard.vue        # 信息面板·仪表盘（管理层）
        ├── EmployeeList.vue     # 员工管理（管理层）
        └── EmployeeStats.vue    # 分类统计（管理层）
```

## 运行方法

### 1. 初始化数据库（首次）

```bash
cd MySQL_Project_backend
python migrate.py        # 加列 + 预置角色 + 写入默认密码 123456
```

### 2. 启动后端（端口 8000）

```bash
cd MySQL_Project_backend
python -m uvicorn main:app --reload --port 8000
```

> 数据库连接配置在 `MySQL_Project_backend/database.py` 中，如账号密码不同请自行修改。

### 3. 启动前端（端口 5173）

```bash
# 首次运行先安装依赖
npm install

# 开发模式
npm run dev
```

浏览器访问 http://localhost:5173。开发模式下 `/api` 与 `/uploads` 由 Vite 代理到
`http://127.0.0.1:8000`，无需额外跨域配置。

### 4. 生产构建

```bash
npm run build     # 产物输出到 dist/
```

> 生产环境需将 `/api` 与 `/uploads` 反向代理到 8000。

## 功能清单

- **登录**：账号为姓名（英文不区分大小写），默认密码 `123456`，token 会话 + 路由守卫；未登录自动跳登录页。
- **个人中心**：查看/修改联系信息、修改密码、上传图片头像（JPG/PNG/GIF/WebP，≤5MB）。
- **群聊**（类似多人邮箱，消息持久化）：每个职员自动拥有「部门群聊」（仅同部门）与「全员群聊」（全部部门）；分页加载历史 + 5 秒轮询新消息。
- **私聊**：搜索并选择任意职员一对一聊天，消息持久化；**会话列表**按最近消息排序（新消息置顶），收到私聊显示**未读红点+数量**（含侧边栏「私聊」菜单角标），打开会话即标记已读。
- **员工管理**（管理层）：对普通职员增删改查、多条件查询、分页；新增职员默认密码 `123456`，账号（姓名）唯一性校验。
- **信息面板**（管理层）：仪表盘总览与部门/职位分类统计。
- **禁言管理**（管理层）：对普通职员限时/永久禁言；禁言期间不能群聊发言，可查看、可私聊。
- **总裁管理**（总裁）：授予/撤销普通职员的管理权限，管理部门名单管理。
- **安全**：密码 PBKDF2 哈希存储；接口统一角色鉴权（普通职员越权返回 403）；登录 token HMAC 签名。

## 后端接口（`/api/v1`）

| 分组 | 接口 |
|---|---|
| 认证 | `POST /auth/login`、`POST /auth/logout`、`GET /auth/me` |
| 个人中心 | `PUT /me`、`PUT /me/password`、`POST /me/avatar` |
| 群聊 | `GET /groups/my`、`GET/POST /groups/dept/messages`、`GET/POST /groups/all/messages` |
| 私聊 | `GET /contacts`、`GET/POST /private/messages`、`GET /private/conversations`、`POST /private/read`、`GET /private/unread-total` |
| 禁言 | `GET/POST /mutes`、`DELETE /mutes/{id}` |
| 总裁管理 | `GET/POST /managers`、`DELETE /managers/{id}` |
| 员工管理（管理层） | `GET /employees/search`、`POST/PUT/DELETE /employees/{id}` 等 |
| 统计（管理层） | `GET /overview`、`GET /departments`、`GET /jobs` |

## 说明

- 数据库中 `t_employees` 各列均为 `varchar`（含主键 `EMPLOYEE_ID`），ORM 读取主键时为字符串，
  跨表映射处已统一 `int()` 归一化（详见开发问题文档 P15）。
- 新表 `t_group_messages` / `t_private_messages` / `t_mutes` 由 SQLAlchemy 启动时自动创建。
