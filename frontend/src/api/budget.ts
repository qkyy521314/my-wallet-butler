import request from './request'

export const getBudgets = (params?: { skip?: number, limit?: number }) => {
  return request.get('/budgets', { params })
}

export const getBudgetById = (id: number) => {
  return request.get(`/budgets/${id}`)
}

export const createBudget = (data: any) => {
  return request.post('/budgets', data)
}

export const updateBudget = (id: number, data: any) => {
  return request.put(`/budgets/${id}`, data)
}

export const deleteBudget = (id: number) => {
  return request.delete(`/budgets/${id}`)
}