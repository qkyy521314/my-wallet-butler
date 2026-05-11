<template>
  <el-container class="layout-container">
    <el-aside width="200px" v-if="!isLoginPage && !isRegisterPage">
      <Sidebar />
    </el-aside>
    <el-container>
      <el-header v-if="!isLoginPage && !isRegisterPage">
        <Header />
      </el-header>
      <el-main>
        <slot />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from './Header.vue'
import Sidebar from './Sidebar.vue'

const route = useRoute()

const isLoginPage = computed(() => route.path === '/login')
const isRegisterPage = computed(() => route.path === '/register')
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
}

.el-aside {
  background-color: #545c64;
  color: #fff;
  height: 100vh;
  overflow: hidden;
  flex-shrink: 0;
}

.el-header {
  background-color: #fff;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  padding: 0 20px;
  height: 60px;
  z-index: 100;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

/* 确保内部容器占满剩余高度 */
.layout-container > .el-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  flex: 1;
}
</style>