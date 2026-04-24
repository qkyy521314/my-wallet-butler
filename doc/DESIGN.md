# my-wallet-butler 项目设计文档

> 版本：v1.0 | 创建时间：2026-04-24

---

## 1. 项目概述

**my-wallet-butler** 是一款个人财务管理系统，帮助用户全面记录和管理个人资产、消费支出、收入来源，提供清晰的财务状况视图和智能分析能力。

### 1.1 核心目标

- 📊 **全面记账**：记录每一笔收入与支出
- 💰 **资产管理**：管理多个账户（现金、银行卡、信用卡、数字钱包等）
- 📈 **财务分析**：可视化报表，消费趋势分析
- 🎯 **预算管理**：设置月度/分类预算，超支提醒
- 🔒 **数据安全**：本地优先，可选云端同步

---

## 2. 功能模块

### 2.1 交易记录模块

| 功能 | 说明 |
|------|------|
| 新增交易 | 支持收入/支出，关联账户和分类 |
| 编辑/删除 | 修改历史记录，支持批量操作 |
| 交易详情 | 金额、时间、分类、账户、备注、标签、附件（截图/小票） |
| 批量导入 | 支持 CSV/Excel 导入，银行流水解析 |
| 重复交易 | 设置周期性自动记录（如月租、工资） |

### 2.2 账户管理模块

| 功能 | 说明 |
|------|------|
| 账户类型 | 现金、储蓄卡、信用卡、数字货币、投资账户、其他 |
| 账户余额 | 实时更新，支持手动调整 |
| 多账户转账 | 账户间转账记录 |
| 账户分组 | 按类型/用途分组管理 |
| 账户冻结/归档 | 不活跃账户隐藏 |

### 2.3 分类管理模块

| 功能 | 说明 |
|------|------|
| 预设分类 | 餐饮、交通、购物、娱乐、住房、医疗、教育等 |
| 自定义分类 | 用户自由创建/修改分类 |
| 多级分类 | 支持一级/二级分类（如 餐饮 → 外卖） |
| 收入/支出分类 | 区分收入来源和支出类别 |
| 分类图标/颜色 | 可视化区分 |

### 2.4 预算管理模块

| 功能 | 说明 |
|------|------|
| 月度预算 | 按分类设置月度支出上限 |
| 年度预算 | 年度总支出/收入目标 |
| 预算提醒 | 达到 80%、100% 时提醒 |
| 预算执行率 | 实时显示预算使用情况 |
| 预算调整 | 支持临时调整预算额度 |

### 2.5 报表分析模块

| 功能 | 说明 |
|------|------|
| 收支概览 | 日/周/月/年收支汇总 |
| 分类饼图 | 各分类支出占比 |
| 趋势折线图 | 收支趋势变化 |
| 账户资产变化 | 各账户余额变化曲线 |
| 同比/环比 | 与上月/去年同期对比 |
| 自定义报表 | 按时间段、分类、账户自定义查询 |
| 导出报表 | PDF/Excel 导出 |

### 2.6 标签系统

| 功能 | 说明 |
|------|------|
| 自定义标签 | 为交易打标签（如 旅行、装修、双11） |
| 标签筛选 | 按标签筛选交易记录 |
| 标签统计 | 按标签汇总支出 |

### 2.7 目标储蓄

| 功能 | 说明 |
|------|------|
| 创建目标 | 设置储蓄目标（如 买电脑 5000 元） |
| 进度追踪 | 可视化进度条 |
| 定期存入 | 关联自动转账 |
| 目标提醒 | 达成进度提醒 |

---

## 3. 数据模型

### 3.1 核心实体

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Account   │────<│ Transaction  │>────│  Category    │
│  (账户)     │  1:N │  (交易记录)  │  N:1 │  (分类)     │
└─────────────┘     └──────────────┘     └──────────────┘
                           │
                           │ N:M
                           ▼
                     ┌──────────────┐
                     │    Tag       │
                     │  (标签)      │
                     └──────────────┘

┌─────────────┐     ┌──────────────┐
│   Budget    │>────│   Category   │
│  (预算)     │  1:1 │  (分类)     │
└─────────────┘     └──────────────┘

┌─────────────┐
│    Goal     │
│  (储蓄目标)  │
└─────────────┘
```

### 3.2 字段定义

#### Account（账户）
```
id, name, type, currency, balance, icon, color, 
is_active, created_at, updated_at, notes
```

#### Transaction（交易记录）
```
id, type (income/expense/transfer), amount, currency,
account_id, category_id, payee, date, notes,
tags[], attachments[], is_recurring, recurring_rule,
created_at, updated_at
```

#### Category（分类）
```
id, name, type (income/expense), parent_id,
icon, color, sort_order, is_system, created_at
```

#### Tag（标签）
```
id, name, color, created_at
```

#### Budget（预算）
```
id, category_id, amount, period (monthly/yearly),
start_date, end_date, alert_threshold, created_at
```

#### Goal（储蓄目标）
```
id, name, target_amount, current_amount, 
deadline, icon, created_at, updated_at
```

---

## 4. 技术架构

### 4.1 技术栈选型

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + TypeScript + Vite | 主框架 |
| **移动端** | UniApp / Taro | 跨平台（可选） |
| **UI 组件** | Element Plus / Naive UI | 桌面端 |
| **状态管理** | Pinia | 数据状态 |
| **后端** | Python + FastAPI | API 服务 |
| **数据库** | MySQL 8.x | 数据存储（Docker 容器） |
| **ORM** | SQLAlchemy 2.x (Async) | 数据访问 |
| **认证** | JWT (python-jose / PyJWT) | 用户认证 |
| **部署** | Docker + Nginx | 容器化部署 |

### 4.2 架构模式

```
┌─────────────────────────────────────────────────┐
│                  用户界面层                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Web 端  │  │ 移动端   │  │ CLI 端   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
└───────┼──────────────┼──────────────┼────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│                  API 网关层                       │
│         RESTful API / GraphQL (可选)             │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│                  业务逻辑层                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │交易服务  │  │账户服务  │  │报表服务  │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────────────┬──────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────┐
│                  数据访问层                       │
│         SQLAlchemy ORM → MySQL (Docker)         │
└─────────────────────────────────────────────────┘
```

---

## 5. 项目目录结构

```
my-wallet-butler/
├── doc/                    # 项目文档
│   ├── DESIGN.md           # 设计文档（本文件）
│   ├── API.md              # API 文档
│   └── DATABASE.md         # 数据库设计
├── server/                 # 后端服务 (Python + FastAPI)
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── v1/
│   │   │   │   ├── transactions.py
│   │   │   │   ├── accounts.py
│   │   │   │   ├── categories.py
│   │   │   │   └── reports.py
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py   # 配置管理
│   │   │   ├── security.py # 认证/加密
│   │   │   └── database.py # 数据库连接
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # FastAPI 入口
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── web/                    # Web 前端 (Vue 3 + Vite)
│   ├── src/
│   │   ├── api/            # API 调用封装
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 公共组件
│   │   ├── composables/    # 组合式函数
│   │   ├── layouts/        # 布局组件
│   │   ├── pages/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── styles/         # 全局样式
│   │   ├── utils/          # 工具函数
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── mobile/                 # 移动端（可选）
├── docker/                 # Docker 配置
├── .env.example            # 环境变量示例
├── docker-compose.yml      # Docker Compose
└── README.md
```

---

## 6. API 设计（概要）

### 6.1 交易相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/transactions` | 获取交易列表（分页/筛选） |
| POST | `/api/transactions` | 新增交易 |
| GET | `/api/transactions/:id` | 获取交易详情 |
| PUT | `/api/transactions/:id` | 更新交易 |
| DELETE | `/api/transactions/:id` | 删除交易 |
| POST | `/api/transactions/import` | 批量导入 |

### 6.2 账户相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/accounts` | 获取账户列表 |
| POST | `/api/accounts` | 新增账户 |
| PUT | `/api/accounts/:id` | 更新账户 |
| DELETE | `/api/accounts/:id` | 删除账户 |
| POST | `/api/accounts/transfer` | 账户间转账 |

### 6.3 分类相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/categories` | 获取分类列表 |
| POST | `/api/categories` | 新增分类 |
| PUT | `/api/categories/:id` | 更新分类 |
| DELETE | `/api/categories/:id` | 删除分类 |

### 6.4 报表相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/reports/summary` | 收支概览 |
| GET | `/api/reports/category` | 分类统计 |
| GET | `/api/reports/trend` | 趋势分析 |
| GET | `/api/reports/budget` | 预算执行情况 |

---

## 7. 开发计划

### Phase 1：基础框架（1-2 周）
- [ ] 项目初始化，技术栈搭建
- [ ] 数据库设计与建模
- [ ] 用户认证系统
- [ ] 账户 CRUD

### Phase 2：核心功能（2-3 周）
- [ ] 交易记录 CRUD
- [ ] 分类管理
- [ ] 标签系统
- [ ] 转账功能

### Phase 3：分析报表（1-2 周）
- [ ] 收支概览
- [ ] 分类饼图/趋势图
- [ ] 月度/年度报表

### Phase 4：高级功能（2-3 周）
- [ ] 预算管理
- [ ] 目标储蓄
- [ ] 批量导入
- [ ] 周期性交易

### Phase 5：移动端 & 优化（持续）
- [ ] 移动端适配 / React Native
- [ ] 数据同步
- [ ] 性能优化
- [ ] 用户体验打磨

---

## 8. 非功能需求

### 8.1 性能
- 列表加载 < 500ms
- 报表生成 < 2s
- 支持 10 万+ 交易记录

### 8.2 安全
- 用户数据隔离
- 敏感数据加密存储
- HTTPS 传输
- 操作日志审计

### 8.3 可用性
- 响应式设计（桌面 + 平板 + 手机）
- 离线支持（PWA）
- 数据备份与恢复

---

## 10. 开发环境配置

### 10.1 Docker MySQL 容器

```yaml
# docker-compose.yml (数据库)
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: wallet-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: your_root_password
      MYSQL_DATABASE: wallet_butler
      MYSQL_USER: wallet_user
      MYSQL_PASSWORD: your_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  mysql_data:
```

### 10.2 后端 Python 环境

```bash
# 创建虚拟环境
cd server
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# requirements.txt 核心依赖：
# fastapi==0.115.0
# uvicorn[standard]==0.32.0
# sqlalchemy[asyncio]==2.0.36
# aiomysql==0.2.0
# aiosqlite==0.20.0
# pydantic==2.9.0
# pydantic-settings==2.6.0
# python-jose[cryptography]==3.3.0
# passlib[bcrypt]==1.7.4
# python-multipart==0.0.17
# alembic==1.13.0
# httpx==0.27.0
# pytest==8.3.0
```

### 10.3 前端 Vue 环境

```bash
# 创建 Vue 项目
cd web
npm create vite@latest . -- --template vue-ts

# 安装核心依赖
npm install vue-router@4 pinia axios element-plus @element-plus/icons-vue
npm install -D unplugin-auto-import unplugin-vue-components
```

---

## 9. 待决策事项

| 事项 | 选项 | 状态 |
|------|------|------|
| 数据库选型 | SQLite（单机）vs PostgreSQL（多用户） | 待决策 |
| 部署方式 | 本地 Docker 部署 | 已决策 |
| 移动端方案 | UniApp vs Taro vs 不做 | 待决策 |
| 是否支持多币种 | 是 vs 否 | 待决策 |
| 是否需要社交功能 | 家庭共享 vs 纯个人 | 待决策 |

---

_文档维护：开发过程中持续更新_
