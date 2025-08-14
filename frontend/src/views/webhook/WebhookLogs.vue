<template>
  <div class="webhook-logs">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h1 class="page-title">Webhook日志</h1>
        <el-tag v-if="webhookInfo" type="primary" class="ml-10">
          {{ webhookInfo.name }}
        </el-tag>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData" :loading="loading">
          刷新
        </el-button>
        <el-button :icon="Delete" @click="clearLogs" type="danger">
          清空日志
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="page-container">
      <el-row :gutter="20" class="search-row">
        <el-col :xs="24" :sm="12" :md="6">
          <el-select
            v-model="searchForm.status"
            placeholder="选择状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="超时" value="timeout" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
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
        <el-col :xs="24" :sm="12" :md="6">
          <el-date-picker
            v-model="searchForm.start_date"
            type="datetime"
            placeholder="开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="handleSearch"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-date-picker
            v-model="searchForm.end_date"
            type="datetime"
            placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="handleSearch"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 统计信息 -->
    <div class="page-container">
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="12" :sm="6">
          <div class="stat-card success">
            <div class="stat-number">{{ stats.success_count }}</div>
            <div class="stat-label">成功</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card failed">
            <div class="stat-number">{{ stats.failed_count }}</div>
            <div class="stat-label">失败</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card timeout">
            <div class="stat-number">{{ stats.timeout_count }}</div>
            <div class="stat-label">超时</div>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="stat-card total">
            <div class="stat-number">{{ stats.total_count }}</div>
            <div class="stat-label">总计</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 日志列表 -->
    <div class="page-container">
      <el-table
        v-loading="loading"
        :data="logList"
        stripe
        @sort-change="handleSortChange"
        @expand-change="handleExpandChange"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="log-detail">
              <div class="detail-section">
                <h4>请求信息</h4>
                <div class="detail-content">
                  <div class="detail-item">
                    <label>URL:</label>
                    <code>{{ row.request_url }}</code>
                  </div>
                  <div class="detail-item">
                    <label>方法:</label>
                    <el-tag :type="getMethodTagType(row.request_method)" size="small">
                      {{ row.request_method }}
                    </el-tag>
                  </div>
                  <div class="detail-item">
                    <label>请求头:</label>
                    <pre class="json-content">{{ formatJson(row.request_headers) }}</pre>
                  </div>
                  <div class="detail-item">
                    <label>请求体:</label>
                    <pre class="json-content">{{ formatJson(row.request_body) }}</pre>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>响应信息</h4>
                <div class="detail-content">
                  <div class="detail-item">
                    <label>状态码:</label>
                    <el-tag :type="getStatusTagType(row.response_status)" size="small">
                      {{ row.response_status || 'N/A' }}
                    </el-tag>
                  </div>
                  <div class="detail-item">
                    <label>响应头:</label>
                    <pre class="json-content">{{ formatJson(row.response_headers) }}</pre>
                  </div>
                  <div class="detail-item">
                    <label>响应体:</label>
                    <pre class="json-content">{{ formatJson(row.response_body) }}</pre>
                  </div>
                  <div class="detail-item">
                    <label>耗时:</label>
                    <span>{{ row.duration }}ms</span>
                  </div>
                </div>
              </div>
              
              <div v-if="row.error_message" class="detail-section">
                <h4>错误信息</h4>
                <div class="detail-content">
                  <div class="error-message">
                    {{ row.error_message }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="event_type" label="事件类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getEventTagType(row.event_type)" size="small">
              {{ getEventTypeLabel(row.event_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="request_method" label="方法" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.request_method)" size="small">
              {{ row.request_method }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="response_status" label="状态码" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.response_status">
              {{ row.response_status }}
            </span>
            <el-text v-else type="info">N/A</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="duration" label="耗时" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.duration !== null">
              {{ row.duration }}ms
            </span>
            <el-text v-else type="info">N/A</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="retry_count" label="重试次数" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.retry_count > 0">
              {{ row.retry_count }}
            </span>
            <el-text v-else type="info">0</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="error_message" label="错误信息" min-width="200">
          <template #default="{ row }">
            <el-text v-if="row.error_message" class="error-text" truncated>
              {{ row.error_message }}
            </el-text>
            <el-text v-else type="success">无</el-text>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="触发时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Refresh"
              @click="retryWebhook(row)"
              :loading="row.retryLoading"
              :disabled="row.status === 'success'"
            >
              重试
            </el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Refresh,
  Delete
} from '@element-plus/icons-vue'
import { webhookApi } from '@/api'
import type { WebhookLog, Webhook } from '@/types/api'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const logList = ref<(WebhookLog & { retryLoading?: boolean })[]>([])
const webhookInfo = ref<Webhook | null>(null)
const webhookId = computed(() => route.params.id as string)

// 搜索表单
const searchForm = reactive({
  status: '',
  event_type: '',
  start_date: '',
  end_date: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 统计信息
const stats = reactive({
  success_count: 0,
  failed_count: 0,
  timeout_count: 0,
  total_count: 0
})

// 方法
const refreshData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      status: searchForm.status || undefined,
      event_type: searchForm.event_type || undefined,
      start_date: searchForm.start_date || undefined,
      end_date: searchForm.end_date || undefined
    }
    
    const response = await webhookApi.getLogs(Number(webhookId.value), params)
    logList.value = response.items.map(item => ({ 
      ...item, 
      retryLoading: false
    }))
    pagination.total = response.total
    
    // 更新统计信息
    updateStats()
  } catch (error) {
    console.error('获取Webhook日志失败:', error)
  } finally {
    loading.value = false
  }
}

const loadWebhookInfo = async () => {
  try {
    webhookInfo.value = await webhookApi.getById(Number(webhookId.value))
  } catch (error) {
    console.error('获取Webhook信息失败:', error)
  }
}

const updateStats = () => {
  stats.success_count = logList.value.filter(log => log.status === 'success').length
  stats.failed_count = logList.value.filter(log => log.status === 'failed').length
  stats.timeout_count = logList.value.filter(log => log.status === 'timeout').length
  stats.total_count = logList.value.length
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

const handleExpandChange = (row: WebhookLog, expanded: boolean) => {
  // 展开时可以加载更多详细信息
  if (expanded) {
    console.log('展开日志详情:', row.id)
  }
}

const retryWebhook = async (log: WebhookLog & { retryLoading?: boolean }) => {
  log.retryLoading = true
  try {
    await webhookApi.retry(log.id)
    ElMessage.success('重试请求已发送')
    // 刷新数据以查看重试结果
    setTimeout(() => {
      refreshData()
    }, 2000)
  } catch (error) {
    console.error('重试Webhook失败:', error)
  } finally {
    log.retryLoading = false
  }
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await webhookApi.clearLogs(Number(webhookId.value))
    ElMessage.success('日志已清空')
    refreshData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空日志失败:', error)
    }
  }
}

const goBack = () => {
  router.push({ name: 'WebhookList' })
}

const getStatusTagType = (status: string | number) => {
  if (typeof status === 'number') {
    if (status >= 200 && status < 300) return 'success'
    if (status >= 400 && status < 500) return 'warning'
    if (status >= 500) return 'danger'
    return 'info'
  }
  
  const typeMap: Record<string, string> = {
    'success': 'success',
    'failed': 'danger',
    'timeout': 'warning'
  }
  return typeMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    'success': '成功',
    'failed': '失败',
    'timeout': '超时'
  }
  return labelMap[status] || status
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

const formatJson = (data: any) => {
  if (!data) return 'N/A'
  try {
    return JSON.stringify(data, null, 2)
  } catch {
    return String(data)
  }
}

// 生命周期
onMounted(() => {
  loadWebhookInfo()
  refreshData()
})
</script>

<style scoped>
.webhook-logs {
  padding: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-row {
  margin-bottom: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ddd;
}

.stat-card.success {
  border-left-color: #67c23a;
}

.stat-card.failed {
  border-left-color: #f56c6c;
}

.stat-card.timeout {
  border-left-color: #e6a23c;
}

.stat-card.total {
  border-left-color: #409eff;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-card.success .stat-number {
  color: #67c23a;
}

.stat-card.failed .stat-number {
  color: #f56c6c;
}

.stat-card.timeout .stat-number {
  color: #e6a23c;
}

.stat-card.total .stat-number {
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.log-detail {
  padding: 20px;
  background-color: #fafafa;
  border-radius: 4px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  font-size: 12px;
}

.detail-item code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.json-content {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
  margin: 0;
  flex: 1;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  border-left: 4px solid #f56c6c;
}

.error-text {
  color: #f56c6c;
  max-width: 200px;
}

@media (max-width: 768px) {
  .search-row .el-col {
    margin-bottom: 10px;
  }
  
  .stats-row .el-col {
    margin-bottom: 10px;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
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