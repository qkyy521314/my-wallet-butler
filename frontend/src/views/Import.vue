<template>
  <div class="import-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>批量导入交易记录</h3>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="card">
        <el-tab-pane label="CSV 导入" name="csv">
          <div class="import-section">
            <h4>上传 CSV 文件</h4>
            <el-upload
              class="upload-demo"
              drag
              :action="uploadAction"
              :headers="uploadHeaders"
              :data="{ user_id: 1 }"
              :accept="'.csv'"
              :on-success="handleCsvSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeCsvUpload"
              :auto-upload="false"
              ref="csvUploadRef"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽 CSV 文件到这里 或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请确保 CSV 文件包含以下列: amount, description, category, account
                </div>
              </template>
            </el-upload>

            <div class="controls">
              <el-button type="primary" @click="submitCsvUpload" :loading="csvLoading">上传</el-button>
              <el-button @click="previewCsvFile">预览</el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Excel 导入" name="excel">
          <div class="import-section">
            <h4>上传 Excel 文件</h4>
            <el-upload
              class="upload-demo"
              drag
              :action="uploadAction"
              :headers="uploadHeaders"
              :data="{ user_id: 1 }"
              :accept="'.xlsx,.xls'"
              :on-success="handleExcelSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeExcelUpload"
              :auto-upload="false"
              ref="excelUploadRef"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽 Excel 文件到这里 或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请确保 Excel 文件包含以下列: amount, description, category, account
                </div>
              </template>
            </el-upload>

            <div class="controls">
              <el-button type="primary" @click="submitExcelUpload" :loading="excelLoading">上传</el-button>
              <el-button @click="previewExcelFile">预览</el-button>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="导入预览" name="preview">
          <div class="preview-section" v-if="previewData && previewData.length > 0">
            <h4>预览数据 (前 {{ previewRows }} 行)</h4>
            <el-table :data="previewData" style="width: 100%" max-height="400">
              <el-table-column
                v-for="column in previewColumns"
                :key="column"
                :prop="column"
                :label="column"
                show-overflow-tooltip
              />
            </el-table>
            <div class="total-rows">总计: {{ totalPreviewRows }} 行</div>
          </div>
          <div v-else class="no-preview">
            <el-empty description="暂无预览数据，请先上传文件并预览" />
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="result-section" v-if="importResult">
        <h4>导入结果</h4>
        <el-card class="result-card">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总处理行数">{{ importResult.total_processed }}</el-descriptions-item>
            <el-descriptions-item label="成功导入">{{ importResult.successful_imports }}</el-descriptions-item>
            <el-descriptions-item label="失败行数" :content-style="{ color: '#F56C6C' }">
              {{ importResult.failed_imports }}
            </el-descriptions-item>
            <el-descriptions-item label="成功率">
              {{ importResult.total_processed > 0
                ? ((importResult.successful_imports / importResult.total_processed) * 100).toFixed(2) + '%'
                : '0%' }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="error-list" v-if="importResult.errors && importResult.errors.length > 0">
            <h5>错误详情</h5>
            <el-table :data="importResult.errors" style="width: 100%" stripe>
              <el-table-column prop="row" label="行号" width="80" />
              <el-table-column label="错误信息">
                <template #default="scope">
                  <div v-for="(error, index) in scope.row.errors" :key="index" class="error-item">
                    {{ error }}
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { previewCSV, previewExcel, uploadCSV, uploadExcel } from '@/api/import'

// 响应式数据
const activeTab = ref('csv')
const csvLoading = ref(false)
const excelLoading = ref(false)
const previewData = ref<any[]>([])
const previewColumns = ref<string[]>([])
const totalPreviewRows = ref(0)
const importResult = ref<any>(null)
const previewRows = ref(10)

// 上传配置
const uploadAction = '/api/v1/import/upload-csv' // 实际请求会根据类型动态更改
const uploadHeaders = {
  // 这里可以添加认证头
}

// 上传引用
const csvUploadRef = ref()
const excelUploadRef = ref()

// 上传 CSV
const submitCsvUpload = async () => {
  if (!csvUploadRef.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  const fileList = csvUploadRef.value.uploadFiles
  if (fileList.length === 0) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }

  csvLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', fileList[0].raw)
    formData.append('user_id', '1')

    const response = await uploadCSV(formData)
    importResult.value = response.data
    ElMessage.success('CSV 文件上传成功！')
  } catch (error) {
    console.error('CSV upload error:', error)
    ElMessage.error('CSV 文件上传失败')
  } finally {
    csvLoading.value = false
  }
}

// 上传 Excel
const submitExcelUpload = async () => {
  if (!excelUploadRef.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  const fileList = excelUploadRef.value.uploadFiles
  if (fileList.length === 0) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }

  excelLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', fileList[0].raw)
    formData.append('user_id', '1')

    const response = await uploadExcel(formData)
    importResult.value = response.data
    ElMessage.success('Excel 文件上传成功！')
  } catch (error) {
    console.error('Excel upload error:', error)
    ElMessage.error('Excel 文件上传失败')
  } finally {
    excelLoading.value = false
  }
}

// 预览 CSV
const previewCsvFile = async () => {
  if (!csvUploadRef.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  const fileList = csvUploadRef.value.uploadFiles
  if (fileList.length === 0) {
    ElMessage.warning('请先选择要预览的文件')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', fileList[0].raw)
    formData.append('rows', previewRows.value.toString())

    const response = await previewCSV(formData)
    previewData.value = response.data.preview_data
    previewColumns.value = response.data.columns
    totalPreviewRows.value = response.data.total_rows

    activeTab.value = 'preview'
    ElMessage.success('CSV 文件预览加载成功！')
  } catch (error) {
    console.error('CSV preview error:', error)
    ElMessage.error('CSV 文件预览失败')
  }
}

// 预览 Excel
const previewExcelFile = async () => {
  if (!excelUploadRef.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  const fileList = excelUploadRef.value.uploadFiles
  if (fileList.length === 0) {
    ElMessage.warning('请先选择要预览的文件')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', fileList[0].raw)
    formData.append('rows', previewRows.value.toString())

    const response = await previewExcel(formData)
    previewData.value = response.data.preview_data
    previewColumns.value = response.data.columns
    totalPreviewRows.value = response.data.total_rows

    activeTab.value = 'preview'
    ElMessage.success('Excel 文件预览加载成功！')
  } catch (error) {
    console.error('Excel preview error:', error)
    ElMessage.error('Excel 文件预览失败')
  }
}

// 上传成功回调
const handleCsvSuccess = (response: any) => {
  ElMessage.success('CSV 文件上传成功！')
  importResult.value = response
}

const handleExcelSuccess = (response: any) => {
  ElMessage.success('Excel 文件上传成功！')
  importResult.value = response
}

const handleUploadError = (error: any) => {
  console.error('Upload error:', error)
  ElMessage.error('文件上传失败')
}

const beforeCsvUpload = (file: File) => {
  const isCsv = file.type === 'text/csv' || file.name.toLowerCase().endsWith('.csv')
  if (!isCsv) {
    ElMessage.error('只能上传 CSV 文件!')
    return false
  }
  return true
}

const beforeExcelUpload = (file: File) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel' ||
                  file.name.toLowerCase().endsWith('.xlsx') ||
                  file.name.toLowerCase().endsWith('.xls')

  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件(.xlsx/.xls)!')
    return false
  }
  return true
}
</script>

<style scoped>
.import-page {
  padding: 20px;
}

.card-header h3 {
  margin: 0;
}

.import-section {
  padding: 20px 0;
}

.import-section h4 {
  margin-bottom: 15px;
}

.controls {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.preview-section {
  padding: 20px 0;
}

.total-rows {
  margin-top: 10px;
  text-align: right;
  color: #909399;
  font-size: 14px;
}

.no-preview {
  text-align: center;
  padding: 40px 0;
}

.result-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.result-card {
  margin-top: 10px;
}

.error-list {
  margin-top: 15px;
}

.error-item {
  color: #F56C6C;
  font-size: 13px;
  line-height: 1.5;
}
</style>