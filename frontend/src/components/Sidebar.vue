<template>
  <div class="sidebar-container">
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="white" fill-opacity="0.15"/>
            <path d="M8 12C8 10.8954 8.89543 10 10 10H22C23.1046 10 24 10.8954 24 12V20C24 21.1046 23.1046 22 22 22H10C8.89543 22 8 21.1046 8 20V12Z" stroke="white" stroke-width="2"/>
            <path d="M12 15H20M12 18H17" stroke="white" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="logo-text">钱包管家</span>
      </div>
    </div>

    <nav class="sidebar-nav">
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="false"
        router
        background-color="transparent"
        text-color="rgba(255, 255, 255, 0.7)"
        active-text-color="#ffffff"
        :default-openeds="['dashboard']"
      >
        <div class="menu-section-title">概览</div>
        <el-menu-item index="/dashboard" class="menu-item">
          <el-icon><House /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <div class="menu-section-title">管理</div>
        <el-menu-item index="/accounts" class="menu-item">
          <el-icon><Wallet /></el-icon>
          <template #title>账户管理</template>
        </el-menu-item>

        <el-menu-item index="/categories" class="menu-item">
          <el-icon><FolderOpened /></el-icon>
          <template #title>分类管理</template>
        </el-menu-item>

        <el-menu-item index="/transactions" class="menu-item">
          <el-icon><Tickets /></el-icon>
          <template #title>交易记录</template>
        </el-menu-item>

        <el-menu-item index="/budgets" class="menu-item">
          <el-icon><Money /></el-icon>
          <template #title>预算管理</template>
        </el-menu-item>

        <div class="menu-section-title">工具</div>
        <el-menu-item index="/reports" class="menu-item">
          <el-icon><PieChart /></el-icon>
          <template #title>报表分析</template>
        </el-menu-item>

        <el-menu-item index="/import" class="menu-item">
          <el-icon><Upload /></el-icon>
          <template #title>批量导入</template>
        </el-menu-item>

        <el-menu-item index="/backup" class="menu-item">
          <el-icon><DocumentCopy /></el-icon>
          <template #title>数据备份</template>
        </el-menu-item>

        <template v-if="isAdmin">
          <div class="menu-section-title">系统</div>
          <el-menu-item index="/admin/users" class="menu-item">
            <el-icon><Setting /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </template>
      </el-menu>
    </nav>

    <div class="sidebar-footer">
      <div class="version-tag">v1.0.0</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import {
  House,
  Wallet,
  FolderOpened,
  Tickets,
  Money,
  PieChart,
  Upload,
  DocumentCopy,
  Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()

const isAdmin = computed(() => {
  return userStore.user?.username === 'admin'
})

const activeMenu = computed(() => {
  const { path } = route
  if (path.startsWith('/dashboard')) return '/dashboard'
  if (path.startsWith('/accounts')) return '/accounts'
  if (path.startsWith('/categories')) return '/categories'
  if (path.startsWith('/transactions')) return '/transactions'
  if (path.startsWith('/budgets')) return '/budgets'
  if (path.startsWith('/reports')) return '/reports'
  if (path.startsWith('/import')) return '/import'
  if (path.startsWith('/backup')) return '/backup'
  if (path.startsWith('/admin/users')) return '/admin/users'
  return '/dashboard'
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.sidebar-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.sidebar-header {
  padding: $space-lg;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: $space-md;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-family: $font-display;
  font-size: $text-xl;
  font-weight: 700;
  color: white;
  letter-spacing: -0.02em;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: $space-md 0;
}

.sidebar-menu {
  border-right: none;
  background: transparent;

  &:not(.el-menu--collapse) {
    width: 100%;
  }
}

.menu-section-title {
  padding: $space-lg $space-lg $space-sm;
  font-size: $text-xs;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.4);
  margin-top: $space-sm;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 12px;
  border-radius: $radius-md;
  transition: all $transition-base;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 0;
    background: white;
    border-radius: 0 2px 2px 0;
    transition: height $transition-base;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.1) !important;

    .el-icon {
      transform: scale(1.1);
    }
  }

  &.is-active {
    background: rgba(255, 255, 255, 0.15) !important;

    &::before {
      height: 24px;
    }
  }

  .el-icon {
    font-size: 18px;
    transition: transform $transition-base;
  }
}

:deep(.el-menu-item span) {
  font-weight: 500;
  font-size: $text-base;
}

.sidebar-footer {
  padding: $space-lg;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.version-tag {
  text-align: center;
  font-size: $text-xs;
  color: rgba(255, 255, 255, 0.3);
  font-weight: 500;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}
</style>
