<template>
  <div class="transaction-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>交易记录</h3>
          <el-button type="primary" @click="showCreateDialog">新增交易</el-button>
        </div>
      </template>

      <el-table :data="transactions" style="width: 100%" v-loading="loading">
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="amount" label="金额" :formatter="amountFormatter" />
        <el-table-column prop="transaction_type" label="类型">
          <template #default="scope">
            <el-tag :type="getTypeColor(scope.row.transaction_type)">
              {{ getTypeText(scope.row.transaction_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category.name" label="分类" />
        <el-table-column prop="account.name" label="账户" />
        <el-table-column prop="date" label="日期" :formatter="dateFormatter" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteTransaction(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 交易表单对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
        <el-form :model="transactionForm" :rules="rules" ref="formRef" label-width="100px">
          <el-form-item label="交易类型" prop="transaction_type">
            <el-radio-group v-model="transactionForm.transaction_type" @change="onTransactionTypeChange">
              <el-radio label="income">收入</el-radio>
              <el-radio label="expense">支出</el-radio>
              <el-radio label="transfer">转账</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="描述" prop="description">
            <el-input v-model="transactionForm.description" placeholder="请输入交易描述" />
          </el-form-item>

          <el-form-item label="金额" prop="amount">
            <el-input-number v-model="transactionForm.amount" :precision="2" :step="0.01" style="width: 100%" />
          </el-form-item>

          <el-form-item label="分类" prop="category_id" v-if="transactionForm.transaction_type !== 'transfer'">
            <el-select v-model="transactionForm.category_id" placeholder="请选择分类" style="width: 100%">
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            :label="transactionForm.transaction_type === 'transfer' ? '转出账户' : '账户'"
            prop="account_id"
          >
            <el-select v-model="transactionForm.account_id" placeholder="请选择账户" style="width: 100%">
              <el-option
                v-for="account in accounts"
                :key="account.id"
                :label="account.name"
                :value="account.id"
              />
            </el-select>
          </el-form-item>

          <!-- 转账时需要选择转入账户 -->
          <el-form-item label="转入账户" prop="to_account_id" v-if="transactionForm.transaction_type === 'transfer'">
            <el-select v-model="transactionForm.to_account_id" placeholder="请选择转入账户" style="width: 100%">
              <el-option
                v-for="account in accounts.filter(a => a.id !== transactionForm.account_id)"
                :key="account.id"
                :label="account.name"
                :value="account.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="交易日期" prop="date">
            <el-date-picker
              v-model="transactionForm.date"
              type="datetime"
              placeholder="请选择交易日期时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="submitForm">确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { getTransactions, createTransaction, updateTransaction, deleteTransaction as deleteApiTransaction } from '@/api/transaction'
import { getCategories } from '@/api/category'
import { getAccounts } from '@/api/account'
import { ElMessage, ElMessageBox } from 'element-plus'

// 定义响应式数据
const transactions = ref([])
const categories = ref([])
const accounts = ref([])
const loading = ref(true)
const dialogVisible = ref(false)
const isEdit = ref(false)
const transactionForm = reactive({
  id: undefined,
  amount: 0,
  description: '',
  transaction_type: 'expense',
  category_id: undefined,
  account_id: undefined,
  from_account_id: undefined,
  to_account_id: undefined,
  date: new Date().toISOString()
})

// 表单验证规则
const rules = {
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' }
  ],
  transaction_type: [
    { required: true, message: '请选择交易类型', trigger: 'change' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  account_id: [
    { required: true, message: '请选择账户', trigger: 'change' }
  ],
  to_account_id: [
    { required: true, message: '请选择转入账户', trigger: 'change' }
  ],
  date: [
    { required: true, message: '请选择交易日期', trigger: 'change' }
  ]
}

const formRef = ref()
const dialogTitle = ref('新增交易')

// 类型颜色映射
const getTypeColor = (type: string) => {
  switch (type) {
    case 'income': return 'success'
    case 'expense': return 'danger'
    case 'transfer': return 'primary'
    default: return 'info'
  }
}

// 类型文本映射
const getTypeText = (type: string) => {
  switch (type) {
    case 'income': return '收入'
    case 'expense': return '支出'
    case 'transfer': return '转账'
    default: return type
  }
}

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

// 加载交易数据
const loadTransactions = async () => {
  try {
    loading.value = true
    const response = await getTransactions()
    transactions.value = response.data
  } catch (error) {
    console.error('Failed to load transactions:', error)
    ElMessage.error('加载交易数据失败')
  } finally {
    loading.value = false
  }
}

// 加载分类数据
const loadCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
    ElMessage.error('加载分类数据失败')
  }
}

// 加载账户数据
const loadAccounts = async () => {
  try {
    const response = await getAccounts()
    accounts.value = response.data
  } catch (error) {
    console.error('Failed to load accounts:', error)
    ElMessage.error('加载账户数据失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增交易'
  Object.assign(transactionForm, {
    id: undefined,
    amount: 0,
    description: '',
    transaction_type: 'expense',
    category_id: undefined,
    account_id: undefined,
    from_account_id: undefined,
    to_account_id: undefined,
    date: new Date().toISOString()
  })
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (transaction: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑交易'
  Object.assign(transactionForm, transaction)
  dialogVisible.value = true
}

// 交易类型改变事件
const onTransactionTypeChange = () => {
  if (transactionForm.transaction_type !== 'transfer') {
    transactionForm.to_account_id = undefined
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        let response
        if (isEdit.value) {
          response = await updateTransaction(transactionForm.id!, transactionForm)
          ElMessage.success('交易更新成功')
        } else {
          response = await createTransaction(transactionForm)
          ElMessage.success('交易创建成功')
        }

        dialogVisible.value = false
        await loadTransactions()
      } catch (error) {
        console.error('Submit error:', error)
        ElMessage.error(isEdit.value ? '更新交易失败' : '创建交易失败')
      }
    }
  })
}

// 删除交易
const deleteTransaction = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该交易吗？此操作不可撤销', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteApiTransaction(id)
    ElMessage.success('删除成功')
    await loadTransactions()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 页面初始化
onMounted(async () => {
  await Promise.all([
    loadTransactions(),
    loadCategories(),
    loadAccounts()
  ])
})
</script>

<style scoped>
.transaction-list {
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}
</style>