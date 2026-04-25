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
}

.el-aside {
  background-color: #545c64;
  color: #fff;
  height: 100vh;
  overflow: hidden;
}

.el-header {
  background-color: #fff;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  padding: 0 20px;
  z-index: 100;
}

.el-main {
  background-color: #f0f2f5;
  padding: 0;
}
</style>