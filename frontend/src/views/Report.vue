<template>
  <div class="report-page">
    <!-- 日期范围选择 -->
    <el-card class="filter-card">
      <div class="filter-row">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="loadData"
        />
        <el-button-group class="quick-select">
          <el-button size="small" @click="setQuickRange('month')">本月</el-button>
          <el-button size="small" @click="setQuickRange('quarter')">本季度</el-button>
          <el-button size="small" @click="setQuickRange('year')">本年度</el-button>
        </el-button-group>
      </div>
    </el-card>

    <!-- 收支概览 -->
    <el-card class="summary-card">
      <template #header>
        <h3>💰 收支概览</h3>
      </template>
      <div class="summary-grid">
        <el-card class="summary-item">
          <div class="summary-content">
            <div class="summary-icon income">💰</div>
            <div class="summary-info">
              <div class="summary-title">总收入</div>
              <div class="summary-value income">{{ formatCurrency(summary.total_income || 0) }}</div>
            </div>
          </div>
        </el-card>
        <el-card class="summary-item">
          <div class="summary-content">
            <div class="summary-icon expense">💸</div>
            <div class="summary-info">
              <div class="summary-title">总支出</div>
              <div class="summary-value expense">{{ formatCurrency(summary.total_expense || 0) }}</div>
            </div>
          </div>
        </el-card>
        <el-card class="summary-item">
          <div class="summary-content">
            <div class="summary-icon net">📊</div>
            <div class="summary-info">
              <div class="summary-title">净收入</div>
              <div class="summary-value" :class="summary.net_income >= 0 ? 'income' : 'expense'">
                {{ formatCurrency(summary.net_income || 0) }}
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <!-- 分类支出占比饼图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header-row">
            <h3>🍩 分类支出占比</h3>
            <el-radio-group v-model="analysisType" size="small" @change="loadCategoryData">
              <el-radio-button label="expense">支出</el-radio-button>
              <el-radio-button label="income">收入</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="pieChartRef" style="height: 350px;"></div>
      </el-card>

      <!-- 收支趋势折线图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header-row">
            <h3>📈 收支趋势</h3>
            <el-radio-group v-model="trendGroupBy" size="small" @change="loadTrendData">
              <el-radio-button label="day">按天</el-radio-button>
              <el-radio-button label="week">按周</el-radio-button>
              <el-radio-button label="month">按月</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="lineChartRef" style="height: 350px;"></div>
      </el-card>
    </div>

    <!-- 月度报表 -->
    <el-card class="monthly-card">
      <template #header>
        <h3>📅 月度报表</h3>
      </template>
      <div class="monthly-controls">
        <el-date-picker
          v-model="monthlyDate"
          type="month"
          format="YYYY-MM"
          value-format="YYYY-MM"
          placeholder="选择年月"
          @change="loadMonthlyReport"
        />
      </div>

      <div v-if="monthlyReport.summary" class="monthly-summary">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="总收入">{{ formatCurrency(monthlyReport.summary.total_income) }}</el-descriptions-item>
          <el-descriptions-item label="总支出">{{ formatCurrency(monthlyReport.summary.total_expense) }}</el-descriptions-item>
          <el-descriptions-item label="净收入">
            <span :style="{ color: monthlyReport.summary.net_income >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ formatCurrency(monthlyReport.summary.net_income) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="monthlyReport.category_analysis?.categories?.length" class="monthly-categories">
        <h4>分类支出详情</h4>
        <el-table :data="monthlyReport.category_analysis.categories" stripe>
          <el-table-column prop="category_name" label="分类名称" />
          <el-table-column prop="amount" label="金额">
            <template #default="scope">
              {{ formatCurrency(scope.row.amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比(%)" />
        </el-table>
      </div>

      <div v-if="monthlyReport.budget_performance?.length" class="monthly-budgets">
        <h4>预算执行情况</h4>
        <el-table :data="monthlyReport.budget_performance" stripe>
          <el-table-column prop="name" label="预算名称" />
          <el-table-column prop="category_name" label="分类" />
          <el-table-column prop="budget_amount" label="预算金额">
            <template #default="scope">
              {{ formatCurrency(scope.row.budget_amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="spent_amount" label="已花费">
            <template #default="scope">
              {{ formatCurrency(scope.row.spent_amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="percentage_used" label="执行率(%)" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag
                :type="scope.row.is_over_spent ? 'danger' : scope.row.percentage_used >= 80 ? 'warning' : 'success'"
              >
                {{ scope.row.is_over_spent ? '超支' : scope.row.percentage_used >= 80 ? '警戒' : '正常' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 数据导出 -->
    <el-card class="export-card">
      <template #header>
        <h3>📤 数据导出</h3>
      </template>
      <div class="export-controls">
        <el-alert
          title="导出当前日期范围内的交易记录"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        />
        <el-space>
          <el-button type="success" @click="handleExportCSV" :loading="exporting">
            📄 导出 CSV
          </el-button>
          <el-button type="primary" @click="handleExportExcel" :loading="exporting">
            📊 导出 Excel
          </el-button>
        </el-space>
      </div>
    </el-card>

    <!-- 数据备份与恢复 -->
    <el-card class="backup-card">
      <template #header>
        <h3>💾 数据备份与恢复</h3>
      </template>

      <el-tabs v-model="backupTab">
        <!-- 备份管理 -->
        <el-tab-pane label="备份管理" name="backup">
          <div class="backup-actions">
            <el-button type="primary" @click="handleCreateBackup" :loading="backingUp">
              📦 创建新备份
            </el-button>
            <el-button @click="loadBackupList" :loading="loadingBackups">
              🔄 刷新列表
            </el-button>
          </div>

          <el-table :data="backupList" stripe v-if="backupList.length">
            <el-table-column prop="filename" label="文件名" min-width="250" />
            <el-table-column label="记录数" width="200">
              <template #default="scope">
                <span v-if="scope.row.record_counts">
                  交易: {{ scope.row.record_counts.transactions || 0 }} |
                  账户: {{ scope.row.record_counts.accounts || 0 }} |
                  分类: {{ scope.row.record_counts.categories || 0 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="大小" width="100">
              <template #default="scope">
                {{ formatFileSize(scope.row.size_bytes) }}
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.exported_at || scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="scope">
                <el-button size="small" @click="handleDownloadBackup(scope.row.filename)">
                  ⬇️ 下载
                </el-button>
                <el-popconfirm
                  title="确定删除此备份？"
                  @confirm="handleDeleteBackup(scope.row.filename)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">🗑️ 删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无备份" />
        </el-tab-pane>

        <!-- 数据恢复 -->
        <el-tab-pane label="数据恢复" name="restore">
          <el-alert
            title="从备份文件恢复数据"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 16px;"
          />

          <div class="restore-section">
            <h4>方式一：从已有备份恢复</h4>
            <el-select v-model="selectedBackup" placeholder="选择备份文件" style="width: 300px; margin-right: 12px;">
              <el-option
                v-for="b in backupList"
                :key="b.filename"
                :label="b.filename"
                :value="b.filename"
              />
            </el-select>
            <el-radio-group v-model="restoreMode" style="margin-right: 12px;">
              <el-radio label="merge">合并模式</el-radio>
              <el-radio label="replace">替换模式（清空现有数据）</el-radio>
            </el-radio-group>
            <el-button type="warning" @click="handleRestoreFromBackup" :loading="restoring" :disabled="!selectedBackup">
              🔄 恢复数据
            </el-button>
          </div>

          <el-divider />

          <div class="restore-section">
            <h4>方式二：上传备份文件恢复</h4>
            <el-upload
              :auto-upload="false"
              :limit="1"
              accept=".json"
              :on-change="handleFileChange"
            >
              <el-button type="primary">📁 选择 JSON 备份文件</el-button>
            </el-upload>
            <div style="margin-top: 12px;">
              <el-radio-group v-model="restoreMode" style="margin-right: 12px;">
                <el-radio label="merge">合并模式</el-radio>
                <el-radio label="replace">替换模式（清空现有数据）</el-radio>
              </el-radio-group>
              <el-button type="warning" @click="handleRestoreFromUpload" :loading="restoring" :disabled="!uploadFile">
                🔄 从文件恢复
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  getSummaryReport,
  getCategoryAnalysis,
  getTrendAnalysis,
  getMonthlyReport,
  exportTransactionsCSV,
  exportTransactionsExcel,
  createBackup,
  listBackups,
  downloadBackup,
  deleteBackup,
  restoreFromBackup,
  restoreFromUpload
} from '@/api/report'
import { ElMessage } from 'element-plus'

// ============ 数据 ============
const summary = ref({ total_income: 0, total_expense: 0, net_income: 0 })
const categoryData = ref<any[]>([])
const trendData = ref<any[]>([])
const monthlyReport = ref<any>({ summary: null, category_analysis: null, budget_performance: [] })

// ============ 控制器 ============
const dateRange = ref<[string, string]>([
  new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
  new Date().toISOString().split('T')[0]
])
const analysisType = ref('expense')
const trendGroupBy = ref('day')
const monthlyDate = ref(new Date().toISOString().slice(0, 7))

// ============ 图表 ============
const pieChartRef = ref<HTMLDivElement>()
const lineChartRef = ref<HTMLDivElement>()
let pieChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

// ============ 导出状态 ============
const exporting = ref(false)

// ============ 备份状态 ============
const backupTab = ref('backup')
const backupList = ref<any[]>([])
const loadingBackups = ref(false)
const backingUp = ref(false)
const restoring = ref(false)
const selectedBackup = ref('')
const restoreMode = ref('merge')
const uploadFile = ref<File | null>(null)

// ============ 生命周期 ============
onMounted(() => {
  nextTick(() => {
    initCharts()
  })
  loadData()
  loadBackupList()
})

onUnmounted(() => {
  if (pieChart) pieChart.dispose()
  if (lineChart) lineChart.dispose()
})

// ============ 快速日期选择 ============
const setQuickRange = (range: string) => {
  const now = new Date()
  let start: Date

  if (range === 'month') {
    start = new Date(now.getFullYear(), now.getMonth(), 1)
  } else if (range === 'quarter') {
    const quarter = Math.floor(now.getMonth() / 3)
    start = new Date(now.getFullYear(), quarter * 3, 1)
  } else {
    start = new Date(now.getFullYear(), 0, 1)
  }

  dateRange.value = [
    start.toISOString().split('T')[0],
    now.toISOString().split('T')[0]
  ]
  loadData()
}

// ============ 加载数据 ============
const loadData = async () => {
  if (!dateRange.value || dateRange.value.length < 2) return

  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    }

    const [summaryRes, categoryRes] = await Promise.all([
      getSummaryReport(params),
      getCategoryAnalysis({ ...params, transaction_type: analysisType.value })
    ])

    summary.value = summaryRes.data
    categoryData.value = categoryRes.data.categories || []

    renderPieChart()
    loadTrendData()
  } catch (error: any) {
    console.error('Failed to load data:', error)
    ElMessage.error('加载数据失败')
  }
}

const loadCategoryData = () => {
  loadData()
}

const loadTrendData = async () => {
  if (!dateRange.value || dateRange.value.length < 2) return

  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      group_by: trendGroupBy.value
    }

    const res = await getTrendAnalysis(params)
    trendData.value = res.data.trend_data || []
    renderLineChart()
  } catch (error: any) {
    console.error('Failed to load trend data:', error)
  }
}

const loadMonthlyReport = async () => {
  if (!monthlyDate.value) return

  try {
    const [year, month] = monthlyDate.value.split('-').map(Number)
    const res = await getMonthlyReport({ year, month })
    monthlyReport.value = res.data
  } catch (error: any) {
    console.error('Failed to load monthly report:', error)
    ElMessage.error('加载月度报告失败')
  }
}

// ============ 图表渲染 ============
const initCharts = () => {
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }
  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value)
  }

  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  if (pieChart) pieChart.resize()
  if (lineChart) lineChart.resize()
}

const renderPieChart = () => {
  if (!pieChart) return

  const chartData = categoryData.value.map((item: any) => ({
    value: item.amount,
    name: item.category_name
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [{
      name: analysisType.value === 'expense' ? '支出分类' : '收入分类',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%'
      },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' }
      },
      data: chartData
    }]
  }

  pieChart.setOption(option, true)
}

const renderLineChart = () => {
  if (!lineChart) return

  const dates = trendData.value.map((item: any) => item.date)
  const incomes = trendData.value.map((item: any) => item.income)
  const expenses = trendData.value.map((item: any) => item.expense)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        let result = params[0].axisValue + '<br/>'
        params.forEach((param: any) => {
          result += param.marker + param.seriesName + ': ¥' + param.value.toLocaleString() + '<br/>'
        })
        return result
      }
    },
    legend: { data: ['收入', '支出'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: { rotate: dates.length > 15 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '¥{value}' }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        smooth: true,
        data: incomes,
        itemStyle: { color: '#67C23A' },
        areaStyle: { color: 'rgba(103, 194, 58, 0.15)' }
      },
      {
        name: '支出',
        type: 'line',
        smooth: true,
        data: expenses,
        itemStyle: { color: '#F56C6C' },
        areaStyle: { color: 'rgba(245, 108, 108, 0.15)' }
      }
    ]
  }

  lineChart.setOption(option, true)
}

// ============ 导出功能 ============
const handleExportCSV = async () => {
  exporting.value = true
  try {
    const res = await exportTransactionsCSV({
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    })
    downloadBlob(res.data, `transactions_${Date.now()}.csv`)
    ElMessage.success('CSV 导出成功')
  } catch (error: any) {
    console.error('CSV export failed:', error)
    ElMessage.error('CSV 导出失败')
  } finally {
    exporting.value = false
  }
}

const handleExportExcel = async () => {
  exporting.value = true
  try {
    const res = await exportTransactionsExcel({
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    })
    downloadBlob(res.data, `transactions_${Date.now()}.xlsx`)
    ElMessage.success('Excel 导出成功')
  } catch (error: any) {
    console.error('Excel export failed:', error)
    ElMessage.error('Excel 导出失败')
  } finally {
    exporting.value = false
  }
}

const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// ============ 备份功能 ============
const loadBackupList = async () => {
  loadingBackups.value = true
  try {
    const res = await listBackups()
    backupList.value = res.data.backups || []
  } catch (error: any) {
    console.error('Failed to load backup list:', error)
    ElMessage.error('加载备份列表失败')
  } finally {
    loadingBackups.value = false
  }
}

const handleCreateBackup = async () => {
  backingUp.value = true
  try {
    const res = await createBackup()
    ElMessage.success(`备份创建成功！${JSON.stringify(res.data.record_counts)}`)
    loadBackupList()
  } catch (error: any) {
    console.error('Backup failed:', error)
    ElMessage.error('备份创建失败')
  } finally {
    backingUp.value = false
  }
}

const handleDownloadBackup = async (filename: string) => {
  try {
    const res = await downloadBackup(filename)
    downloadBlob(res.data, filename)
    ElMessage.success('下载成功')
  } catch (error: any) {
    console.error('Download failed:', error)
    ElMessage.error('下载失败')
  }
}

const handleDeleteBackup = async (filename: string) => {
  try {
    await deleteBackup(filename)
    ElMessage.success('备份已删除')
    loadBackupList()
  } catch (error: any) {
    console.error('Delete failed:', error)
    ElMessage.error('删除失败')
  }
}

// ============ 恢复功能 ============
const handleRestoreFromBackup = async () => {
  if (!selectedBackup.value) {
    ElMessage.warning('请先选择备份文件')
    return
  }

  if (restoreMode.value === 'replace') {
    ElMessage.warning('替换模式将清空当前所有数据，请确认！')
  }

  restoring.value = true
  try {
    const res = await restoreFromBackup(selectedBackup.value, {
      mode: restoreMode.value
    })
    ElMessage.success(`恢复成功！${JSON.stringify(res.data.restored_counts)}`)
    loadData()
  } catch (error: any) {
    console.error('Restore failed:', error)
    ElMessage.error('恢复失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    restoring.value = false
  }
}

const handleFileChange = (file: any) => {
  uploadFile.value = file.raw
}

const handleRestoreFromUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请先选择备份文件')
    return
  }

  if (restoreMode.value === 'replace') {
    ElMessage.warning('替换模式将清空当前所有数据，请确认！')
  }

  restoring.value = true
  try {
    const res = await restoreFromUpload(uploadFile.value, {
      mode: restoreMode.value
    })
    ElMessage.success(`恢复成功！${JSON.stringify(res.data.restored_counts)}`)
    uploadFile.value = null
    loadData()
  } catch (error: any) {
    console.error('Restore failed:', error)
    ElMessage.error('恢复失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    restoring.value = false
  }
}

// ============ 工具函数 ============
const formatCurrency = (value: number) => {
  return '¥ ' + parseFloat(value || 0).toFixed(2)
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDate = (dateStr: string | number) => {
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
</script>

<style scoped>
.report-page {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.quick-select {
  margin-left: auto;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.summary-item {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}

.summary-content {
  display: flex;
  align-items: center;
}

.summary-icon {
  font-size: 28px;
  margin-right: 12px;
}

.summary-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 22px;
  font-weight: bold;
}

.summary-value.income { color: #67C23A; }
.summary-value.expense { color: #F56C6C; }

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 900px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  margin-bottom: 0;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.monthly-card, .export-card, .backup-card {
  margin-bottom: 20px;
}

.monthly-controls {
  margin-bottom: 16px;
}

.monthly-summary, .monthly-categories, .monthly-budgets {
  margin-top: 16px;
}

.monthly-categories h4, .monthly-budgets h4 {
  margin-bottom: 12px;
  color: #606266;
}

.export-controls {
  padding: 8px 0;
}

.backup-actions {
  margin-bottom: 16px;
}

.restore-section {
  margin-bottom: 16px;
}

.restore-section h4 {
  margin-bottom: 12px;
  color: #606266;
}
</style>
