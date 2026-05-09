<template>
  <div class="sidebar-container">
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical"
      :collapse="false"
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><House /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>

      <el-menu-item index="/accounts">
        <el-icon><Wallet /></el-icon>
        <span>账户管理</span>
      </el-menu-item>

      <el-menu-item index="/categories">
        <el-icon><FolderOpened /></el-icon>
        <span>分类管理</span>
      </el-menu-item>

      <el-menu-item index="/transactions">
        <el-icon><Tickets /></el-icon>
        <span>交易记录</span>
      </el-menu-item>

      <el-menu-item index="/budgets">
        <el-icon><Money /></el-icon>
        <span>预算管理</span>
      </el-menu-item>

      <el-menu-item index="/reports">
        <el-icon><PieChart /></el-icon>
        <span>报表分析</span>
      </el-menu-item>

      <el-menu-item index="/import">
        <el-icon><Upload /></el-icon>
        <span>批量导入</span>
      </el-menu-item>

      <el-menu-item index="/backup">
        <el-icon><DocumentCopy /></el-icon>
        <span>数据备份</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  House,
  Wallet,
  FolderOpened,
  Tickets,
  Money,
  PieChart,
  Upload,
  DocumentCopy
} from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => {
  const { path } = route
  // 匹配当前激活的菜单项
  if (path.startsWith('/dashboard')) return '/dashboard'
  if (path.startsWith('/accounts')) return '/accounts'
  if (path.startsWith('/categories')) return '/categories'
  if (path.startsWith('/transactions')) return '/transactions'
  if (path.startsWith('/budgets')) return '/budgets'
  if (path.startsWith('/reports')) return '/reports'
  if (path.startsWith('/import')) return '/import'
  if (path.startsWith('/backup')) return '/backup'
  return '/dashboard'
})
</script>

<style scoped>
.sidebar-container {
  height: 100%;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}
</style>