import request from './request'

export const getUsers = (skip: number = 0, limit: number = 100) => {
  return request.get('/admin/users', { params: { skip, limit } })
}

export const resetUserPassword = (userId: number, newPassword: string) => {
  return request.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword })
}

export const updateUserStatus = (userId: number, isActive: boolean) => {
  return request.put(`/admin/users/${userId}/status`, { is_active: isActive })
}
