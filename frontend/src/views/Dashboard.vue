<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-item">
            <div class="summary-icon bg-blue">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="summary-content">
              <h3>总资产</h3>
              <p class="amount">¥ {{ totalAssets }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-item">
            <div class="summary-icon bg-green">
              <el-icon><Money /></el-icon>
            </div>
            <div class="summary-content">
              <h3>本月收入</h3>
              <p class="amount">¥ {{ monthlyIncome }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-item">
            <div class="summary-icon bg-red">
              <el-icon><Document /></el-icon>
            </div>
            <div class="summary-content">
              <h3>本月支出</h3>
              <p class="amount">¥ {{ monthlyExpense }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-item">
            <div class="summary-icon bg-orange">
              <el-icon><PieChart /></el-icon>
            </div>
            <div class="summary-content">
              <h3>结余</h3>
              <p class="amount">¥ {{ balance }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近交易</span>
            </div>
          </template>
          <el-table :data="recentTransactions" style="width: 100%">
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="amount" label="金额" :formatter="amountFormatter" />
            <el-table-column prop="date" label="日期" :formatter="dateFormatter" />
            <el-table-column prop="category.name" label="分类" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>账户余额</span>
            </div>
          </template>
          <el-table :data="accountBalances" style="width: 100%">
            <el-table-column prop="name" label="账户" />
            <el-table-column prop="balance" label="余额" :formatter="amountFormatter" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Wallet, Money, Document, PieChart } from '@element-plus/icons-vue'
import { useAccountStore } from '@/store/modules/account'
import { getTransactions } from '@/api/transaction'

// 使用状态管理
const accountStore = useAccountStore()

// 初始化数据
const totalAssets = ref(0)
const monthlyIncome = ref(0)
const monthlyExpense = ref(0)
const balance = ref(0)
const recentTransactions = ref([])
const accountBalances = ref([])

// 金额格式化函数
const amountFormatter = (row: any, column: any, cellValue: any) => {
  return `¥ ${cellValue.toFixed(2)}`
}

// 日期格式化函数
const dateFormatter = (row: any, column: any, cellValue: any) => {
  return new Date(cellValue).toLocaleDateString()
}

onMounted(async () => {
  // 获取账户信息
  await accountStore.fetchAccounts()

  // 设置模拟数据
  totalAssets.value = 15420.50
  monthlyIncome.value = 8500.00
  monthlyExpense.value = 3240.75
  balance.value = monthlyIncome.value - monthlyExpense.value

  // 获取最近交易
  recentTransactions.value = [
    { id: 1, description: '工资收入', amount: 8500.00, date: '2023-05-15T00:00:00Z', category: { name: '工资' } },
    { id: 2, description: '超市购物', amount: -245.50, date: '2023-05-14T00:00:00Z', category: { name: '食品' } },
    { id: 3, description: '餐厅用餐', amount: -120.00, date: '2023-05-13T00:00:00Z', category: { name: '餐饮' } },
    { id: 4, description: '房租支付', amount: -2000.00, date: '2023-05-01T00:00:00Z', category: { name: '住房' } },
  ]

  // 获取账户余额
  accountBalances.value = accountStore.accounts.map((account: any) => ({
    name: account.name,
    balance: account.balance
  }))
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.summary-card {
  height: 100px;
}

.summary-item {
  display: flex;
  align-items: center;
}

.summary-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: white;
}

.bg-blue {
  background-color: #409eff;
}

.bg-green {
  background-color: #67c23a;
}

.bg-red {
  background-color: #f56c6c;
}

.bg-orange {
  background-color: #e6a23c;
}

.summary-content h3 {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.summary-content .amount {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-table {
  margin-top: 20px;
}
</style>