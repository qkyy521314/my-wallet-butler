<template>
  <div class="backup-container">
    <h2>数据备份与恢复</h2>

    <el-alert
      title="注意：备份和恢复操作涉及整个数据库，请谨慎操作！"
      type="warning"
      :closable="false"
      show-icon
      class="warning-alert"
    />

    <!-- 创建备份 -->
    <el-card shadow="hover" class="action-card">
      <template #header>
        <span>创建新备份</span>
      </template>
      <div class="action-row">
        <el-button type="primary" :loading="creating" @click="handleCreate">
          <el-icon><Download /></el-icon>
          立即备份
        </el-button>
        <span class="action-hint">备份文件将保存在服务器本地</span>
      </div>
    </el-card>

    <!-- 备份列表 -->
    <el-card shadow="hover" class="list-card">
      <template #header>
        <div class="list-header">
          <span>备份列表</span>
          <el-button size="small" @click="loadBackups" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="backups" stripe v-loading="loading">
        <el-table-column prop="filename" label="文件名" min-width="280">
          <template #default="{ row }">
            <el-icon><Document /></el-icon>
            {{ row.filename }}
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleRestore(row.filename)"
            >
              恢复
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row.filename)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && backups.length === 0" description="暂无备份文件" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Refresh, Document } from '@element-plus/icons-vue'
import { createBackup, listBackups, deleteBackup, restoreBackup } from '../api/report'
import { useUserStore } from '../store/modules/user'

const userStore = useUserStore()
const loading = ref(false)
const creating = ref(false)
const backups = ref<any[]>([])

const userId = computed(() => userStore.user?.id || 0)

async function loadBackups() {
  loading.value = true
  try {
    const res = await listBackups(userId.value)
    backups.value = res.data.backups || []
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '加载备份列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  creating.value = true
  try {
    const res = await createBackup(userId.value)
    ElMessage.success('备份创建成功: ' + res.data.filename)
    loadBackups()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '备份失败')
  } finally {
    creating.value = false
  }
}

async function handleDelete(filename: string) {
  try {
    await ElMessageBox.confirm(
      `确定要删除备份 ${filename} 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await deleteBackup(filename, userId.value)
    ElMessage.success('备份已删除')
    loadBackups()
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '删除失败')
    }
  }
}

async function handleRestore(filename: string) {
  try {
    await ElMessageBox.confirm(
      `确定要从备份 ${filename} 恢复数据吗？当前数据将被覆盖！`,
      '⚠️ 危险操作',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'error',
      }
    )
    const res = await restoreBackup(filename, userId.value)
    ElMessage.success(res.data.message)
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '恢复失败')
    }
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

onMounted(() => {
  loadBackups()
})
</script>

<style scoped>
.backup-container {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.warning-alert {
  margin-bottom: 20px;
}

.action-card {
  margin-bottom: 20px;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-hint {
  color: #909399;
  font-size: 14px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-icon {
  margin-right: 4px;
}
</style>
