<template>
  <div class="task-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">任务管理</h1>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          创建任务
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
            placeholder="搜索任务名称或描述"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
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
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="searchForm.ai_model_id"
            placeholder="选择AI模型"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="model in aiModels"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 任务列表 -->
    <div class="page-container">
      <el-table
        v-loading="loading"
        :data="taskList"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="任务名称" sortable min-width="150">
          <template #default="{ row }">
            <div class="task-name">
              <strong>{{ row.name }}</strong>
              <el-tag
                v-if="row.is_scheduled"
                type="info"
                size="small"
                class="ml-10"
              >
                定时任务
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200">
          <template #default="{ row }">
            <el-text class="task-description" truncated>
              {{ row.description || '无描述' }}
            </el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="ai_model" label="AI模型" width="150">
          <template #default="{ row }">
            <el-text v-if="row.ai_model" truncated>
              {{ row.ai_model.name }}
            </el-text>
            <el-text v-else type="info">未配置</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="storage_credential" label="存储凭证" width="150">
          <template #default="{ row }">
            <el-text v-if="row.storage_credential" truncated>
              {{ row.storage_credential.name }}
            </el-text>
            <el-text v-else type="info">未配置</el-text>
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
        
        <el-table-column prop="last_executed_at" label="最后执行" width="180">
          <template #default="{ row }">
            <span v-if="row.last_executed_at">
              {{ formatTime(row.last_executed_at) }}
            </span>
            <el-text v-else type="info">未执行</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button
              type="success"
              size="small"
              :icon="VideoPlay"
              @click="executeTask(row)"
              :loading="row.executeLoading"
              :disabled="!row.is_active"
            >
              执行
            </el-button>
            <el-button
              type="info"
              size="small"
              :icon="Document"
              @click="viewExecutions(row)"
            >
              记录
            </el-button>
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="viewTask(row)"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="editTask(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这个任务吗？"
              @confirm="deleteTask(row)"
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
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入任务名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="任务描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            placeholder="请输入任务描述"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="AI模型" prop="ai_model_id">
          <el-select 
            v-model="formData.ai_model_id" 
            placeholder="请选择AI模型"
            style="width: 100%"
          >
            <el-option
              v-for="model in aiModels"
              :key="model.id"
              :label="`${model.name} (${model.model_type})`"
              :value="model.id"
            >
              <div class="model-option">
                <span>{{ model.name }}</span>
                <small>{{ model.model_type }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="存储凭证" prop="storage_credential_id">
          <el-select 
            v-model="formData.storage_credential_id" 
            placeholder="请选择存储凭证"
            style="width: 100%"
          >
            <el-option
              v-for="credential in storageCredentials"
              :key="credential.id"
              :label="`${credential.name} (${credential.protocol_type})`"
              :value="credential.id"
            >
              <div class="credential-option">
                <span>{{ credential.name }}</span>
                <small>{{ credential.protocol_type }} - {{ credential.server_address }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        

        
        <el-form-item label="分析提示词" prop="analysis_prompt">
          <el-input
            v-model="formData.analysis_prompt"
            type="textarea"
            placeholder="请输入分析提示词，告诉AI如何分析文件"
            :rows="4"
            maxlength="2000"
            show-word-limit
          />
          <div class="form-tip">
            例如: 请分析这个文档的主要内容，提取关键信息并总结要点
          </div>
        </el-form-item>
        
        <el-form-item label="定时执行">
          <el-switch 
            v-model="formData.is_scheduled" 
            @change="handleScheduleChange"
          />
        </el-form-item>
        
        <el-form-item 
          v-if="formData.is_scheduled" 
          label="Cron表达式" 
          prop="cron_expression"
        >
          <el-input
            v-model="formData.cron_expression"
            placeholder="请输入Cron表达式"
          />
          <div class="form-tip">
            例如: 0 0 9 * * ? (每天上午9点执行)
            <el-link type="primary" href="https://cron.qqe2.com/" target="_blank">
              Cron表达式生成器
            </el-link>
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
      title="任务详情"
      width="700px"
    >
      <div v-if="currentTask" class="task-detail">
        <div class="detail-item">
          <label>任务名称:</label>
          <span>{{ currentTask.name }}</span>
        </div>
        <div class="detail-item">
          <label>任务描述:</label>
          <span>{{ currentTask.description || '无描述' }}</span>
        </div>
        <div class="detail-item">
          <label>AI模型:</label>
          <span v-if="currentTask.ai_model">
            {{ currentTask.ai_model.name }} ({{ currentTask.ai_model.model_type }})
          </span>
          <el-text v-else type="info">未配置</el-text>
        </div>
        <div class="detail-item">
          <label>存储凭证:</label>
          <span v-if="currentTask.storage_credential">
            {{ currentTask.storage_credential.name }} ({{ currentTask.storage_credential.protocol_type }})
          </span>
          <el-text v-else type="info">未配置</el-text>
        </div>
        <div class="detail-item">
          <label>分析提示词:</label>
          <div class="prompt-content">
            {{ currentTask.analysis_prompt }}
          </div>
        </div>
        <div class="detail-item">
          <label>定时执行:</label>
          <el-tag :type="currentTask.is_scheduled ? 'success' : 'info'">
            {{ currentTask.is_scheduled ? '是' : '否' }}
          </el-tag>
        </div>
        <div v-if="currentTask.is_scheduled" class="detail-item">
          <label>Cron表达式:</label>
          <code>{{ currentTask.cron_expression }}</code>
        </div>
        <div class="detail-item">
          <label>状态:</label>
          <el-tag :type="currentTask.is_active ? 'success' : 'danger'">
            {{ currentTask.is_active ? '启用' : '禁用' }}
          </el-tag>
        </div>

        <div class="detail-item">
          <label>创建时间:</label>
          <span>{{ formatTime(currentTask.created_at) }}</span>
        </div>
        <div class="detail-item">
          <label>更新时间:</label>
          <span>{{ formatTime(currentTask.updated_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus,
  Refresh,
  Search,
  View,
  Edit,
  Delete,
  VideoPlay,
  Document
} from '@element-plus/icons-vue'
import { taskApi, aiModelApi, storageApi } from '@/api'
import type { AnalysisTask, AnalysisTaskCreate, AIModel, StorageCredential } from '@/types/api'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const taskList = ref<(AnalysisTask & { statusLoading?: boolean; executeLoading?: boolean })[]>([])
const aiModels = ref<AIModel[]>([])
const storageCredentials = ref<StorageCredential[]>([])
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const currentTask = ref<AnalysisTask | null>(null)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  search: '',
  status: '',
  ai_model_id: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive<AnalysisTaskCreate>({
  name: '',
  description: '',
  webhook_id: 0,
  ai_model_id: 0,
  storage_credential_id: 0,
  analysis_prompt: '',
  is_scheduled: false,
  cron_expression: '',
  data_extraction_config: {},
  prompt_template: '',
  feishu_config: {},
  field_mapping: {},
  is_active: true
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  ai_model_id: [
    { required: true, message: '请选择AI模型', trigger: 'change' }
  ],
  storage_credential_id: [
    { required: true, message: '请选择存储凭证', trigger: 'change' }
  ],
  file_path: [
    { required: true, message: '请输入文件路径', trigger: 'blur' }
  ],
  analysis_prompt: [
    { required: true, message: '请输入分析提示词', trigger: 'blur' },
    { min: 10, max: 2000, message: '长度在 10 到 2000 个字符', trigger: 'blur' }
  ],
  cron_expression: [
    { 
      validator: (rule, value, callback) => {
        if (formData.is_scheduled && !value) {
          callback(new Error('定时任务需要设置Cron表达式'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑任务' : '创建任务')

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      ai_model_id: searchForm.ai_model_id || undefined,
      is_active: searchForm.status === 'active' ? true : searchForm.status === 'inactive' ? false : undefined
    }
    
    const response = await taskApi.getList(params)
    taskList.value = response.items.map(item => ({ 
      ...item, 
      statusLoading: false,
      executeLoading: false
    }))
    pagination.total = response.total
  } catch (error) {
    console.error('获取任务列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadAIModels = async () => {
  try {
    const response = await aiModelApi.getList({ size: 100 })
    aiModels.value = response.items.filter(item => item.is_active)
  } catch (error) {
    console.error('获取AI模型列表失败:', error)
  }
}

const loadStorageCredentials = async () => {
  try {
    const response = await storageApi.getList({ size: 100 })
    storageCredentials.value = response.items.filter(item => item.is_active)
  } catch (error) {
    console.error('获取存储凭证列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  refreshData()
}

const handleSortChange = ({ prop, order }: any) => {
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

const viewTask = (task: AnalysisTask) => {
  currentTask.value = task
  viewDialogVisible.value = true
}

const editTask = (task: AnalysisTask) => {
  isEdit.value = true
  currentTask.value = task
  
  // 填充表单数据
  Object.assign(formData, {
    name: task.name,
    description: task.description,
    ai_model_id: task.ai_model_id,
    storage_credential_id: task.storage_credential_id,
    analysis_prompt: task.analysis_prompt,
    is_scheduled: task.is_scheduled,
    cron_expression: task.cron_expression,
    is_active: task.is_active
  })
  
  dialogVisible.value = true
}

const deleteTask = async (task: AnalysisTask) => {
  try {
    await taskApi.delete(task.id)
    ElMessage.success('删除成功')
    refreshData()
  } catch (error) {
    console.error('删除任务失败:', error)
  }
}

const handleStatusChange = async (task: AnalysisTask & { statusLoading?: boolean }) => {
  task.statusLoading = true
  try {
    await taskApi.update(task.id, { is_active: task.is_active })
    ElMessage.success(`${task.is_active ? '启用' : '禁用'}成功`)
  } catch (error) {
    // 恢复原状态
    task.is_active = !task.is_active
    console.error('更新状态失败:', error)
  } finally {
    task.statusLoading = false
  }
}

const executeTask = async (task: AnalysisTask & { executeLoading?: boolean }) => {
  task.executeLoading = true
  try {
    const result = await taskApi.execute(task.id)
    ElMessage.success('任务执行已启动')
    
    // 可以跳转到执行记录页面查看结果
    if (result.execution_id) {
      ElMessageBox.confirm(
        '任务已开始执行，是否查看执行记录？',
        '执行成功',
        {
          confirmButtonText: '查看记录',
          cancelButtonText: '稍后查看',
          type: 'success'
        }
      ).then(() => {
        router.push({ 
          name: 'TaskExecutions', 
          params: { id: task.id },
          query: { execution_id: result.execution_id }
        })
      }).catch(() => {})
    }
  } catch (error) {
    console.error('执行任务失败:', error)
  } finally {
    task.executeLoading = false
  }
}

const viewExecutions = (task: AnalysisTask) => {
  router.push({ name: 'TaskExecutions', params: { id: task.id } })
}

const submitForm = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitLoading.value = true
  try {
    if (isEdit.value && currentTask.value) {
      await taskApi.update(currentTask.value.id, formData)
      ElMessage.success('更新成功')
    } else {
      await taskApi.create(formData)
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
    description: '',
    ai_model_id: '',
    storage_credential_id: '',
    file_path: '',
    analysis_prompt: '',
    is_scheduled: false,
    cron_expression: '',
    is_active: true
  })
  formRef.value?.resetFields()
}

const handleScheduleChange = (value: boolean) => {
  if (!value) {
    formData.cron_expression = ''
  }
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  refreshData()
  loadAIModels()
  loadStorageCredentials()
})
</script>

<style scoped>
.task-list {
  padding: 0;
}

.search-row {
  margin-bottom: 20px;
}

.task-name {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.task-description {
  max-width: 200px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.model-option,
.credential-option {
  display: flex;
  flex-direction: column;
}

.model-option small,
.credential-option small {
  color: #909399;
  font-size: 12px;
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

.task-detail {
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
  min-width: 100px;
  font-weight: 600;
  color: #606266;
}

.detail-item span {
  flex: 1;
  word-break: break-all;
}

.detail-item code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.prompt-content {
  flex: 1;
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .search-row .el-col {
    margin-bottom: 10px;
  }
  
  .task-name {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-item label {
    min-width: auto;
  }
}
</style>