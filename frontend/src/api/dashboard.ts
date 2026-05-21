import request from './request'

// 仪表盘概览
export interface DashboardSummary {
  total_assets: number
  monthly_income: number
  monthly_expense: number
  balance: number
}

export const getDashboardSummary = () => {
  return request.get<DashboardSummary>('/dashboard/summary')
}

// 最近交易
export interface RecentTransaction {
  id: number
  description: string
  amount: number
  date: string | null
  category: {
    name: string | null
  }
}

export const getRecentTransactions = (limit: number = 5) => {
  return request.get<{ transactions: RecentTransaction[] }>('/dashboard/recent-transactions', {
    params: { limit }
  })
}

// 账户余额
export interface AccountBalance {
  id: number
  name: string
  type: string
  balance: number
}

export const getAccountBalances = () => {
  return request.get<{ accounts: AccountBalance[] }>('/dashboard/account-balances')
}

// 预算概览
export interface BudgetOverview {
  category: string
  spent: number
  limit: number
  percent: number
}

export const getBudgetOverview = () => {
  return request.get<{ budgets: BudgetOverview[] }>('/dashboard/budget-overview')
}
