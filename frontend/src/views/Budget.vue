<template>
  <div class="budget-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>预算管理</h3>
          <el-button type="primary" @click="showCreateDialog">新增预算</el-button>
        </div>
      </template>

      <el-table :data="budgets" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="预算名称" />
        <el-table-column prop="category.name" label="分类" />
        <el-table-column prop="amount" label="预算金额" :formatter="amountFormatter" />
        <el-table-column prop="spent_amount" label="已花费" :formatter="amountFormatter" />
        <el-table-column prop="period_start" label="开始时间" :formatter="dateFormatter" />
        <el-table-column prop="period_end" label="结束时间" :formatter="dateFormatter" />
        <el-table-column prop="progress" label="进度">
          <template #default="scope">
            <el-progress
              :percentage="calculateProgress(scope.row.spent_amount, scope.row.amount)"
              :status="getProgressStatus(scope.row.spent_amount, scope.row.amount)"
              :color="getProgressColor(scope.row.spent_amount, scope.row.amount)"
            />
            <div>{{ calculateProgress(scope.row.spent_amount, scope.row.amount) }}%</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag
              :type="scope.row.is_over_spent ? 'danger' : calculateProgress(scope.row.spent_amount, scope.row.amount) >= 80 ? 'warning' : 'success'"
            >
              {{ scope.row.is_over_spent ? '超支' : calculateProgress(scope.row.spent_amount, scope.row.amount) >= 80 ? '警戒' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="info" @click="viewStats(scope.row.id)">统计</el-button>
            <el-button size="small" type="danger" @click="deleteBudget(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 预算表单对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
        <el-form :model="budgetForm" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="预算名称" prop="name">
            <el-input v-model="budgetForm.name" placeholder="请输入预算名称" />
          </el-form-item>

          <el-form-item label="分类" prop="category_id">
            <el-select v-model="budgetForm.category_id" placeholder="请选择分类" style="width: 100%">
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="预算金额" prop="amount">
            <el-input-number v-model="budgetForm.amount" :precision="2" :step="0.01" style="width: 100%" />
          </el-form-item>

          <el-form-item label="开始时间" prop="period_start">
            <el-date-picker
              v-model="budgetForm.period_start"
              type="datetime"
              placeholder="请选择开始时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="结束时间" prop="period_end">
            <el-date-picker
              v-model="budgetForm.period_end"
              type="datetime"
              placeholder="请选择结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="描述">
            <el-input v-model="budgetForm.description" type="textarea" placeholder="请输入预算描述" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitForm">确定</el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 预算统计对话框 -->
      <el-dialog v-model="statsDialogVisible" title="预算统计详情" width="600px">
        <div v-if="selectedStats">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="预算名称">{{ selectedStats.name }}</el-descriptions-item>
            <el-descriptions-item label="总预算金额">{{ amountFormatter(null, null, selectedStats.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="已花费">{{ amountFormatter(null, null, selectedStats.spent_amount) }}</el-descriptions-item>
            <el-descriptions-item label="剩余预算">{{ amountFormatter(null, null, selectedStats.remaining_amount) }}</el-descriptions-item>
            <el-descriptions-item label="花费百分比">{{ selectedStats.spent_percentage }}%</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag
                :type="selectedStats.is_over_spent ? 'danger' : selectedStats.spent_percentage >= 80 ? 'warning' : 'success'"
              >
                {{ selectedStats.is_over_spent ? '超支' : selectedStats.spent_percentage >= 80 ? '警戒' : '正常' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { getBudgets, createBudget, updateBudget, deleteBudget as deleteApiBudget, getBudgetStats } from '@/api/budget'
import { getCategories } from '@/api/category'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

// 定义响应式数据
const budgets = ref([])
const categories = ref([])
const loading = ref(true)
const dialogVisible = ref(false)
const statsDialogVisible = ref(false)
const selectedStats = ref(null)
const isEdit = ref(false)
const budgetForm = reactive({
  id: undefined,
  name: '',
  category_id: undefined,
  amount: 0,
  period_start: new Date().toISOString(),
  period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30天后
  description: '',
  spent_amount: 0
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入预算名称', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入预算金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '预算金额必须大于0', trigger: 'blur' }
  ],
  period_start: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  period_end: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ]
}

const formRef = ref()
const dialogTitle = ref('新增预算')

// 金额格式化函数
const amountFormatter = (row: any, column: any, cellValue: any) => {
  return `¥ ${parseFloat(cellValue || 0).toFixed(2)}`
}

// 日期格式化函数
const dateFormatter = (row: any, column: any, cellValue: any) => {
  return new Date(cellValue).toLocaleDateString()
}

// 计算预算进度百分比
const calculateProgress = (spent: number, total: number) => {
  const spentNum = parseFloat(spent || 0)
  const totalNum = parseFloat(total || 0)
  if (totalNum === 0) return 0
  return Math.round((spentNum / totalNum) * 100)
}

// 根据进度返回状态
const getProgressStatus = (spent: number, total: number) => {
  const percentage = calculateProgress(spent, total)
  if (percentage >= 100) return 'exception'
  if (percentage >= 80) return 'warning'
  return 'success'
}

// 根据进度返回颜色
const getProgressColor = (spent: number, total: number) => {
  const percentage = calculateProgress(spent, total)
  if (percentage >= 100) return '#F56C6C' // 红色
  if (percentage >= 80) return '#E6A23C'  // 黄色
  return '#67C23A'  // 绿色
}

// 加载预算数据
const loadBudgets = async () => {
  try {
    loading.value = true
    const response = await getBudgets()
    budgets.value = response.data.data?.items || response.data.data || []
  } catch (error) {
    console.error('Failed to load budgets:', error)
    ElMessage.error('加载预算数据失败')
  } finally {
    loading.value = false
  }
}

// 加载分类数据
const loadCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response.data.data?.items || response.data.data || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    ElMessage.error('加载分类数据失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增预算'
  Object.assign(budgetForm, {
    id: undefined,
    name: '',
    category_id: undefined,
    amount: 0,
    period_start: new Date().toISOString(),
    period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30天后
    description: '',
    spent_amount: 0
  })
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (budget: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑预算'
  Object.assign(budgetForm, budget)
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        let response
        if (isEdit.value) {
          response = await updateBudget(budgetForm.id!, budgetForm)
          ElMessage.success('预算更新成功')
        } else {
          response = await createBudget(budgetForm)
          ElMessage.success('预算创建成功')
        }

        dialogVisible.value = false
        await loadBudgets()
      } catch (error) {
        console.error('Submit error:', error)
        ElMessage.error(isEdit.value ? '更新预算失败' : '创建预算失败')
      }
    }
  })
}

// 删除预算
const deleteBudget = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该预算吗？此操作不可撤销', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteApiBudget(id)
    ElMessage.success('删除成功')
    await loadBudgets()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 查看预算统计
const viewStats = async (id: number) => {
  try {
    const response = await getBudgetStats(id)
    selectedStats.value = response.data
    statsDialogVisible.value = true
  } catch (error) {
    console.error('Failed to load budget stats:', error)
    ElMessage.error('加载预算统计失败')
  }
}

// 页面初始化
onMounted(async () => {
  await Promise.all([
    loadBudgets(),
    loadCategories()
  ])
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.budget-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-family: $font-display;
    font-weight: 600;
    color: $text-primary;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: $space-md;
}

:deep(.el-card) {
  border-radius: $radius-lg;
}

:deep(.el-card__header) {
  padding: $space-md $space-lg;
  border-bottom: 1px solid $border-light;
}

:deep(.el-table) {
  border-radius: $radius-lg;
  overflow: hidden;

  th.el-table__cell {
    background: $gray-50 !important;
    font-family: $font-display;
    font-weight: 600;
    color: $text-secondary;
    font-size: $text-sm;
  }
}
</style>