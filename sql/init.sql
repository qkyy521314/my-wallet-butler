-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS wallet_butler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE wallet_butler;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建账户表
CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'CNY',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建分类表
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_type ENUM('income', 'expense') NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建交易表
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    transaction_type ENUM('income', 'expense', 'transfer') NOT NULL,
    category_id INT,
    account_id INT NOT NULL,
    from_account_id INT,
    to_account_id INT,
    date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (from_account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (to_account_id) REFERENCES accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建标签表
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    color VARCHAR(7), -- Hex color code
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建预算表
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    spent_amount DECIMAL(10, 2) DEFAULT 0.00,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 插入初始数据
-- 插入一个管理员用户
INSERT INTO users (username, email, hashed_password, first_name, last_name, is_active, is_verified) VALUES
('admin', 'admin@example.com', '$2b$12$VcCDgh2NDk07Jj91yJ53vObCyt8/T5Zsg97BMzQECKC3MJqYUPfz2', 'Admin', 'User', TRUE, TRUE); -- 密码: password

-- 插入默认账户类型
INSERT INTO accounts (name, account_type, balance, currency, description, user_id) VALUES
('现金', 'cash', 1000.00, 'CNY', '日常现金', 1),
('招商银行储蓄卡', 'bank', 5000.00, 'CNY', '主要储蓄账户', 1),
('信用卡', 'credit_card', 0.00, 'CNY', '招商银行信用卡', 1);

-- 插入默认分类
INSERT INTO categories (name, category_type, description, user_id) VALUES
('工资', 'income', '工作收入', 1),
('奖金', 'income', '额外奖励收入', 1),
('食品', 'expense', '购买食物开销', 1),
('交通', 'expense', '出行交通费用', 1),
('住房', 'expense', '房租/房贷', 1),
('娱乐', 'expense', '休闲娱乐开销', 1);

-- 插入示例交易
INSERT INTO transactions (amount, description, transaction_type, category_id, account_id, date, user_id) VALUES
(8000.00, '1月份工资', 'income', 1, 2, '2023-01-15 09:00:00', 1),
(-300.00, '超市购物', 'expense', 3, 1, '2023-01-16 18:30:00', 1),
(-50.00, '地铁费用', 'expense', 4, 1, '2023-01-16 19:00:00', 1),
(-2000.00, '1月份房租', 'expense', 5, 2, '2023-01-01 10:00:00', 1);