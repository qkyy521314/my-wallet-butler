<template>
  <div class="register-container">
    <!-- Background decoration -->
    <div class="bg-decoration">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
      <div class="bg-pattern"></div>
    </div>

    <div class="register-wrapper">
      <!-- Left side - Branding -->
      <div class="register-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="64" height="64" rx="16" fill="white" fill-opacity="0.15"/>
              <path d="M16 24C16 21.7909 17.7909 20 20 20H44C46.2091 20 48 21.7909 48 24V40C48 42.2091 46.2091 44 44 44H20C17.7909 44 16 42.2091 16 40V24Z" stroke="white" stroke-width="2.5"/>
              <path d="M24 30H40M24 36H34" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="20" cy="20" r="6" fill="#14B8A6"/>
            </svg>
          </div>
          <h1 class="brand-title">开始理财之旅</h1>
          <p class="brand-tagline">注册成为钱包管家用户</p>

          <div class="brand-benefits">
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>免费使用所有功能</span>
            </div>
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>数据安全加密存储</span>
            </div>
            <div class="benefit-item">
              <el-icon><Check /></el-icon>
              <span>实时同步多设备</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right side - Register Form -->
      <div class="register-form-wrapper">
        <div class="register-card">
          <div class="card-header">
            <h2>创建账户</h2>
            <p>填写以下信息完成注册</p>
          </div>

          <el-form
            :model="registerForm"
            :rules="rules"
            ref="formRef"
            class="register-form"
            label-position="top"
          >
            <el-form-item label="用户名" prop="username">
              <div class="input-wrapper">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名 (3-20个字符)"
                  size="large"
                />
              </div>
            </el-form-item>

            <el-form-item label="邮箱地址" prop="email">
              <div class="input-wrapper">
                <el-icon class="input-icon"><Message /></el-icon>
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱地址"
                  size="large"
                  type="email"
                />
              </div>
            </el-form-item>

            <el-form-item label="登录密码" prop="password">
              <div class="input-wrapper">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码 (至少6位)"
                  size="large"
                  show-password
                />
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleRegister"
                :loading="loading"
                size="large"
                class="register-btn"
              >
                <span v-if="!loading">立即注册</span>
                <span v-else>注册中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="card-footer">
            <span>已有账户？</span>
            <router-link to="/login" class="login-link">立即登录</router-link>
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
import { ElMessage } from 'element-plus'
import { User, Message, Lock, Check } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const registerForm = reactive({
  username: '',
  email: '',
  password: ''
})

const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const formRef = ref()

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      loading.value = true
      userStore.register(registerForm)
        .then(() => {
          ElMessage.success('注册成功！请登录')
          router.push('/login')
        })
        .catch(err => {
          console.error('Registration error:', err)
          ElMessage.error(err.response?.data?.detail || '注册失败，请稍后重试')
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

.register-container {
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
  left: -100px;
  animation: float 18s ease-in-out infinite;
}

.shape-2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  right: -100px;
  animation: float 22s ease-in-out infinite reverse;
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 30%;
  right: 30%;
  animation: float 16s ease-in-out infinite;
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

.register-wrapper {
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
.register-brand {
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

.brand-benefits {
  display: flex;
  flex-direction: column;
  gap: $space-md;
}

.benefit-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $space-md;
  font-size: $text-base;
  opacity: 0.9;

  .el-icon {
    font-size: 18px;
    color: $success-color;
    background: rgba($success-color, 0.2);
    border-radius: 50%;
    padding: 4px;
  }
}

// Right side - Form
.register-form-wrapper {
  flex: 1;
  padding: $space-2xl;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-card {
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

.register-form {
  :deep(.el-form-item) {
    margin-bottom: $space-lg;
  }

  :deep(.el-form-item__label) {
    font-weight: 500;
    color: $text-primary;
    padding-bottom: $space-xs;
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

.register-btn {
  width: 100%;
  height: 48px;
  font-size: $text-base;
  font-weight: 600;
  border-radius: $radius-md;
  background: linear-gradient(135deg, $primary-color 0%, $primary-dark 100%);
  border: none;
  transition: all $transition-base;
  letter-spacing: 0.02em;
  margin-top: $space-md;

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

  .login-link {
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
  .register-wrapper {
    flex-direction: column;
  }

  .register-brand {
    padding: $space-xl;
  }

  .brand-benefits {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .register-container {
    padding: $space-md;
  }

  .register-wrapper {
    border-radius: $radius-lg;
  }

  .register-brand {
    padding: $space-lg;
  }

  .register-form-wrapper {
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
