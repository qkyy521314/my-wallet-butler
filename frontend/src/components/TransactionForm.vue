<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
    <el-form-item label="交易类型" prop="transaction_type">
      <el-radio-group v-model="formData.transaction_type" @change="onTransactionTypeChange">
        <el-radio value="income">收入</el-radio>
        <el-radio value="expense">支出</el-radio>
        <el-radio value="transfer">转账</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input v-model="formData.description" placeholder="请输入交易描述" />
    </el-form-item>

    <el-form-item label="金额" prop="amount">
      <el-input-number v-model="formData.amount" :precision="2" :step="0.01" style="width: 100%" />
    </el-form-item>

    <el-form-item label="分类" prop="category_id" v-if="formData.transaction_type !== 'transfer'">
      <el-select v-model="formData.category_id" placeholder="请选择分类" style="width: 100%">
        <el-option
          v-for="category in categories"
          :key="category.id"
          :label="category.name"
          :value="category.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item
      :label="formData.transaction_type === 'transfer' ? '转出账户' : '账户'"
      prop="account_id"
    >
      <el-select v-model="formData.account_id" placeholder="请选择账户" style="width: 100%">
        <el-option
          v-for="account in accounts"
          :key="account.id"
          :label="account.name"
          :value="account.id"
        />
      </el-select>
    </el-form-item>

    <!-- 转账时需要选择转入账户 -->
    <el-form-item label="转入账户" prop="to_account_id" v-if="formData.transaction_type === 'transfer'">
      <el-select v-model="formData.to_account_id" placeholder="请选择转入账户" style="width: 100%">
        <el-option
          v-for="account in filteredAccounts"
          :key="account.id"
          :label="account.name"
          :value="account.id"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="交易日期" prop="date">
      <el-date-picker
        v-model="formData.date"
        type="datetime"
        placeholder="请选择交易日期时间"
        format="YYYY-MM-DD HH:mm:ss"
        value-format="YYYY-MM-DDTHH:mm:ss"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { getCategories } from '@/api/category'
import { getAccounts } from '@/api/account'
import { ElMessage } from 'element-plus'

// 定义props和emit
interface Props {
  initialData?: any
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({})
})

const emit = defineEmits<{
  submit: [data: any]
}>()

// 表单数据
const formData = reactive({
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

// 定义响应式数据
const categories = ref([])
const accounts = ref([])
const formRef = ref()

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

// 过滤账户（排除转出账户）
const filteredAccounts = computed(() => {
  return accounts.value.filter((account: any) => account.id !== formData.account_id)
})

// 监听初始数据变化
watch(() => props.initialData, (newVal) => {
  if (newVal) {
    Object.assign(formData, newVal)
  }
}, { immediate: true })

// 交易类型改变事件
const onTransactionTypeChange = () => {
  if (formData.transaction_type !== 'transfer') {
    formData.to_account_id = undefined
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        emit('submit', { ...formData })
      } catch (error) {
        console.error('Submit error:', error)
        ElMessage.error('提交失败')
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(formData, {
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

// 初始化数据
loadCategories()
loadAccounts()
</script>

<style scoped>
.el-form {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}
</style>