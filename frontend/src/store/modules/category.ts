import { defineStore } from 'pinia'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/category'

interface CategoryState {
  categories: any[]
  currentCategory: any | null
}

export const useCategoryStore = defineStore('category', {
  state: (): CategoryState => ({
    categories: [],
    currentCategory: null
  }),

  actions: {
    async fetchCategories() {
      try {
        const response = await getCategories()
        this.categories = response.data.data?.items || []
        return response
      } catch (error) {
        console.error('Failed to fetch categories:', error)
        throw error
      }
    },

    async addCategory(categoryData: any) {
      try {
        const response = await createCategory(categoryData)
        this.categories.push(response.data)
        return response
      } catch (error) {
        console.error('Failed to create category:', error)
        throw error
      }
    },

    async updateCategory(id: number, categoryData: any) {
      try {
        const response = await updateCategory(id, categoryData)
        const index = this.categories.findIndex(category => category.id === id)
        if (index !== -1) {
          this.categories[index] = response.data
        }
        return response
      } catch (error) {
        console.error('Failed to update category:', error)
        throw error
      }
    },

    async removeCategory(id: number) {
      try {
        await deleteCategory(id)
        this.categories = this.categories.filter(category => category.id !== id)
        return { success: true }
      } catch (error) {
        console.error('Failed to delete category:', error)
        throw error
      }
    }
  }
})