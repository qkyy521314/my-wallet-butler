<template>
  <div class="login-container">
    <!-- Background decoration -->
    <div class="bg-decoration">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
      <div class="bg-pattern"></div>
    </div>

    <div class="login-wrapper">
      <!-- Left side - Branding -->
      <div class="login-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="64" height="64" rx="16" fill="white" fill-opacity="0.15"/>
              <path d="M16 24C16 21.7909 17.7909 20 20 20H44C46.2091 20 48 21.7909 48 24V40C48 42.2091 46.2091 44 44 44H20C17.7909 44 16 42.2091 16 40V24Z" stroke="white" stroke-width="2.5"/>
              <path d="M24 30H40M24 36H34" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="20" cy="20" r="6" fill="#14B8A6"/>
            </svg>
          </div>
          <h1 class="brand-title">我的钱包管家</h1>
          <p class="brand-tagline">智能管理您的每一笔收支</p>

          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><Wallet /></el-icon>
              </div>
              <span>多账户管理</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <span>智能报表分析</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><Lock /></el-icon>
              </div>
              <span>数据安全保障</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right side - Login Form -->
      <div class="login-form-wrapper">
        <div class="login-card">
          <div class="card-header">
            <h2>欢迎回来</h2>
            <p>登录您的账户继续使用</p>
          </div>

          <el-form
            :model="loginForm"
            :rules="rules"
            ref="formRef"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <div class="input-wrapper">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  size="large"
                  :prefix-icon="null"
                />
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-wrapper">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  :prefix-icon="null"
                  show-password
                />
              </div>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="javascript:void(0)" class="forgot-link" @click="showForgotPassword">忘记密码？</a>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                size="large"
                class="login-btn"
              >
                <span v-if="!loading">立即登录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="card-footer">
            <span>还没有账户？</span>
            <router-link to="/register" class="register-link">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Wallet, DataAnalysis, Lock, User } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({
  username: '',
  password: ''
})

const rememberMe = ref(false)
const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const formRef = ref()

const showForgotPassword = () => {
  ElMessageBox.alert(
    '请联系管理员重置密码。管理员可在"用户管理"页面中为您重置密码。',
    '忘记密码',
    { confirmButtonText: '我知道了', type: 'info' }
  )
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      loading.value = true
      userStore.login(loginForm)
        .then(() => {
          ElMessage.success('登录成功，欢迎回来！')
          router.push('/dashboard')
        })
        .catch(err => {
          console.error('Login error:', err)
          ElMessage.error(err.response?.data?.detail || '登录失败，请检查用户名和密码')
        })
        .finally(() => {
          loading.value = false
        })
    }
  })
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0D9488 0%, #134E4A 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: $space-xl;
}

.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  background: white;
}

.shape-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
  animation: float 20s ease-in-out infinite;
}

.shape-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
  animation: float 15s ease-in-out infinite reverse;
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 40%;
  left: 30%;
  animation: float 18s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(10deg); }
}

.bg-pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.login-wrapper {
  display: flex;
  max-width: 1000px;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: $radius-xl;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// Left side - Branding
.login-brand {
  flex: 1;
  background: linear-gradient(180deg, #0D9488 0%, #134E4A 100%);
  padding: $space-2xl;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
  }
}

.brand-content {
  text-align: center;
  color: white;
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: $space-lg;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.brand-title {
  font-family: $font-display;
  font-size: $text-3xl;
  font-weight: 700;
  margin-bottom: $space-sm;
  letter-spacing: -0.02em;
}

.brand-tagline {
  font-size: $text-lg;
  opacity: 0.8;
  margin-bottom: $space-2xl;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: $space-md;
}

.feature-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $space-md;
  font-size: $text-base;
  opacity: 0.9;

  .feature-icon {
    width: 36px;
    height: 36px;
    border-radius: $radius-md;
    background: rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
  }
}

// Right side - Form
.login-form-wrapper {
  flex: 1;
  padding: $space-2xl;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.card-header {
  margin-bottom: $space-xl;

  h2 {
    font-family: $font-display;
    font-size: $text-2xl;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: $space-xs;
  }

  p {
    color: $text-secondary;
    font-size: $text-base;
  }
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: $space-lg;
  }
}

.input-wrapper {
  position: relative;

  .input-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 18px;
    color: $text-tertiary;
    z-index: 1;
  }

  :deep(.el-input__wrapper) {
    padding: 8px 14px 8px 42px;
    border-radius: $radius-md;
    box-shadow: 0 0 0 1px $border-color inset;
    transition: all $transition-base;

    &:hover {
      box-shadow: 0 0 0 1px $gray-400 inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 2px rgba($primary-color, 0.2), 0 0 0 1px $primary-color inset;
    }
  }

  :deep(.el-input__inner) {
    font-size: $text-base;
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $space-lg;

  :deep(.el-checkbox__label) {
    color: $text-secondary;
    font-size: $text-sm;
  }

  .forgot-link {
    font-size: $text-sm;
    color: $primary-color;

    &:hover {
      text-decoration: underline;
    }
  }
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: $text-base;
  font-weight: 600;
  border-radius: $radius-md;
  background: linear-gradient(135deg, $primary-color 0%, $primary-dark 100%);
  border: none;
  transition: all $transition-base;
  letter-spacing: 0.02em;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba($primary-color, 0.35);
  }

  &:active {
    transform: translateY(0);
  }
}

.card-footer {
  text-align: center;
  margin-top: $space-xl;
  padding-top: $space-lg;
  border-top: 1px solid $border-light;
  color: $text-secondary;
  font-size: $text-sm;

  .register-link {
    color: $primary-color;
    font-weight: 600;
    margin-left: $space-xs;

    &:hover {
      text-decoration: underline;
    }
  }
}

// Responsive
@media (max-width: 900px) {
  .login-wrapper {
    flex-direction: column;
  }

  .login-brand {
    padding: $space-xl;
  }

  .brand-features {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }

  .feature-item {
    font-size: $text-sm;

    .feature-icon {
      width: 32px;
      height: 32px;
      font-size: 16px;
    }
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: $space-md;
  }

  .login-wrapper {
    border-radius: $radius-lg;
  }

  .login-brand {
    padding: $space-lg;
  }

  .login-form-wrapper {
    padding: $space-lg;
  }

  .brand-title {
    font-size: $text-xl;
  }

  .brand-tagline {
    font-size: $text-base;
  }
}
</style>
