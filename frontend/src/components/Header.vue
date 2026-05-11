<template>
  <div class="header-container">
    <div class="logo">
      <h3>我的钱包管家</h3>
    </div>
    <div class="user-info">
      <el-dropdown @command="handleCommand">
        <span class="el-dropdown-link">
          <el-avatar :size="30" :src="avatar" />
          <span class="username">{{ user?.username || '用户' }}</span>
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="settings">设置</el-dropdown-item>
            <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 用户头像，可以是默认头像或来自用户信息
const avatar = computed(() => 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')

// 当前用户信息
const user = computed(() => userStore.user)

// 下拉菜单命令处理
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
    default:
      break
  }
}
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  width: 100%;
}

.logo h3 {
  margin: 0;
  color: #409EFF;
  font-size: 18px;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.username {
  margin: 0 10px;
  color: #333;
  font-size: 14px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.el-dropdown-link:hover {
  background-color: #f5f7fa;
}

:deep(.el-icon--right) {
  margin-left: 4px;
}
</style>