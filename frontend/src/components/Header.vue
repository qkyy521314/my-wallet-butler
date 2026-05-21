<template>
  <header class="app-header">
    <div class="header-left">
      <div class="page-title">
        <h2>{{ pageTitle }}</h2>
      </div>
    </div>

    <div class="header-right">
      <div class="header-actions">
        <el-tooltip content="刷新数据" placement="bottom">
          <el-button class="action-btn" circle @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-tooltip>
      </div>

      <el-dropdown @command="handleCommand" trigger="click" class="user-dropdown">
        <div class="user-info">
          <el-avatar :size="36" class="user-avatar">
            <img :src="avatar" alt="avatar" />
          </el-avatar>
          <div class="user-details">
            <span class="username">{{ user?.username || '用户' }}</span>
            <span class="user-role">个人账户</span>
          </div>
          <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="user-dropdown-menu">
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { Refresh, ArrowDown, User, Setting, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/accounts': '账户管理',
    '/categories': '分类管理',
    '/transactions': '交易记录',
    '/budgets': '预算管理',
    '/reports': '报表分析',
    '/import': '批量导入',
    '/backup': '数据备份',
    '/profile': '个人资料',
    '/settings': '系统设置',
    '/login': '登录',
    '/register': '注册'
  }
  return titles[route.path] || '仪表盘'
})

const avatar = computed(() =>
  'https://api.dicebear.com/7.x/avataaars/svg?seed=wallet-butler'
)

const user = computed(() => userStore.user)

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      userStore.logout()
      break
  }
}

const handleRefresh = () => {
  window.location.reload()
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
  padding: 0 $space-xl;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title h2 {
  font-family: $font-display;
  font-size: $text-2xl;
  font-weight: 600;
  color: $text-primary;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: $space-lg;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $space-sm;
}

.action-btn {
  border: 1px solid $border-color;
  background: white;
  color: $text-secondary;
  transition: all $transition-base;

  &:hover {
    border-color: $primary-color;
    color: $primary-color;
    background: rgba($primary-color, 0.05);
  }
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: $space-md;
  padding: $space-sm $space-md;
  border-radius: $radius-lg;
  transition: background-color $transition-base;

  &:hover {
    background-color: $gray-50;
  }
}

.user-avatar {
  background: linear-gradient(135deg, $primary-color 0%, $primary-light 100%);
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 600;
  color: $text-primary;
  font-size: $text-sm;
  line-height: 1.3;
}

.user-role {
  font-size: $text-xs;
  color: $text-tertiary;
}

.dropdown-arrow {
  color: $text-tertiary;
  font-size: 14px;
  margin-left: $space-xs;
  transition: transform $transition-fast;
}

.user-dropdown:hover .dropdown-arrow {
  transform: translateY(2px);
}

// Dropdown menu styling
:deep(.user-dropdown-menu) {
  border-radius: $radius-lg;
  padding: $space-sm;
  border: 1px solid $border-color;
  box-shadow: $shadow-lg;

  .el-dropdown-menu__item {
    border-radius: $radius-md;
    padding: 10px 16px;
    font-size: $text-sm;
    color: $text-secondary;
    display: flex;
    align-items: center;
    gap: $space-sm;
    transition: all $transition-base;

    .el-icon {
      font-size: 16px;
    }

    &:hover {
      background: rgba($primary-color, 0.08);
      color: $primary-color;
    }

    &.el-dropdown-menu__item--divided {
      margin-top: $space-sm;
      padding-top: $space-md;
      border-top: 1px solid $border-light;
    }
  }
}

// Responsive
@media (max-width: 768px) {
  .app-header {
    padding: 0 $space-md;
  }

  .user-details {
    display: none;
  }

  .page-title h2 {
    font-size: $text-lg;
  }
}
</style>
