<template>
  <div class="backup-container">
    <h2>💾 数据备份与恢复</h2>

    <el-alert
      title="备份文件保存在服务器本地，建议定期下载备份到本地电脑"
      type="info"
      :closable="false"
      show-icon
      class="info-alert"
    />

    <el-tabs v-model="activeTab">
      <!-- 备份管理 -->
      <el-tab-pane label="备份管理" name="backup">
        <!-- 创建备份 -->
        <el-card shadow="hover" class="action-card">
          <template #header>
            <span>创建新备份</span>
          </template>
          <div class="action-row">
            <el-button type="primary" :loading="creating" @click="handleCreate">
              📦 立即备份
            </el-button>
            <span class="action-hint">备份所有交易、账户、分类、标签和预算数据</span>
          </div>
        </el-card>

        <!-- 备份列表 -->
        <el-card shadow="hover" class="list-card">
          <template #header>
            <div class="list-header">
              <span>备份列表</span>
              <el-button size="small" @click="loadBackups" :loading="loading">
                🔄 刷新
              </el-button>
            </div>
          </template>

          <el-table :data="backups" stripe v-loading="loading">
            <el-table-column prop="filename" label="文件名" min-width="280">
              <template #default="{ row }">
                📄 {{ row.filename }}
              </template>
            </el-table-column>
            <el-table-column label="记录数" width="200">
              <template #default="{ row }">
                <span v-if="row.record_counts">
                  交易: {{ row.record_counts.transactions || 0 }} |
                  账户: {{ row.record_counts.accounts || 0 }} |
                  分类: {{ row.record_counts.categories || 0 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="大小" width="100">
              <template #default="{ row }">
                {{ formatSize(row.size_bytes) }}
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.exported_at || row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="handleDownload(row.filename)">
                  ⬇️ 下载
                </el-button>
                <el-button type="warning" size="small" @click="handleRestore(row.filename)">
                  🔄 恢复
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(row.filename)">
                  🗑️ 删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!loading && backups.length === 0" description="暂无备份文件，点击上方【立即备份】创建" />
        </el-card>
      </el-tab-pane>

      <!-- 上传恢复 -->
      <el-tab-pane label="上传恢复" name="upload">
        <el-card shadow="hover">
          <template #header>
            <span>从文件恢复数据</span>
          </template>

          <el-alert
            title="选择之前导出的 JSON 备份文件进行恢复"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 16px;"
          />

          <div class="upload-section">
            <el-upload
              :auto-upload="false"
              :limit="1"
              accept=".json"
              :on-change="handleFileChange"
              drag
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处，或 <em>点击选择</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  仅支持 .json 格式的备份文件
                </div>
              </template>
            </el-upload>

            <div class="restore-options">
              <span style="margin-right: 12px; color: #606266;">恢复模式：</span>
              <el-radio-group v-model="restoreMode">
                <el-radio value="merge">合并模式（保留现有数据）</el-radio>
                <el-radio value="replace">替换模式（清空现有数据）</el-radio>
              </el-radio-group>
            </div>

            <el-button
              type="warning"
              size="large"
              :loading="restoring"
              :disabled="!uploadFile"
              @click="handleUploadRestore"
              style="margin-top: 16px;"
            >
              🔄 开始恢复
            </el-button>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import {
  createBackup,
  listBackups,
  deleteBackup,
  downloadBackup,
  restoreFromBackup,
  restoreFromUpload
} from '@/api/report'

const activeTab = ref('backup')
const loading = ref(false)
const creating = ref(false)
const restoring = ref(false)
const backups = ref<any[]>([])
const uploadFile = ref<File | null>(null)
const restoreMode = ref('merge')

async function loadBackups() {
  loading.value = true
  try {
    const res = await listBackups()
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
    const res = await createBackup()
    const counts = res.data.record_counts
    ElMessage.success(
      `备份创建成功！账户: ${counts.accounts}, 分类: ${counts.categories}, ` +
      `标签: ${counts.tags}, 交易: ${counts.transactions}, 预算: ${counts.budgets}`
    )
    loadBackups()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '备份失败')
  } finally {
    creating.value = false
  }
}

async function handleDownload(filename: string) {
  try {
    const res = await downloadBackup(filename)
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '下载失败')
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
    await deleteBackup(filename)
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
      `确定要从备份 ${filename} 恢复数据吗？`,
      '⚠️ 数据恢复确认',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const mode = restoreMode.value
    const res = await restoreFromBackup(filename, { mode })
    const counts = res.data.restored_counts
    ElMessage.success(
      `恢复成功！账户: ${counts.accounts}, 分类: ${counts.categories}, ` +
      `标签: ${counts.tags}, 交易: ${counts.transactions}, 预算: ${counts.budgets}`
    )
  } catch (err: any) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '恢复失败')
    }
  }
}

function handleFileChange(file: any) {
  uploadFile.value = file.raw
}

async function handleUploadRestore() {
  if (!uploadFile.value) {
    ElMessage.warning('请先选择备份文件')
    return
  }

  if (restoreMode.value === 'replace') {
    try {
      await ElMessageBox.confirm(
        '替换模式将清空当前所有数据！确定要继续吗？',
        '⚠️ 危险操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'error',
        }
      )
    } catch {
      return
    }
  }

  restoring.value = true
  try {
    const res = await restoreFromUpload(uploadFile.value, { mode: restoreMode.value })
    const counts = res.data.restored_counts
    ElMessage.success(
      `恢复成功！账户: ${counts.accounts}, 分类: ${counts.categories}, ` +
      `标签: ${counts.tags}, 交易: ${counts.transactions}, 预算: ${counts.budgets}`
    )
    uploadFile.value = null
    loadBackups()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '恢复失败')
  } finally {
    restoring.value = false
  }
}

function formatSize(bytes: number): string {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function formatDate(dateStr: string | number): string {
  if (!dateStr) return '-'
  if (typeof dateStr === 'number') {
    return new Date(dateStr * 1000).toLocaleString('zh-CN')
  }
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return String(dateStr)
  }
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

.info-alert {
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

.upload-section {
  padding: 16px 0;
}

.restore-options {
  margin-top: 16px;
  display: flex;
  align-items: center;
}
</style>
