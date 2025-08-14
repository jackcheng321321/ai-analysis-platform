<template>
  <div class="webhook-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">Webhook管理</h1>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog">
          创建Webhook
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
            placeholder="搜索Webhook名称或URL"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8">
          <el-select
            v-model="searchForm.event_type"
            placeholder="选择事件类型"
            clearable
            @change="handleSearch"
          >
            <el-option label="任务完成" value="task_completed" />
            <el-option label="任务失败" value="task_failed" />
            <el-option label="任务开始" value="task_started" />
            <el-option label="系统错误" value="system_error" />
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

    <!-- Webhook列表 -->
    <div class="page-container">
      <el-table
        v-loading="loading"
        :data="webhookList"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column prop="name" label="Webhook名称" sortable min-width="150">
          <template #default="{ row }">
            <div class="webhook-name">
              <strong>{{ row.name }}</strong>
              <el-tag
                :type="getEventTagType(row.event_type)"
                size="small"
                class="ml-10"
              >
                {{ getEventTypeLabel(row.event_type) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="url" label="URL地址" min-width="250">
          <template #default="{ row }">
            <el-text class="webhook-url" truncated>
              {{ row.url }}
            </el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="method" label="请求方法" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.method)" size="small">
              {{ row.method }}
            </el-tag>
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
        
        <el-table-column prop="last_triggered_at" label="最后触发" width="180">
          <template #default="{ row }">
            <span v-if="row.last_triggered_at">
              {{ formatTime(row.last_triggered_at) }}
            </span>
            <el-text v-else type="info">未触发</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="success"
              size="small"
              :icon="Connection"
              @click="testWebhook(row)"
              :loading="row.testLoading"
            >
              测试
            </el-button>
            <el-button
              type="info"
              size="small"
              :icon="Document"
              @click="viewLogs(row)"
            >
              日志
            </el-button>
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="viewWebhook(row)"
            >
              查看
            </el-button>
            <el-button
              type="warning"
              size="small"
              :icon="Edit"
              @click="editWebhook(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这个Webhook吗？"
              @confirm="deleteWebhook(row)"
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
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="Webhook名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入Webhook名称"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="URL地址" prop="url">
          <el-input
            v-model="formData.url"
            placeholder="请输入Webhook URL地址"
            type="url"
          />
          <div class="form-tip">
            例如: https://api.example.com/webhook/callback
          </div>
        </el-form-item>
        
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="formData.method" placeholder="请选择请求方法">
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="PATCH" value="PATCH" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="事件类型" prop="event_type">
          <el-select v-model="formData.event_type" placeholder="请选择事件类型">
            <el-option label="任务完成" value="task_completed" />
            <el-option label="任务失败" value="task_failed" />
            <el-option label="任务开始" value="task_started" />
            <el-option label="系统错误" value="system_error" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="请求头">
          <div class="headers-container">
            <div 
              v-for="(header, index) in formData.headers" 
              :key="index" 
              class="header-item"
            >
              <el-input
                v-model="header.key"
                placeholder="Header名称"
                style="width: 40%"
              />
              <el-input
                v-model="header.value"
                placeholder="Header值"
                style="width: 50%"
              />
              <el-button
                type="danger"
                :icon="Delete"
                size="small"
                @click="removeHeader(index)"
                style="width: 8%"
              />
            </div>
            <el-button
              type="primary"
              :icon="Plus"
              size="small"
              @click="addHeader"
            >
              添加Header
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="超时时间">
          <el-input-number
            v-model="formData.timeout"
            :min="1"
            :max="300"
            :step="1"
            controls-position="right"
          />
          <span class="ml-10">秒</span>
        </el-form-item>
        
        <el-form-item label="重试次数">
          <el-input-number
            v-model="formData.retry_count"
            :min="0"
            :max="10"
            :step="1"
            controls-position="right"
          />
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
            @click="testFormWebhook"
            :loading="testLoading"
          >
            测试Webhook
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
      title="Webhook详情"
      width="600px"
    >
      <div v-if="currentWebhook" class="webhook-detail">
        <div class="detail-item">
          <label>Webhook名称:</label>
          <span>{{ currentWebhook.name }}</span>
        </div>
        <div class="detail-item">
          <label>URL地址:</label>
          <span class="url-text">{{ currentWebhook.url }}</span>
        </div>
        <div class="detail-item">
          <label>请求方法:</label>
          <el-tag :type="getMethodTagType(currentWebhook.method)">
            {{ currentWebhook.method }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>事件类型:</label>
          <el-tag :type="getEventTagType(currentWebhook.event_type || '')">
            {{ getEventTypeLabel(currentWebhook.event_type || '') }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>请求头:</label>
          <div class="headers-display">
            <div 
              v-for="(value, key) in currentWebhook.headers" 
              :key="key"
              class="header-display-item"
            >
              <code>{{ key }}: {{ value }}</code>
            </div>
            <span v-if="!Object.keys(currentWebhook.headers || {}).length" class="no-headers">
              无自定义请求头
            </span>
          </div>
        </div>
        <div class="detail-item">
          <label>超时时间:</label>
          <span>{{ currentWebhook.timeout }}秒</span>
        </div>
        <div class="detail-item">
          <label>重试次数:</label>
          <span>{{ currentWebhook.retry_count }}次</span>
        </div>
        <div class="detail-item">
          <label>状态:</label>
          <el-tag :type="currentWebhook.is_active ? 'success' : 'danger'">
            {{ currentWebhook.is_active ? '启用' : '禁用' }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>最后触发:</label>
          <span v-if="currentWebhook.last_triggered_at">
            {{ formatTime(currentWebhook.last_triggered_at) }}
          </span>
          <el-text v-else type="info">未触发</el-text>
        </div>
        <div class="detail-item">
          <label>创建时间:</label>
          <span>{{ formatTime(currentWebhook.created_at) }}</span>
        </div>
        <div class="detail-item">
          <label>更新时间:</label>
          <span>{{ formatTime(currentWebhook.updated_at) }}</span>
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
  Connection,
  Document
} from '@element-plus/icons-vue'
import { webhookApi } from '@/api'
import type { Webhook, WebhookCreate } from '@/types/api'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const webhookList = ref<(Webhook & { statusLoading?: boolean; testLoading?: boolean })[]>([])
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const isEdit = ref(false)
const currentWebhook = ref<Webhook | null>(null)
const testLoading = ref(false)
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  search: '',
  event_type: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 表单数据
const formData = reactive<WebhookCreate & { headers: Array<{ key: string; value: string }> }>({
  name: '',
  url: '',
  method: 'POST',
  event_type: '',
  headers: [],
  timeout: 30,
  retry_count: 3,
  is_active: true
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入Webhook名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入URL地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  event_type: [
    { required: true, message: '请选择事件类型', trigger: 'change' }
  ]
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑Webhook' : '创建Webhook')

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      search: searchForm.search || undefined,
      event_type: searchForm.event_type || undefined,
      is_active: searchForm.status === 'active' ? true : searchForm.status === 'inactive' ? false : undefined
    }
    
    const response = await webhookApi.getList(params)
    webhookList.value = response.items.map(item => ({ 
      ...item, 
      statusLoading: false,
      testLoading: false
    }))
    pagination.total = response.total
  } catch (error) {
    console.error('获取Webhook列表失败:', error)
  } finally {
    loading.value = false
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

const viewWebhook = (webhook: Webhook) => {
  currentWebhook.value = webhook
  viewDialogVisible.value = true
}

const editWebhook = (webhook: Webhook) => {
  isEdit.value = true
  currentWebhook.value = webhook
  
  // 填充表单数据
  Object.assign(formData, {
    name: webhook.name,
    url: webhook.url,
    method: webhook.method,
    event_type: webhook.event_type,
    headers: Object.entries(webhook.headers || {}).map(([key, value]) => ({ key, value })),
    timeout: webhook.timeout,
    retry_count: webhook.retry_count,
    is_active: webhook.is_active
  })
  
  dialogVisible.value = true
}

const deleteWebhook = async (webhook: Webhook) => {
  try {
    await webhookApi.delete(webhook.id)
    ElMessage.success('删除成功')
    refreshData()
  } catch (error) {
    console.error('删除Webhook失败:', error)
  }
}

const handleStatusChange = async (webhook: Webhook & { statusLoading?: boolean }) => {
  webhook.statusLoading = true
  try {
    await webhookApi.update(webhook.id, { is_active: webhook.is_active })
    ElMessage.success(`${webhook.is_active ? '启用' : '禁用'}成功`)
  } catch (error) {
    // 恢复原状态
    webhook.is_active = !webhook.is_active
    console.error('更新状态失败:', error)
  } finally {
    webhook.statusLoading = false
  }
}

const testWebhook = async (webhook: Webhook & { testLoading?: boolean }) => {
  webhook.testLoading = true
  try {
    const result = await webhookApi.test(webhook.id)
    
    if (result.success) {
      ElMessage.success('Webhook测试成功')
    } else {
      ElMessage.error(`Webhook测试失败: ${result.message}`)
    }
  } catch (error) {
    console.error('测试Webhook失败:', error)
  } finally {
    webhook.testLoading = false
  }
}

const testFormWebhook = async () => {
  if (!formData.url || !formData.method || !formData.event_type) {
    ElMessage.warning('请先填写完整的Webhook信息')
    return
  }
  
  testLoading.value = true
  try {
    // 转换headers格式
    const headers = formData.headers.reduce((acc, header) => {
      if (header.key && header.value) {
        acc[header.key] = header.value
      }
      return acc
    }, {} as Record<string, string>)
    
    const result = await webhookApi.testUrl({
      url: formData.url,
      method: formData.method,
      headers,
      timeout: formData.timeout
    })
    
    if (result.success) {
      ElMessage.success('Webhook测试成功')
    } else {
      ElMessage.error(`Webhook测试失败: ${result.message}`)
    }
  } catch (error) {
    console.error('测试Webhook失败:', error)
  } finally {
    testLoading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitLoading.value = true
  try {
    // 过滤有效的headers
    const headers = formData.headers.filter(header => header.key && header.value)
    
    const submitData = {
      name: formData.name,
      url: formData.url,
      method: formData.method,
      event_type: formData.event_type,
      headers,
      timeout: formData.timeout,
      retry_count: formData.retry_count,
      is_active: formData.is_active
    }
    
    if (isEdit.value && currentWebhook.value) {
      await webhookApi.update(currentWebhook.value.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await webhookApi.create(submitData)
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
    url: '',
    method: 'POST',
    event_type: '',
    headers: [],
    timeout: 30,
    retry_count: 3,
    is_active: true
  })
  formRef.value?.resetFields()
}

const addHeader = () => {
  formData.headers.push({ key: '', value: '' })
}

const removeHeader = (index: number) => {
  formData.headers.splice(index, 1)
}

const viewLogs = (webhook: Webhook) => {
  router.push({ name: 'WebhookLogs', params: { id: webhook.id } })
}

const getEventTagType = (eventType: string) => {
  const typeMap: Record<string, string> = {
    'task_completed': 'success',
    'task_failed': 'danger',
    'task_started': 'primary',
    'system_error': 'warning'
  }
  return typeMap[eventType] || 'info'
}

const getEventTypeLabel = (eventType: string) => {
  const labelMap: Record<string, string> = {
    'task_completed': '任务完成',
    'task_failed': '任务失败',
    'task_started': '任务开始',
    'system_error': '系统错误'
  }
  return labelMap[eventType] || eventType
}

const getMethodTagType = (method: string) => {
  const typeMap: Record<string, string> = {
    'POST': 'primary',
    'PUT': 'success',
    'PATCH': 'warning'
  }
  return typeMap[method] || 'info'
}

const formatTime = (time: string) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.webhook-list {
  padding: 0;
}

.search-row {
  margin-bottom: 20px;
}

.webhook-name {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.webhook-url {
  max-width: 250px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.headers-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-item {
  display: flex;
  align-items: center;
  gap: 10px;
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

.webhook-detail {
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

.url-text {
  font-family: 'Courier New', monospace;
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.headers-display {
  flex: 1;
}

.header-display-item {
  margin-bottom: 5px;
}

.header-display-item code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.no-headers {
  color: #909399;
  font-style: italic;
}

@media (max-width: 768px) {
  .search-row .el-col {
    margin-bottom: 10px;
  }
  
  .webhook-name {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-item .el-input {
    width: 100% !important;
  }
  
  .header-item .el-button {
    width: auto !important;
    align-self: flex-end;
  }
}
</style>