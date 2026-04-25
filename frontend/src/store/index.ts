import { createPinia } from 'pinia'
import { useUserStore } from './modules/user'
import { useAccountStore } from './modules/account'
import { useCategoryStore } from './modules/category'

export { useUserStore, useAccountStore, useCategoryStore }

export default createPinia()