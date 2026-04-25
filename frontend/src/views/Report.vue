<template>
  <div class="report-page">
    <el-card class="summary-card">
      <template #header>
        <h3>收支概览</h3>
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

    <el-card class="analysis-card">
      <template #header>
        <div class="analysis-header">
          <h3>分类支出占比</h3>
          <div class="date-range-selector">
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
          </div>
        </div>
      </template>

      <div class="chart-container">
        <div class="pie-chart" ref="pieChartRef" style="height: 400px;"></div>
      </div>
    </el-card>

    <el-card class="analysis-card">
      <template #header>
        <h3>收支趋势</h3>
      </template>

      <div class="chart-container">
        <div class="trend-controls">
          <el-radio-group v-model="trendGroupBy" @change="loadTrendData">
            <el-radio-button label="day">按天</el-radio-button>
            <el-radio-button label="month">按月</el-radio-button>
          </el-radio-group>
        </div>
        <div class="line-chart" ref="lineChartRef" style="height: 400px;"></div>
      </div>
    </el-card>

    <el-card class="analysis-card">
      <template #header>
        <h3>月度报表</h3>
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

      <div class="monthly-summary" v-if="monthlyReport.summary">
        <h4>月度摘要</h4>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="总收入">{{ formatCurrency(monthlyReport.summary.total_income) }}</el-descriptions-item>
          <el-descriptions-item label="总支出">{{ formatCurrency(monthlyReport.summary.total_expense) }}</el-descriptions-item>
          <el-descriptions-item label="净收入">{{ formatCurrency(monthlyReport.summary.net_income) }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="monthly-categories" v-if="monthlyReport.category_analysis">
        <h4>分类支出详情</h4>
        <el-table :data="monthlyReport.category_analysis.categories" style="width: 100%">
          <el-table-column prop="category_name" label="分类名称" />
          <el-table-column prop="amount" label="金额" :formatter="(row, column, cellValue) => formatCurrency(cellValue)" />
          <el-table-column prop="percentage" label="占比(%)" />
        </el-table>
      </div>

      <div class="monthly-budgets" v-if="monthlyReport.budget_performance && monthlyReport.budget_performance.length > 0">
        <h4>预算执行情况</h4>
        <el-table :data="monthlyReport.budget_performance" style="width: 100%">
          <el-table-column prop="name" label="预算名称" />
          <el-table-column prop="category_name" label="分类" />
          <el-table-column prop="budget_amount" label="预算金额" :formatter="(row, column, cellValue) => formatCurrency(cellValue)" />
          <el-table-column prop="spent_amount" label="已花费" :formatter="(row, column, cellValue) => formatCurrency(cellValue)" />
          <el-table-column prop="percentage_used" label="执行率(%)" />
          <el-table-column label="状态">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getSummaryReport, getCategoryAnalysis, getTrendAnalysis, getMonthlyReport } from '@/api/report'
import { ElMessage } from 'element-plus'

// 图表引用
const pieChartRef = ref<HTMLDivElement>()
const lineChartRef = ref<HTMLDivElement>()
let pieChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

// 数据
const summary = ref({ total_income: 0, total_expense: 0, net_income: 0 })
const categoryData = ref([])
const trendData = ref([])
const monthlyReport = ref({ summary: {}, category_analysis: {}, budget_performance: [] })

// 控制器
const dateRange = ref<[string, string]>([
  new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
  new Date().toISOString().split('T')[0]
])
const trendGroupBy = ref('day')
const monthlyDate = ref(new Date().toISOString().slice(0, 7)) // YYYY-MM format

// 初始化图表
onMounted(() => {
  nextTick(() => {
    initCharts()
  })

  loadData()
})

// 初始化图表
const initCharts = () => {
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
  }
  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value)
  }

  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    if (pieChart) pieChart.resize()
    if (lineChart) lineChart.resize()
  })
}

// 加载概览和分类数据
const loadData = async () => {
  if (!dateRange.value || dateRange.value.length < 2) return

  try {
    // 加载概览数据
    const user_id = 1 // 示例用户ID，实际应从登录状态获取
    const summaryParams = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      user_id: user_id
    }

    const summaryRes = await getSummaryReport(summaryParams)
    summary.value = summaryRes.data

    // 加载分类分析数据
    const categoryParams = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      user_id: user_id,
      transaction_type: 'expense'
    }

    const categoryRes = await getCategoryAnalysis(categoryParams)
    categoryData.value = categoryRes.data.categories

    // 渲染饼图
    renderPieChart()
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('加载数据失败')
  }
}

// 加载趋势数据
const loadTrendData = async () => {
  if (!dateRange.value || dateRange.value.length < 2) return

  try {
    const user_id = 1 // 示例用户ID，实际应从登录状态获取
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      user_id: user_id,
      group_by: trendGroupBy.value
    }

    const res = await getTrendAnalysis(params)
    trendData.value = res.data.trend_data

    // 渲染折线图
    renderLineChart()
  } catch (error) {
    console.error('Failed to load trend data:', error)
    ElMessage.error('加载趋势数据失败')
  }
}

// 加载月度报告
const loadMonthlyReport = async () => {
  if (!monthlyDate.value) return

  try {
    const [year, month] = monthlyDate.value.split('-').map(Number)
    const user_id = 1 // 示例用户ID，实际应从登录状态获取

    const params = {
      year: year,
      month: month,
      user_id: user_id
    }

    const res = await getMonthlyReport(params)
    monthlyReport.value = res.data
  } catch (error) {
    console.error('Failed to load monthly report:', error)
    ElMessage.error('加载月度报告失败')
  }
}

// 渲染饼图
const renderPieChart = () => {
  if (!pieChart) return

  const chartData = categoryData.value.map((item: any) => ({
    value: item.amount,
    name: item.category_name
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '支出分类',
        type: 'pie',
        radius: '50%',
        data: chartData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  pieChart.setOption(option, true)
}

// 渲染折线图
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
        params.forEach(param => {
          result += param.seriesName + ': ¥' + param.value + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['收入', '支出']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        stack: '总量',
        data: incomes,
        itemStyle: { color: '#67C23A' }
      },
      {
        name: '支出',
        type: 'line',
        stack: '总量',
        data: expenses,
        itemStyle: { color: '#F56C6C' }
      }
    ]
  }

  lineChart.setOption(option, true)
}

// 格式化货币
const formatCurrency = (value: number) => {
  return '¥ ' + parseFloat(value || 0).toFixed(2)
}

// 清理资源
const onUnmounted = () => {
  if (pieChart) pieChart.dispose()
  if (lineChart) lineChart.dispose()
}
</script>

<style scoped>
.report-page {
  padding: 20px;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.summary-item {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.summary-content {
  display: flex;
  align-items: center;
}

.summary-icon {
  font-size: 24px;
  margin-right: 15px;
}

.summary-info {
  flex: 1;
}

.summary-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.summary-value {
  font-size: 20px;
  font-weight: bold;
}

.summary-value.income {
  color: #67C23A;
}

.summary-value.expense {
  color: #F56C6C;
}

.analysis-card {
  margin-bottom: 20px;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-range-selector {
  margin-left: 20px;
}

.chart-container {
  position: relative;
}

.trend-controls {
  margin-bottom: 20px;
  text-align: center;
}

.monthly-controls {
  margin-bottom: 20px;
}

.monthly-summary, .monthly-categories, .monthly-budgets {
  margin-top: 20px;
}
</style>