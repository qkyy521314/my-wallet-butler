<template>
  <div class="account-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>账户列表</h3>
          <el-button type="primary" @click="showCreateDialog">新增账户</el-button>
        </div>
      </template>

      <el-table :data="accounts" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="账户名称" />
        <el-table-column prop="account_type" label="账户类型">
          <template #default="scope">
            {{ getAccountTypeText(scope.row.account_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余额" :formatter="amountFormatter" />
        <el-table-column prop="currency" label="货币" />
        <el-table-column prop="created_at" label="创建时间" :formatter="dateFormatter" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteAccount(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 账户表单对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
        <el-form :model="accountForm" :rules="rules" ref="formRef" label-width="80px">
          <el-form-item label="账户名称" prop="name">
            <el-input v-model="accountForm.name" placeholder="请输入账户名称" />
          </el-form-item>
          <el-form-item label="账户类型" prop="account_type">
            <el-select v-model="accountForm.account_type" placeholder="请选择账户类型" style="width: 100%">
              <el-option label="现金" value="cash" />
              <el-option label="银行储蓄卡" value="bank" />
              <el-option label="信用卡" value="credit_card" />
              <el-option label="支付宝" value="alipay" />
              <el-option label="微信钱包" value="wechat" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="余额" prop="balance">
            <el-input-number v-model="accountForm.balance" :precision="2" :step="0.01" style="width: 100%" />
          </el-form-item>
          <el-form-item label="货币" prop="currency">
            <el-select v-model="accountForm.currency" placeholder="请选择货币类型" style="width: 100%">
              <el-option label="人民币 (CNY)" value="CNY" />
              <el-option label="美元 (USD)" value="USD" />
              <el-option label="欧元 (EUR)" value="EUR" />
              <el-option label="其他" value="OTHER" />
            </el-select>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="accountForm.description" type="textarea" placeholder="请输入账户描述" />
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
import { useAccountStore } from '@/store/modules/account'
import { ElMessage, ElMessageBox } from 'element-plus'

// 使用状态管理
const accountStore = useAccountStore()

// 定义响应式数据
const accounts = ref<any[]>([])
const loading = ref(true)
const dialogVisible = ref(false)
const isEdit = ref(false)
const accountForm = reactive({
  id: undefined,
  name: '',
  account_type: 'cash',
  balance: 0,
  currency: 'CNY',
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入账户名称', trigger: 'blur' }
  ],
  account_type: [
    { required: true, message: '请选择账户类型', trigger: 'change' }
  ],
  balance: [
    { required: true, message: '请输入余额', trigger: 'blur' }
  ]
}

const formRef = ref()
const dialogTitle = ref('新增账户')

// 格式化函数
const amountFormatter = (row: any, column: any, cellValue: any) => {
  return `¥ ${parseFloat(cellValue).toFixed(2)}`
}

const dateFormatter = (row: any, column: any, cellValue: any) => {
  return new Date(cellValue).toLocaleDateString()
}

// 账户类型中文映射
const accountTypeMap: Record<string, string> = {
  cash: '现金',
  bank: '银行储蓄卡',
  credit_card: '信用卡',
  alipay: '支付宝',
  wechat: '微信钱包',
  other: '其他'
}

const getAccountTypeText = (type: string) => {
  return accountTypeMap[type] || type
}

// 加载账户数据
const loadAccounts = async () => {
  try {
    loading.value = true
    const response = await accountStore.fetchAccounts()
    accounts.value = response.data?.items || []
  } catch (error) {
    console.error('Failed to load accounts:', error)
    ElMessage.error('加载账户数据失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增账户'
  Object.assign(accountForm, {
    id: undefined,
    name: '',
    account_type: 'cash',
    balance: 0,
    currency: 'CNY',
    description: ''
  })
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (account: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑账户'
  Object.assign(accountForm, account)
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await accountStore.updateAccount(accountForm.id!, accountForm)
          ElMessage.success('账户更新成功')
        } else {
          await accountStore.addAccount(accountForm)
          ElMessage.success('账户创建成功')
        }

        dialogVisible.value = false
        await loadAccounts()
      } catch (error) {
        console.error('Submit error:', error)
        ElMessage.error(isEdit.value ? '更新账户失败' : '创建账户失败')
      }
    }
  })
}

// 删除账户
const deleteAccount = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该账户吗？此操作不可撤销', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await accountStore.removeAccount(id)
    ElMessage.success('删除成功')
    await loadAccounts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 页面初始化
onMounted(async () => {
  await loadAccounts()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.account-list {
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
