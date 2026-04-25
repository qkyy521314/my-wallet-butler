-- My Wallet Butler 数据库初始化脚本

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建账户表
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    account_type VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建分类表
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_type VARCHAR(20) NOT NULL, -- income, expense
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建交易表
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    transaction_type VARCHAR(20) NOT NULL, -- income, expense, transfer
    category_id INTEGER REFERENCES categories(id),
    account_id INTEGER REFERENCES accounts(id), -- 主账户（对于转账来说是目标账户）
    from_account_id INTEGER REFERENCES accounts(id), -- 转出账户（仅用于转账）
    to_account_id INTEGER REFERENCES accounts(id),   -- 转入账户（仅用于转账）
    date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建标签表
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    color VARCHAR(7), -- Hex color code
    is_active BOOLEAN DEFAULT TRUE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建交易标签关联表
CREATE TABLE IF NOT EXISTS transaction_tags (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE(transaction_id, tag_id)
);

-- 创建预算表
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount DECIMAL(10, 2) NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    spent_amount DECIMAL(10, 2) DEFAULT 0.00,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_over_spent BOOLEAN DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_accounts_user_id ON accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_category_id ON budgets(category_id);
CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_transaction_tags_transaction ON transaction_tags(transaction_id);
CREATE INDEX IF NOT EXISTS idx_transaction_tags_tag ON transaction_tags(tag_id);

-- 插入默认分类
INSERT INTO categories (name, description, category_type, user_id, created_at) VALUES
('工资', '工资收入', 'income', 1, NOW()),
('奖金', '奖金收入', 'income', 1, NOW()),
('投资收益', '股票、基金等投资收益', 'income', 1, NOW()),
('食品', '食物支出', 'expense', 1, NOW()),
('住房', '房租或房贷', 'expense', 1, NOW()),
('交通', '交通费用', 'expense', 1, NOW()),
('医疗', '医疗健康支出', 'expense', 1, NOW()),
('娱乐', '娱乐活动支出', 'expense', 1, NOW()),
('教育', '教育培训支出', 'expense', 1, NOW()),
('购物', '购物消费', 'expense', 1, NOW());

-- 插入默认账户
INSERT INTO accounts (name, balance, account_type, description, user_id, created_at) VALUES
('招商银行储蓄卡', 10000.00, 'bank_card', '主要储蓄账户', 1, NOW()),
('现金', 2000.00, 'cash', '日常现金', 1, NOW()),
('支付宝', 1500.00, 'e_wallet', '电子钱包', 1, NOW()),
('信用卡', 0.00, 'credit_card', '信用卡账户', 1, NOW());