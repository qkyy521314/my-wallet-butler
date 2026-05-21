<template>
  <div class="admin-users-page">
    <div class="page-header">
      <div>
        <h1>用户管理</h1>
        <p>管理系统用户，重置密码、启用/禁用账户</p>
      </div>
    </div>

    <el-card shadow="never" class="users-card">
      <el-table :data="users" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openResetDialog(row)">
              重置密码
            </el-button>
            <el-button
              size="small"
              :type="row.is_active ? 'danger' : 'success'"
              @click="toggleStatus(row)"
              :disabled="row.username === currentUser?.username"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 重置密码对话框 -->
    <el-dialog v-model="resetDialogVisible" title="重置密码" width="420px" :close-on-click-modal="false">
      <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-width="80px">
        <el-form-item label="用户">
          <span>{{ resetForm.username }}</span>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="resetForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="resetForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword" :loading="resetLoading">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, resetUserPassword, updateUserStatus } from '@/api/admin'
import { useUserStore } from '@/store/modules/user'

const userStore = useUserStore()
const currentUser = computed(() => userStore.user)

const users = ref<any[]>([])
const loading = ref(false)

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers()
    users.value = res.data?.data || res.data || []
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 重置密码
const resetDialogVisible = ref(false)
const resetLoading = ref(false)
const resetFormRef = ref()
const resetForm = reactive({
  userId: 0,
  username: '',
  newPassword: '',
  confirmPassword: ''
})

const resetRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== resetForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const openResetDialog = (user: any) => {
  resetForm.userId = user.id
  resetForm.username = user.username
  resetForm.newPassword = ''
  resetForm.confirmPassword = ''
  resetDialogVisible.value = true
}

const handleResetPassword = async () => {
  const valid = await resetFormRef.value?.validate().catch(() => false)
  if (!valid) return

  resetLoading.value = true
  try {
    await resetUserPassword(resetForm.userId, resetForm.newPassword)
    ElMessage.success(`已重置用户 "${resetForm.username}" 的密码`)
    resetDialogVisible.value = false
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '重置密码失败')
  } finally {
    resetLoading.value = false
  }
}

// 启用/禁用
const toggleStatus = async (user: any) => {
  const action = user.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      '确认操作',
      { type: 'warning' }
    )
    await updateUserStatus(user.id, !user.is_active)
    ElMessage.success(`已${action}用户 "${user.username}"`)
    await loadUsers()
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err?.response?.data?.detail || `${action}用户失败`)
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped lang="scss">
.admin-users-page {
  .page-header {
    margin-bottom: 24px;
    h1 { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
    p { color: #8b8fa8; font-size: 14px; }
  }
}

.users-card {
  border-radius: 12px;
  border: 1px solid #f0f1f5;
}
</style>
