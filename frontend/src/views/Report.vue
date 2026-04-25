<template>
  <div class="report-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>报表分析</h3>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-title">月度收支对比</div>
            </template>
            <div class="chart-container">
              <el-empty description="图表功能待实现" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-title">支出分类占比</div>
            </template>
            <div class="chart-container">
              <el-empty description="图表功能待实现" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-title">预算执行情况</div>
            </template>
            <div class="chart-container">
              <el-empty description="图表功能待实现" />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <div class="card-title">资产分布</div>
            </template>
            <div class="chart-container">
              <el-empty description="图表功能待实现" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row style="margin-top: 20px;">
        <el-card shadow="hover">
          <template #header>
            <div class="card-title">交易明细</div>
          </template>
          <el-table :data="recentTransactions" style="width: 100%">
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="amount" label="金额" :formatter="amountFormatter" />
            <el-table-column prop="category.name" label="分类" />
            <el-table-column prop="date" label="日期" :formatter="dateFormatter" />
            <el-table-column prop="account.name" label="账户" />
          </el-table>
        </el-card>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 定义响应式数据
const recentTransactions = ref([])

// 金额格式化函数
const amountFormatter = (row: any, column: any, cellValue: any) => {
  const amount = parseFloat(cellValue)
  if (amount > 0) {
    return `+ ¥ ${Math.abs(amount).toFixed(2)}`
  } else if (amount < 0) {
    return `- ¥ ${Math.abs(amount).toFixed(2)}`
  } else {
    return `¥ 0.00`
  }
}

// 日期格式化函数
const dateFormatter = (row: any, column: any, cellValue: any) => {
  return new Date(cellValue).toLocaleDateString()
}

onMounted(() => {
  // 模拟加载交易数据
  recentTransactions.value = [
    { id: 1, description: '工资收入', amount: 8500.00, category: { name: '工资' }, date: '2023-05-15T00:00:00Z', account: { name: '招商银行储蓄卡' } },
    { id: 2, description: '超市购物', amount: -245.50, category: { name: '食品' }, date: '2023-05-14T00:00:00Z', account: { name: '现金' } },
    { id: 3, description: '餐厅用餐', amount: -120.00, category: { name: '餐饮' }, date: '2023-05-13T00:00:00Z', account: { name: '信用卡' } },
    { id: 4, description: '房租支付', amount: -2000.00, category: { name: '住房' }, date: '2023-05-01T00:00:00Z', account: { name: '招商银行储蓄卡' } },
    { id: 5, description: '交通费', amount: -45.30, category: { name: '交通' }, date: '2023-05-12T00:00:00Z', account: { name: '支付宝' } },
  ]
})
</script>

<style scoped>
.report-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.card-title {
  font-weight: bold;
  color: #303133;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>