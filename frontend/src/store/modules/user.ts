import { defineStore } from 'pinia'
import { login, register, getUserInfo, updateUserProfile, logout } from '@/api/auth'

interface UserState {
  user: any | null
  token: string | null
  isAuthenticated: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token')
  }),

  actions: {
    async login(credentials: { username: string, password: string }) {
      try {
        const response = await login(credentials)
        // 兼容两种返回格式：{data: {access_token}} 和 {data: {code, data: {access_token}}}
        const respData = response.data
        let access_token: string

        if (respData?.data?.access_token) {
          // 后端包装了 SuccessResponse
          access_token = respData.data.access_token
        } else if (respData?.access_token) {
          // 直接返回 token
          access_token = respData.access_token
        } else {
          console.error('Unexpected login response:', respData)
          throw new Error('登录响应格式异常')
        }

        this.token = access_token
        this.isAuthenticated = true
        localStorage.setItem('token', access_token)

        await this.fetchUserInfo()
        return response
      } catch (error) {
        throw error
      }
    },

    async register(userData: { username: string, email: string, password: string }) {
      try {
        const response = await register(userData)
        return response
      } catch (error) {
        throw error
      }
    },

    async fetchUserInfo() {
      try {
        const response = await getUserInfo()
        // Now the user data is in response.data.data
        this.user = response.data.data
        return response
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        this.logout()
        throw error
      }
    },

    async updateProfile(userData: { username?: string, email?: string, first_name?: string, last_name?: string }) {
      try {
        const response = await updateUserProfile(userData)
        // Update the user info in the store
        this.user = response.data.data
        return response
      } catch (error) {
        console.error('Failed to update profile:', error)
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')

      // 跳转到登录页
      window.location.href = '/login'
    }
  }
})