import { defineStore } from 'pinia'
import { getAccounts, createAccount, updateAccount, deleteAccount } from '@/api/account'

interface AccountState {
  accounts: any[]
  currentAccount: any | null
}

export const useAccountStore = defineStore('account', {
  state: (): AccountState => ({
    accounts: [],
    currentAccount: null
  }),

  actions: {
    async fetchAccounts() {
      try {
        const response = await getAccounts()
        this.accounts = response.data.data?.items || response.data.data || []
        return response
      } catch (error) {
        console.error('Failed to fetch accounts:', error)
        throw error
      }
    },

    async addAccount(accountData: any) {
      try {
        const response = await createAccount(accountData)
        this.accounts.push(response.data)
        return response
      } catch (error) {
        console.error('Failed to create account:', error)
        throw error
      }
    },

    async updateAccount(id: number, accountData: any) {
      try {
        const response = await updateAccount(id, accountData)
        const index = this.accounts.findIndex(account => account.id === id)
        if (index !== -1) {
          this.accounts[index] = response.data
        }
        return response
      } catch (error) {
        console.error('Failed to update account:', error)
        throw error
      }
    },

    async removeAccount(id: number) {
      try {
        await deleteAccount(id)
        this.accounts = this.accounts.filter(account => account.id !== id)
        return { success: true }
      } catch (error) {
        console.error('Failed to delete account:', error)
        throw error
      }
    }
  }
})