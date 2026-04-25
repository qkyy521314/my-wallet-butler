# My Wallet Butler - 个人记账系统

一个现代化的个人财务管理应用，帮助用户跟踪收入、支出、管理预算和生成财务报告。

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Pinia
- **后端**: FastAPI + Python 3.11 + SQLAlchemy 2.0 + asyncmy
- **数据库**: MySQL 8.0
- **部署**: Docker + Docker Compose

## 功能特性

### 用户管理
- 用户注册/登录
- JWT身份验证
- 个人信息管理

### 账户管理
- 多种账户类型（现金、银行卡、信用卡等）
- 账户余额管理
- 账户详情查看

### 分类管理
- 收入/支出分类管理
- 自定义分类

### 交易管理
- 收入/支出/转账记录
- 交易分类标记
- 交易历史查询

### 预算管理
- 按类别设置预算
- 预算执行情况跟踪
- 预警提醒

### 报表分析
- 月度收支统计
- 分类支出占比
- 预算执行报告
- 图形化展示

## 项目结构

```
my-wallet-butler/
├── backend/                 # 后端FastAPI应用
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI入口
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/               # 前端Vue3应用
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── store/          # Pinia状态管理
│   │   ├── api/            # API请求封装
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── types/          # 类型定义
│   │   ├── utils/          # 工具函数
│   │   └── styles/         # 样式文件
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── sql/
│   └── init.sql           # 数据库初始化脚本
├── docker-compose.yml
└── README.md
```

## 快速开始

### 环境准备

1. 确保已安装 Docker 和 Docker Compose
2. 克隆项目仓库

### 启动开发环境

```bash
# 启动数据库服务
docker-compose up -d

# 后端服务
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端服务
cd frontend
npm install
npm run dev
```

### 配置环境变量

复制 `.env.example` 到 `.env` 并修改相应的配置。

## API 接口

所有接口均以 `/api/v1` 作为前缀：

- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /accounts` - 获取账户列表
- `POST /accounts` - 创建账户
- `GET /categories` - 获取分类列表
- `POST /categories` - 创建分类
- `GET /transactions` - 获取交易列表
- `POST /transactions` - 创建交易
- `GET /budgets` - 获取预算列表
- `POST /budgets` - 创建预算
- `GET /reports` - 获取报表数据

## 部署

使用Docker Compose进行一键部署：

```bash
docker-compose up -d
```

## 开发指南

### 后端开发

1. 遵循FastAPI最佳实践
2. 使用Pydantic进行数据验证
3. 使用SQLAlchemy 2.0进行数据库操作
4. 所有路由加`/api/v1`前缀
5. 实现JWT认证机制

### 前端开发

1. 使用TypeScript进行类型安全开发
2. 使用Element Plus组件库
3. 使用Pinia进行状态管理
4. API请求统一通过Axios封装
5. 组件按功能进行拆分

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 许可证

MIT License
