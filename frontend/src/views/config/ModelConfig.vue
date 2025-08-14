<template>
  <div class="model-config">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">AI模型配置</h1>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          添加模型
        </el-button>
        <el-button :icon="Refresh" @click="refreshData" :loading="loading">
          刷新
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="page-container">
      <el-row :gutter="20" class="search-row">
        <el-col :xs="24" :sm="12" :md="8">
          <el-input
            v-model="searchForm.search"
            placeholder="搜索模型名称"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="searchForm.model_type"
            placeholder="选择模型类型"
            clearable
            @change="handleSearch"
          >
            <el-option label="OpenAI兼容" value="OpenAI-Compatible" />
            <el-option label="Google Gemini" value="Gemini" />
            <el-option label="Anthropic Claude" value="Claude" />
            <el-option label="其他" value="Other" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="searchForm.status"
            placeholder="选择状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 模型列表 -->
    <div class="page-container">
      <el-table
        v-loading="loading"
        :data="modelList"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="模型名称" sortable min-width="150">
          <template #default="{ row }">
            <div class="model-name">
              <strong>{{ row.name }}</strong>
              <el-tag
                :type="getModelTypeTagType(row.model_type)"
                size="small"
                class="ml-10"
              >
                {{ row.model_type }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="api_endpoint" label="API端点" min-width="200">
          <template #default="{ row }">
            <el-text class="api-endpoint" truncated>
              {{ row.api_endpoint }}
            </el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="handleStatusChange(row)"
              :loading="row.statusLoading"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="viewModel(row)"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="editModel(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这个模型配置吗？"
              @confirm="deleteModel(row)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  size="small"
                  :icon="Delete"
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="模型名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入模型名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="模型类型" prop="model_type">
          <el-select v-model="formData.model_type" placeholder="请选择模型类型">
            <el-option label="OpenAI兼容" value="OpenAI-Compatible" />
            <el-option label="Google Gemini" value="Gemini" />
            <el-option label="Anthropic Claude" value="Claude" />
            <el-option label="其他" value="Other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API端点" prop="api_endpoint">
          <el-input
            v-model="formData.api_endpoint"
            placeholder="请输入API端点URL"
            type="url"
          />
        </el-form-item>
        
        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="formData.api_key"
            placeholder="请输入API密钥"
            type="password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="默认参数">
          <el-input
            v-model="defaultParamsText"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的默认参数（可选）"
          />
          <div class="form-tip">
            例如: {"temperature": 0.7, "max_tokens": 1000}
          </div>
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="info"
            @click="testConnection"
            :loading="testLoading"
          >
            测试连接
          </el-button>
          <el-button
            type="primary"
            @click="submitForm"
            :loading="submitLoading"
          >
            {{ isEdit ? '更新' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="模型详情"
      width="500px"
    >
      <div v-if="currentModel" class="model-detail">
        <div class="detail-item">
          <label>模型名称:</label>
          <span>{{ currentModel.name }}</span>
        </div>
        <div class="detail-item">
          <label>模型类型:</label>
          <el-tag :type="getModelTypeTagType(currentModel.model_type)">
            {{ currentModel.model_type }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>API端点:</label>
          <span>{{ currentModel.api_endpoint }}</span>
        </div>
        <div class="detail-item">
          <label>状态:</label>
          <el-tag :type="currentModel.is_active ? 'success' : 'danger'">
            {{ currentModel.is_active ? '启用' : '禁用' }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>默认参数:</label>
          <pre class="json-display">{{ formatJSON(currentModel.default_params) }}</pre>
        </div>
        <div class="detail-item">
          <label>创建时间:</label>
          <span>{{ formatTime(currentModel.created_at) }}</span>
        </div>
        <div class="detail-item">
          <label>更新时间:</label>
          <span>{{ formatTime(currentModel.updated_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus,
  Refresh,
  Search,
  View,
  Edit,
  Delete
} from '@element-plus/icons-vue'
import { aiModelApi } from '@/api'
import type { AIModel, AIModelCreate } from '@/types/api'

// 响应式数据
const loading = ref(false)
const modelList = ref<AIModel[]>([])
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const currentModel = ref<AIModel | null>(null)
const testLoading = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  search: '',
  model_type: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive<AIModelCreate>({
  name: '',
  model_type: '',
  api_endpoint: '',
  api_key: '',
  default_params: {},
  is_active: true
})

// 默认参数文本
const defaultParamsText = ref('')

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  model_type: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  api_endpoint: [
    { required: true, message: '请输入API端点', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  api_key: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑模型' : '添加模型')

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      model_type: searchForm.model_type || undefined,
      is_active: searchForm.status === 'active' ? true : searchForm.status === 'inactive' ? false : undefined
    }
    
    const response = await aiModelApi.getList(params)
    modelList.value = response.items.map(item => ({ ...item, statusLoading: false }))
    pagination.total = response.total
  } catch (error) {
    console.error('获取模型列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  refreshData()
}

const handleSortChange = ({ prop, order }: any) => {
  // 处理排序逻辑
  refreshData()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  refreshData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  refreshData()
}

const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const viewModel = (model: AIModel) => {
  currentModel.value = model
  viewDialogVisible.value = true
}

const editModel = (model: AIModel) => {
  isEdit.value = true
  currentModel.value = model
  
  // 填充表单数据
  Object.assign(formData, {
    name: model.name,
    model_type: model.model_type,
    api_endpoint: model.api_endpoint,
    api_key: '', // 不显示原密钥
    is_active: model.is_active
  })
  
  defaultParamsText.value = JSON.stringify(model.default_params || {}, null, 2)
  
  dialogVisible.value = true
}

const deleteModel = async (model: AIModel) => {
  try {
    await aiModelApi.delete(model.id)
    ElMessage.success('删除成功')
    refreshData()
  } catch (error) {
    console.error('删除模型失败:', error)
  }
}

const handleStatusChange = async (model: AIModel & { statusLoading?: boolean }) => {
  model.statusLoading = true
  try {
    await aiModelApi.update(model.id, { is_active: model.is_active })
    ElMessage.success(`${model.is_active ? '启用' : '禁用'}成功`)
  } catch (error) {
    // 恢复原状态
    model.is_active = !model.is_active
    console.error('更新状态失败:', error)
  } finally {
    model.statusLoading = false
  }
}

const testConnection = async () => {
  if (!formData.api_endpoint || !formData.api_key || !formData.model_type) {
    ElMessage.warning('请先填写API端点、密钥和模型类型')
    return
  }
  
  testLoading.value = true
  try {
    const result = await aiModelApi.testConnection({
      api_endpoint: formData.api_endpoint,
      api_key: formData.api_key,
      model_type: formData.model_type
    })
    
    if (result.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error(`连接测试失败: ${result.message}`)
    }
  } catch (error) {
    console.error('测试连接失败:', error)
  } finally {
    testLoading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  // 解析默认参数
  let defaultParams = {}
  if (defaultParamsText.value.trim()) {
    try {
      defaultParams = JSON.parse(defaultParamsText.value)
    } catch (error) {
      ElMessage.error('默认参数格式错误，请输入有效的JSON')
      return
    }
  }
  
  const submitData = {
    ...formData,
    default_params: defaultParams
  }
  
  submitLoading.value = true
  try {
    if (isEdit.value && currentModel.value) {
      await aiModelApi.update(currentModel.value.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await aiModelApi.create(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    refreshData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    name: '',
    model_type: '',
    api_endpoint: '',
    api_key: '',
    default_params: {},
    is_active: true
  })
  defaultParamsText.value = ''
  formRef.value?.resetFields()
}

const getModelTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    'OpenAI-Compatible': 'primary',
    'Gemini': 'success',
    'Claude': 'warning',
    'Other': 'info'
  }
  return typeMap[type] || 'info'
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

const formatJSON = (obj: any) => {
  return JSON.stringify(obj, null, 2)
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.model-config {
  padding: 0;
}

.search-row {
  margin-bottom: 20px;
}

.model-name {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.api-endpoint {
  max-width: 200px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.model-detail {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.detail-item label {
  min-width: 80px;
  font-weight: 600;
  color: #606266;
}

.detail-item span {
  flex: 1;
  word-break: break-all;
}

.json-display {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 768px) {
  .search-row .el-col {
    margin-bottom: 10px;
  }
  
  .model-name {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>