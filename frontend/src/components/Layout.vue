<template>
  <el-container class="layout-container">
    <el-aside width="260px" v-if="!isLoginPage && !isRegisterPage" class="app-sidebar">
      <Sidebar />
    </el-aside>
    <el-container class="main-wrapper">
      <el-header v-if="!isLoginPage && !isRegisterPage" class="app-header">
        <Header />
      </el-header>
      <el-main class="app-main">
        <div class="page-content">
          <slot />
        </div>
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

<style scoped lang="scss">
@import '@/styles/variables.scss';

.layout-container {
  height: 100vh;
  display: flex;
  background-color: $bg-main;
}

.app-sidebar {
  background: $bg-sidebar;
  width: 260px !important;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 10;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    opacity: 0.5;
    pointer-events: none;
  }
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  background-color: $bg-header;
  border-bottom: 1px solid $border-light;
  box-shadow: $shadow-sm;
  padding: 0 $space-xl;
  height: 64px !important;
  z-index: 5;
  display: flex;
  align-items: center;
}

.app-main {
  background-color: $bg-main;
  padding: 0;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.page-content {
  padding: $space-xl;
  max-width: 1600px;
  margin: 0 auto;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// Responsive adjustments
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: -260px;
    transition: left 0.3s ease;
    z-index: 100;

    &.is-open {
      left: 0;
    }
  }

  .page-content {
    padding: $space-md;
  }
}
</style>
