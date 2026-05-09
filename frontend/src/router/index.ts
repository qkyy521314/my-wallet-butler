import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/accounts',
    name: 'AccountList',
    component: () => import('@/views/AccountList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'CategoryList',
    component: () => import('@/views/CategoryList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/transactions',
    name: 'TransactionList',
    component: () => import('@/views/TransactionList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/budgets',
    name: 'Budget',
    component: () => import('@/views/Budget.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/import',
    name: 'Import',
    component: () => import('@/views/Import.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/backup',
    name: 'Backup',
    component: () => import('@/views/Backup.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && userStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router