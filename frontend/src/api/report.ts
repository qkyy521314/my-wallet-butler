import request from './request'

export const getSummary = () => {
  return request.get('/report/summary')
}

export const getTransactionStatistics = () => {
  return request.get('/report/transaction-statistics')
}

export const getCategoryAnalysis = () => {
  return request.get('/report/category-analysis')
}

export const getBudgetPerformance = () => {
  return request.get('/report/budget-performance')
}