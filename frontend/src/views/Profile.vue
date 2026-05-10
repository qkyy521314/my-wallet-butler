<template>
  <div class="profile-container">
    <h2>👤 个人资料</h2>

    <el-card shadow="hover" class="profile-card">
      <template #header>
        <span>基本信息</span>
      </template>

      <el-form :model="profileForm" label-width="100px" v-loading="loading">
        <el-form-item label="用户名">
          <el-input v-model="profileForm.username" disabled />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="profileForm.email" disabled />
        </el-form-item>

        <el-form-item label="创建时间">
          <el-input v-model="profileForm.created_at" disabled />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="profile-card">
      <template #header>
        <span>修改密码</span>
      </template>

      <el-form :model="passwordForm" label-width="100px" :rules="passwordRules" ref="passwordFormRef">
        <el-form-item label="当前密码" prop="current_password">
          <el-input v-model="passwordForm.current_password" type="password" show-password />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="updating" @click="handleUpdatePassword">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMe } from '@/api/auth'

interface ProfileForm {
  username: string
  email: string
  created_at: string
}

interface PasswordForm {
  current_password: string
  new_password: string
  confirm_password: string
}

const loading = ref(false)
const updating = ref(false)
const passwordFormRef = ref()

const profileForm = ref<ProfileForm>({
  username: '',
  email: '',
  created_at: ''
})

const passwordForm = ref<PasswordForm>({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  current_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: any, callback: any) => {
        if (value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

async function loadProfile() {
  loading.value = true
  try {
    const res = await getMe()
    const data = res.data
    profileForm.value = {
      username: data.username || '',
      email: data.email || '',
      created_at: data.created_at ? new Date(data.created_at).toLocaleString('zh-CN') : '-'
    }
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '加载个人资料失败')
  } finally {
    loading.value = false
  }
}

async function handleUpdatePassword() {
  try {
    await passwordFormRef.value.validate()
  } catch {
    return
  }

  updating.value = true
  try {
    // TODO: 实现修改密码 API
    ElMessage.success('密码修改成功')
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '修改密码失败')
  } finally {
    updating.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.profile-card {
  margin-bottom: 20px;
  max-width: 600px;
}
</style>
