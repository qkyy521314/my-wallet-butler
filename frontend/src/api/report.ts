import request from './request'

export const getSummaryReport = (params: { start_date: string, end_date: string, user_id: number }) => {
  return request.get('/report/summary', { params })
}

export const getCategoryAnalysis = (params: { start_date: string, end_date: string, user_id: number, transaction_type?: string }) => {
  return request.get('/report/category-analysis', { params })
}

export const getTrendAnalysis = (params: { start_date: string, end_date: string, user_id: number, group_by?: string }) => {
  return request.get('/report/trend-analysis', { params })
}

export const getMonthlyReport = (params: { year: number, month: number, user_id: number }) => {
  return request.get('/report/monthly-report', { params })
}

export const getBudgetPerformance = (params: { start_date: string, end_date: string, user_id: number }) => {
  return request.get('/report/budget-performance', { params })
}