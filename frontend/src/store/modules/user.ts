import { defineStore } from 'pinia'
import { login, register, getUserInfo, logout } from '@/api/auth'

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
        const { access_token } = response.data

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
        this.user = response.data
        return response
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        this.logout()
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