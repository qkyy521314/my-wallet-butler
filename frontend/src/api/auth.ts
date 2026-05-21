import request from './request'

export const login = (credentials: { username: string, password: string }) => {
  // OAuth2PasswordRequestForm 期望 application/x-www-form-urlencoded 格式
  const params = new URLSearchParams()
  params.append('username', credentials.username)
  params.append('password', credentials.password)

  return request.post('/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export const register = (userData: { username: string, email: string, password: string }) => {
  return request.post('/register', userData)
}

export const getUserInfo = () => {
  return request.get('/me')
}

export const getMe = getUserInfo

export const updateUserProfile = (userData: { username?: string, email?: string, first_name?: string, last_name?: string }) => {
  return request.put('/profile', userData)
}

export const logout = () => {
  // 本地清除token即可，后端无需特殊处理
  localStorage.removeItem('token')
  return Promise.resolve({ success: true })
}