import request from './request'

export const login = (credentials: { username: string, password: string }) => {
  const formData = new FormData()
  formData.append('username', credentials.username)
  formData.append('password', credentials.password)

  return request.post('/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const register = (userData: { username: string, email: string, password: string }) => {
  return request.post('/register', userData)
}

export const getUserInfo = () => {
  return request.get('/users/me')
}

export const logout = () => {
  // 本地清除token即可，后端无需特殊处理
  localStorage.removeItem('token')
  return Promise.resolve({ success: true })
}