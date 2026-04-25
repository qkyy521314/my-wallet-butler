// 用户类型定义
export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at?: string
}

// 账户类型定义
export interface Account {
  id: number
  name: string
  account_type: string
  balance: number
  currency: string
  description?: string
  is_active: boolean
  user_id: number
  created_at: string
  updated_at?: string
}

// 分类类型定义
export interface Category {
  id: number
  name: string
  category_type: 'income' | 'expense'
  description?: string
  is_active: boolean
  user_id: number
  created_at: string
  updated_at?: string
}

// 交易类型定义
export interface Transaction {
  id: number
  amount: number
  description?: string
  transaction_type: 'income' | 'expense' | 'transfer'
  category_id?: number
  account_id: number
  from_account_id?: number
  to_account_id?: number
  date: string
  is_active: boolean
  user_id: number
  created_at: string
  updated_at?: string
}

// 标签类型定义
export interface Tag {
  id: number
  name: string
  description?: string
  color: string
  is_active: boolean
  user_id: number
  created_at: string
  updated_at?: string
}

// 预算类型定义
export interface Budget {
  id: number
  name: string
  category_id: number
  amount: number
  period_start: string
  period_end: string
  spent_amount: number
  description?: string
  is_active: boolean
  user_id: number
  created_at: string
  updated_at?: string
}

// 通用响应类型定义
export interface ApiResponse<T> {
  success: boolean
  message?: string
  data?: T
  error_code?: string
}

// 分页响应类型定义
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  total_pages: number
}

// Token类型定义
export interface Token {
  access_token: string
  token_type: string
}