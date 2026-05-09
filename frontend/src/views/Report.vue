<template>
  <div class="report-container">
    <h2>报表分析</h2>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <el-date-picker
        v-model="selectedMonth"
        type="month"
        placeholder="选择月份"
        value-format="YYYY-MM"
        @change="loadReport"
      />
      <el-button type="primary" :loading="loading" @click="loadReport">
        查询
      </el-button>
      <el-dropdown @command="handleExport" class="export-dropdown">
        <el-button type="success">
          导出数据 <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
            <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 月度汇总卡片 -->
    <div class="summary-cards" v-if="monthlySummary">
      <el-card shadow="hover" class="summary-card income">
        <div class="card-label">总收入</div>
        <div class="card-value">¥{{ monthlySummary.total_income.toFixed(2) }}</div>
      </el-card>
      <el-card shadow="hover" class="summary-card expense">
        <div class="card-label">总支出</div>
        <div class="card-value">¥{{ monthlySummary.total_expense.toFixed(2) }}</div>
      </el-card>
      <el-card shadow="hover" class="summary-card net">
        <div class="card-label">净收支</div>
        <div class="card-value">¥{{ monthlySummary.net.toFixed(2) }}</div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card shadow="hover" class="chart-card">
        <template #header>每日收支趋势</template>
        <div ref="dailyChartRef" class="chart"></div>
      </el-card>
      <el-card shadow="hover" class="chart-card">
        <template #header>分类支出占比</template>
        <div ref="categoryChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- 预算执行 -->
    <el-card shadow="hover" class="budget-card" v-if="budgetExecution && budgetExecution.budgets.length">
      <template #header>预算执行报告</template>
      <el-table :data="budgetExecution.budgets" stripe>
        <el-table-column prop="category_name" label="分类" width="150" />
        <el-table-column prop="budget_amount" label="预算金额" width="120">
          <template #default="{ row }">¥{{ row.budget_amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="actual_amount" label="实际支出" width="120">
          <template #default="{ row }">¥{{ row.actual_amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="remaining" label="剩余" width="120">
          <template #default="{ row }">
            <span :class="{ 'over-budget': row.is_over }">
              ¥{{ row.remaining.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="executed_percentage" label="执行率" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.executed_percentage"
              :status="row.is_over ? 'exception' : row.executed_percentage > 80 ? 'warning' : ''"
              :stroke-width="18"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getMonthlySummary,
  getCategoryExpense,
  getBudgetExecution,
  getDailyTrend,
  exportCSV,
  exportExcel,
} from '../api/report'
import { useUserStore } from '../store/modules/user'
import dayjs from 'dayjs'

const userStore = useUserStore()
const loading = ref(false)
const selectedMonth = ref(dayjs().format('YYYY-MM'))

const monthlySummary = ref<any>(null)
const categoryExpense = ref<any>(null)
const budgetExecution = ref<any>(null)
const dailyTrend = ref<any>(null)

const dailyChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()
let dailyChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

const userId = computed(() => userStore.user?.id || 0)

async function loadReport() {
  if (!userId.value) {
    ElMessage.warning('请先登录')
    return
  }
  loading.value = true
  try {
    const [d, m] = selectedMonth.value.split('-').map(Number)

    const [summaryRes, categoryRes, budgetRes, trendRes] = await Promise.all([
      getMonthlySummary(d, m, userId.value),
      getCategoryExpense(d, m, userId.value),
      getBudgetExecution(d, m, userId.value),
      getDailyTrend(d, m, userId.value),
    ])

    monthlySummary.value = summaryRes.data
    categoryExpense.value = categoryRes.data
    budgetExecution.value = budgetRes.data
    dailyTrend.value = trendRes.data

    renderDailyChart()
    renderCategoryChart()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '加载报表失败')
  } finally {
    loading.value = false
  }
}

function renderDailyChart() {
  if (!dailyChartRef.value || !dailyTrend.value?.daily_data?.length) return
  if (!dailyChart) {
    dailyChart = echarts.init(dailyChartRef.value)
  }

  const data = dailyTrend.value.daily_data
  const option = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['收入', '支出'],
    },
    xAxis: {
      type: 'category',
      data: data.map((d: any) => d.day.slice(5)), // 只显示 MM-DD
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '收入',
        type: 'bar',
        data: data.map((d: any) => d.income),
        itemStyle: { color: '#67C23A' },
      },
      {
        name: '支出',
        type: 'bar',
        data: data.map((d: any) => d.expense),
        itemStyle: { color: '#F56C6C' },
      },
    ],
  }
  dailyChart.setOption(option)
}

function renderCategoryChart() {
  if (!categoryChartRef.value || !categoryExpense.value?.categories?.length) return
  if (!categoryChart) {
    categoryChart = echarts.init(categoryChartRef.value)
  }

  const data = categoryExpense.value.categories
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: data.map((c: any) => ({
          name: c.name,
          value: c.amount,
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }
  categoryChart.setOption(option)
}

async function handleExport(format: string) {
  if (!userId.value) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const [year, month] = selectedMonth.value.split('-').map(Number)
    const res = format === 'csv'
      ? await exportCSV(year, month, userId.value)
      : await exportExcel(year, month, userId.value)

    // 创建下载链接
    const blob = new Blob([res.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const ext = format === 'csv' ? 'csv' : 'xlsx'
    link.download = `transactions_${year}_${String(month).padStart(2, '0')}.${ext}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '导出失败')
  }
}

// 窗口大小变化时重绘图表
function handleResize() {
  dailyChart?.resize()
  categoryChart?.resize()
}

onMounted(() => {
  loadReport()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  dailyChart?.dispose()
  categoryChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.report-container {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
}

.export-dropdown {
  margin-left: auto;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  text-align: center;
}

.card-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
}

.income .card-value {
  color: #67C23A;
}

.expense .card-value {
  color: #F56C6C;
}

.net .card-value {
  color: #409EFF;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.chart-card {
  min-height: 400px;
}

.chart {
  height: 350px;
  width: 100%;
}

.budget-card {
  margin-bottom: 24px;
}

.over-budget {
  color: #F56C6C;
  font-weight: bold;
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
