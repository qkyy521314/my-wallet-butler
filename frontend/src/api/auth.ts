import request from './request'

export const login = (credentials: { username: string, password: string }) => {
  const formData = new FormData()
  formData.append('username', credentials.username)
  formData.append('password', credentials.password)

  return request.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const register = (userData: { username: string, email: string, password: string }) => {
  return request.post('/auth/register', userData)
}

export const getUserInfo = () => {
  return request.get('/auth/me')
}

export const updateUserProfile = (userData: { username?: string, email?: string, first_name?: string, last_name?: string }) => {
  return request.put('/auth/profile', userData)
}

export const logout = () => {
  // 本地清除token即可，后端无需特殊处理
  localStorage.removeItem('token')
  return Promise.resolve({ success: true })
}