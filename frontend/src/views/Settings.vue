<template>
  <div class="settings-container">
    <h2>⚙️ 系统设置</h2>

    <el-card shadow="hover" class="settings-card">
      <template #header>
        <span>通用设置</span>
      </template>

      <el-form label-width="120px">
        <el-form-item label="默认货币">
          <el-select v-model="settings.currency" style="width: 200px;">
            <el-option label="人民币 (CNY)" value="CNY" />
            <el-option label="美元 (USD)" value="USD" />
            <el-option label="欧元 (EUR)" value="EUR" />
            <el-option label="日元 (JPY)" value="JPY" />
          </el-select>
        </el-form-item>

        <el-form-item label="默认账户">
          <el-select v-model="settings.default_account" style="width: 200px;" clearable>
            <el-option
              v-for="account in validAccounts"
              :key="account.id"
              :label="account.name"
              :value="account.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="默认分类">
          <el-select v-model="settings.default_category" style="width: 200px;" clearable>
            <el-option
              v-for="category in validExpenseCategories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="每页显示条数">
          <el-select v-model="settings.page_size" style="width: 120px;">
            <el-option label="10" :value="10" />
            <el-option label="20" :value="20" />
            <el-option label="50" :value="50" />
            <el-option label="100" :value="100" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="settings-card">
      <template #header>
        <span>通知设置</span>
      </template>

      <el-form label-width="120px">
        <el-form-item label="预算提醒">
          <el-switch v-model="settings.budget_alert" />
        </el-form-item>

        <el-form-item label="超支提醒">
          <el-switch v-model="settings.over_spent_alert" />
        </el-form-item>

        <el-form-item label="月度报告">
          <el-switch v-model="settings.monthly_report" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="settings-card">
      <template #header>
        <span>关于</span>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="应用名称">My Wallet Butler</el-descriptions-item>
        <el-descriptions-item label="版本">1.0.0</el-descriptions-item>
        <el-descriptions-item label="技术栈">Vue 3 + FastAPI + MySQL</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAccounts } from '@/api/account'
import { getCategories } from '@/api/category'

interface Settings {
  currency: string
  default_account: number | null
  default_category: number | null
  page_size: number
  budget_alert: boolean
  over_spent_alert: boolean
  monthly_report: boolean
}

const saving = ref(false)
const accounts = ref<any[]>([])
const categories = ref<any[]>([])

const settings = ref<Settings>({
  currency: 'CNY',
  default_account: null,
  default_category: null,
  page_size: 20,
  budget_alert: true,
  over_spent_alert: true,
  monthly_report: false
})

const expenseCategories = computed(() => {
  return categories.value.filter(c => c.category_type === 'expense')
})

const validAccounts = computed(() => {
  return accounts.value.filter(a => a.id != null)
})

const validExpenseCategories = computed(() => {
  return expenseCategories.value.filter(c => c.id != null)
})

async function loadData() {
  try {
    const [accountsRes, categoriesRes] = await Promise.all([
      getAccounts({ page: 1, size: 100 }),
      getCategories({ page: 1, size: 100 })
    ])
    accounts.value = accountsRes.data.data?.items || accountsRes.data.data || []
    categories.value = categoriesRes.data.data?.items || categoriesRes.data.data || []
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '加载数据失败')
  }
}

async function handleSave() {
  saving.value = true
  try {
    // TODO: 实现保存设置 API
    localStorage.setItem('wallet_settings', JSON.stringify(settings.value))
    ElMessage.success('设置保存成功')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '保存设置失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  // 从本地存储加载设置
  const savedSettings = localStorage.getItem('wallet_settings')
  if (savedSettings) {
    try {
      Object.assign(settings.value, JSON.parse(savedSettings))
    } catch {
      // ignore
    }
  }
  loadData()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  color: #303133;
}

.settings-card {
  margin-bottom: 20px;
  max-width: 700px;
}
</style>
