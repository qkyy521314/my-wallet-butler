import request from './request'

export const getBudgets = (params?: { page?: number, size?: number, year?: number, month?: number }) => {
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

export const getBudgetStats = (id: number) => {
  return request.get(`/budgets/${id}/stats`)
}