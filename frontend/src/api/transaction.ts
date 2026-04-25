import request from './request'

export const getTransactions = (params?: { skip?: number, limit?: number }) => {
  return request.get('/transactions', { params })
}

export const getTransactionById = (id: number) => {
  return request.get(`/transactions/${id}`)
}

export const createTransaction = (data: any) => {
  return request.post('/transactions', data)
}

export const updateTransaction = (id: number, data: any) => {
  return request.put(`/transactions/${id}`, data)
}

export const deleteTransaction = (id: number) => {
  return request.delete(`/transactions/${id}`)
}