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
        const { data } = response.data  // Now the token is in response.data.data
        const { access_token } = data

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