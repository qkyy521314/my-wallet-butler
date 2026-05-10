<template>
  <div class="category-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>分类管理</h3>
          <el-button type="primary" @click="showCreateDialog">新增分类</el-button>
        </div>
      </template>

      <el-table :data="categories" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="category_type" label="类型">
          <template #default="scope">
            <el-tag :type="scope.row.category_type === 'income' ? 'success' : 'danger'">
              {{ scope.row.category_type === 'income' ? '收入' : '支出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" :formatter="dateFormatter" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCategory(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分类表单对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
        <el-form :model="categoryForm" :rules="rules" ref="formRef" label-width="80px">
          <el-form-item label="分类名称" prop="name">
            <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
          </el-form-item>
          <el-form-item label="分类类型" prop="category_type">
            <el-radio-group v-model="categoryForm.category_type">
              <el-radio value="income">收入</el-radio>
              <el-radio value="expense">支出</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="categoryForm.description" type="textarea" placeholder="请输入分类描述" />
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
import { useCategoryStore } from '@/store/modules/category'
import { ElMessage, ElMessageBox } from 'element-plus'

// 使用状态管理
const categoryStore = useCategoryStore()

// 定义响应式数据
const categories = ref([])
const loading = ref(true)
const dialogVisible = ref(false)
const isEdit = ref(false)
const categoryForm = reactive({
  id: undefined,
  name: '',
  category_type: 'expense',
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' }
  ],
  category_type: [
    { required: true, message: '请选择分类类型', trigger: 'change' }
  ]
}

const formRef = ref()
const dialogTitle = ref('新增分类')

// 日期格式化函数
const dateFormatter = (row: any, column: any, cellValue: any) => {
  return new Date(cellValue).toLocaleDateString()
}

// 加载分类数据
const loadCategories = async () => {
  try {
    loading.value = true
    const response = await categoryStore.fetchCategories()
    categories.value = response.data.data?.items || [].data?.items || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    ElMessage.error('加载分类数据失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增分类'
  Object.assign(categoryForm, {
    id: undefined,
    name: '',
    category_type: 'expense',
    description: ''
  })
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (category: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑分类'
  Object.assign(categoryForm, category)
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await categoryStore.updateCategory(categoryForm.id!, categoryForm)
          ElMessage.success('分类更新成功')
        } else {
          await categoryStore.addCategory(categoryForm)
          ElMessage.success('分类创建成功')
        }

        dialogVisible.value = false
        await loadCategories()
      } catch (error) {
        console.error('Submit error:', error)
        ElMessage.error(isEdit.value ? '更新分类失败' : '创建分类失败')
      }
    }
  })
}

// 删除分类
const deleteCategory = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除该分类吗？此操作不可撤销', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await categoryStore.removeCategory(id)
    ElMessage.success('删除成功')
    await loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 页面初始化
onMounted(async () => {
  await loadCategories()
})
</script>

<style scoped>
.category-list {
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
</style>