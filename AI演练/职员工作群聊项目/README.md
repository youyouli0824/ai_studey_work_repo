# 职工信息管理系统

基于 **Vue 3 + Vite + Element Plus + ECharts** 的前端，配合 **FastAPI + MySQL** 后端，
实现对职工信息的增删改查、分页浏览、多条件查询、分类统计与仪表盘总览。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3（组合式 API）、Vite 7、Vue Router、Element Plus、Axios、ECharts |
| 后端 | FastAPI、SQLAlchemy、PyMySQL（`MySQL_Project_backend/`） |
| 数据库 | MySQL（`my-first-sql` 库，`t_employees` 107 条样例数据） |

## 目录结构

```
连接数据库的Vue项目/
├── MySQL_Project_backend/   # FastAPI 后端（原有，已扩展新接口）
├── index.html
├── package.json
├── vite.config.js           # @ 别名、/api 代理到 8000
├── public/
└── src/
    ├── main.js              # 入口（Element Plus 中文 locale + 路由）
    ├── style.css            # 全局主题
    ├── router/              # 路由（/dashboard /employees /stats）
    ├── api/index.js         # Axios 封装 + 全部接口函数
    ├── utils/               # 格式化工具 + 中文映射字典
    ├── components/ChartBox.vue   # ECharts 通用封装
    ├── layout/MainLayout.vue     # 侧边栏 + 顶栏布局
    └── views/
        ├── Dashboard.vue    # 仪表盘（统计卡片 + 4 图表 + 最近入职）
        ├── EmployeeList.vue # 员工管理（增删改查 + 多条件查询 + 分页）
        └── EmployeeStats.vue# 分类统计（部门 / 职位明细）
```

## 运行方法

### 1. 启动后端（端口 8000）

```bash
cd MySQL_Project_backend
python -m uvicorn main:app --reload --port 8000
```

> 数据库连接配置在 `MySQL_Project_backend/database.py` 中，如账号密码不同请自行修改。

### 2. 启动前端（端口 5173）

```bash
# 首次运行先安装依赖
npm install

# 开发模式
npm run dev
```

浏览器访问 http://localhost:5173 （若 5173 被占用，Vite 会自动改用其它端口，以终端提示为准）。
开发模式下 `/api` 请求由 Vite 代理到 `http://127.0.0.1:8000`，无需额外配置跨域。

### 3. 生产构建

```bash
npm run build     # 产物输出到 dist/
```

## 功能清单

- **仪表盘**：员工 / 部门 / 职位总数、平均/最高/最低薪资统计卡片；各部门人数分布、各部门平均薪资、
  各职位人数占比、入职年份趋势四张图表；最近入职员工列表。
- **员工管理**：新增、编辑、单个/批量删除员工；姓名/邮箱关键字、部门、职位、薪资区间、入职日期区间
  多条件组合查询；服务端分页（每页 10/20/50/100 可切换）。
- **分类统计**：部门维度（员工数、占比、平均薪资）与职位维度（员工数、薪资区间）明细表，附分布图表。
- **中文界面**：所有字段名、表头、按钮、提示均为中文；部门/职位展示中文名（映射缺失时回退英文）。

## 后端接口（`/api/v1`）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/employees/search` | 组合查询 + 分页，返回 `{total, page, page_size, items}` |
| GET | `/employees` | 基础分页列表（skip / limit） |
| GET | `/employees/{id}` | 按 ID 查询 |
| POST | `/employees` | 新增（ID 由后端自动生成） |
| PUT | `/employees/{id}` | 更新 |
| DELETE | `/employees/{id}` | 删除（204） |
| GET | `/find/{name}` | 姓名模糊查找 |
| GET | `/departments` | 部门列表 |
| GET | `/jobs` | 职位列表 |
| GET | `/overview` | 仪表盘总览统计 |

## 说明

- 数据库中 `t_employees` 各列均为 `varchar`（含主键 `EMPLOYEE_ID`，无自增），后端在数值聚合与新增
  时已做转数值处理，新增编号取当前最大值 + 1。
- 后端原新增接口存在主键无默认值导致插入失败的问题，本次已在 `create_employee` 中修复。
