<template>
  <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
    <el-form-item label="账户名称" prop="name">
      <el-input v-model="formData.name" placeholder="请输入账户名称" />
    </el-form-item>

    <el-form-item label="账户类型" prop="account_type">
      <el-select v-model="formData.account_type" placeholder="请选择账户类型" style="width: 100%">
        <el-option label="现金" value="cash" />
        <el-option label="银行储蓄卡" value="bank" />
        <el-option label="信用卡" value="credit_card" />
        <el-option label="支付宝" value="alipay" />
        <el-option label="微信钱包" value="wechat" />
        <el-option label="其他" value="other" />
      </el-select>
    </el-form-item>

    <el-form-item label="余额" prop="balance">
      <el-input-number v-model="formData.balance" :precision="2" :step="0.01" style="width: 100%" />
    </el-form-item>

    <el-form-item label="货币" prop="currency">
      <el-select v-model="formData.currency" placeholder="请选择货币类型" style="width: 100%">
        <el-option label="人民币 (CNY)" value="CNY" />
        <el-option label="美元 (USD)" value="USD" />
        <el-option label="欧元 (EUR)" value="EUR" />
        <el-option label="其他" value="OTHER" />
      </el-select>
    </el-form-item>

    <el-form-item label="描述">
      <el-input v-model="formData.description" type="textarea" placeholder="请输入账户描述" />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
      <el-button @click="resetForm">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
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
  name: '',
  account_type: 'cash',
  balance: 0,
  currency: 'CNY',
  description: '',
  is_active: true
})

const formRef = ref()

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

// 监听初始数据变化
watch(() => props.initialData, (newVal) => {
  if (newVal) {
    Object.assign(formData, newVal)
  }
}, { immediate: true })

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
    name: '',
    account_type: 'cash',
    balance: 0,
    currency: 'CNY',
    description: '',
    is_active: true
  })
}
</script>

<style scoped>
.el-form {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}
</style>