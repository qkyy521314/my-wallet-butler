import request from './request'

export const getCategories = (params?: { page?: number, size?: number }) => {
  return request.get('/categories', { params })
}

export const getCategoryById = (id: number) => {
  return request.get(`/categories/${id}`)
}

export const createCategory = (data: any) => {
  return request.post('/categories', data)
}

export const updateCategory = (id: number, data: any) => {
  return request.put(`/categories/${id}`, data)
}

export const deleteCategory = (id: number) => {
  return request.delete(`/categories/${id}`)
}