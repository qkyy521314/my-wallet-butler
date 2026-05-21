import request from './request'

export const getAccounts = (params?: { page?: number, size?: number }) => {
  return request.get('/accounts', { params })
}

export const getAccountById = (id: number) => {
  return request.get(`/accounts/${id}`)
}

export const createAccount = (data: any) => {
  return request.post('/accounts', data)
}

export const updateAccount = (id: number, data: any) => {
  return request.put(`/accounts/${id}`, data)
}

export const deleteAccount = (id: number) => {
  return request.delete(`/accounts/${id}`)
}