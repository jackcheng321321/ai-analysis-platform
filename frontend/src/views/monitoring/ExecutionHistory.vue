<template>
  <div class="execution-history">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">执行历史</h1>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData" :loading="loading">
          刷新
        </el-button>
        <el-button :icon="Download" @click="exportData">
          导出
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="filters" inline>
        <el-form-item label="任务">
          <el-select
            v-model="filters.task_id"
            placeholder="选择任务"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="task in taskOptions"
              :key="task.id"
              :label="task.name"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="等待中" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="触发方式">
          <el-select
            v-model="filters.trigger_type"
            placeholder="选择触发方式"
            clearable
            style="width: 120px"
          >
            <el-option label="手动" value="manual" />
            <el-option label="定时" value="scheduled" />
            <el-option label="Webhook" value="webhook" />
            <el-option label="API" value="api" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.date_range"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 350px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="searchData">
            搜索
          </el-button>
          <el-button @click="resetFilters">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="执行ID" width="120" sortable="custom" />
        
        <el-table-column prop="task_name" label="任务名称" min-width="150">
          <template #default="{ row }">
            <el-link
              type="primary"
              @click="viewTaskDetail(row.task_id)"
              :underline="false"
            >
              {{ row.task_name }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="trigger_type" label="触发方式" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ getTriggerTypeLabel(row.trigger_type) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_path" label="文件路径" min-width="200">
          <template #default="{ row }">
            <span class="path-text">{{ row.file_path || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="duration" label="耗时" width="100" sortable="custom">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="tokens_used" label="Token" width="100" sortable="custom">
          <template #default="{ row }">
            {{ formatNumber(row.tokens_used) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="started_at" label="开始时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatTime(row.started_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="completed_at" label="完成时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatTime(row.completed_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="View"
              @click="viewDetail(row)"
            >
              详情
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              type="danger"
              size="small"
              :icon="Close"
              @click="cancelExecution(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 执行详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="执行详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="selectedExecution" class="execution-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行ID">
            {{ selectedExecution.id }}
          </el-descriptions-item>
          <el-descriptions-item label="任务名称">
            <el-link
              type="primary"
              @click="viewTaskDetail(selectedExecution.task_id.toString())"
              :underline="false"
            >
              {{ selectedExecution.task?.name || '-' }}
            </el-link>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedExecution.execution_status)">
              {{ getStatusLabel(selectedExecution.execution_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="触发方式">
            <el-tag>手动执行</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="文件路径">
            <span class="path-text">-</span>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ selectedExecution.execution_time_ms ? formatDuration(selectedExecution.execution_time_ms) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="Token消耗">
            {{ formatNumber(selectedExecution.token_usage || 0) }}
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(0) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatTime(selectedExecution.started_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ selectedExecution.completed_at ? formatTime(selectedExecution.completed_at) : '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <!-- 执行结果 -->
        <div class="result-section">
          <h4>执行结果</h4>
          <div v-if="selectedExecution.ai_response" class="result-content">
            <pre>{{ JSON.stringify(selectedExecution.ai_response, null, 2) }}</pre>
          </div>
          <el-text v-else type="info">无执行结果</el-text>
        </div>
        
        <el-divider />
        
        <!-- 错误信息 -->
        <div v-if="selectedExecution.error_message" class="error-section">
          <h4>错误信息</h4>
          <div class="error-content">
            <pre>{{ selectedExecution.error_message }}</pre>
          </div>
        </div>
        
        <!-- 执行日志 -->
        <div class="logs-section">
          <h4>执行日志</h4>
          <div v-if="false" class="logs-content">
            <div 
              v-for="(log, index) in []"
              :key="index"
              class="log-item"
              class="log-info"
            >
              <span class="log-time">{{ formatTime(new Date().toISOString()) }}</span>
              <span class="log-level">INFO</span>
              <span class="log-message">暂无日志</span>
            </div>
          </div>
          <el-text v-else type="info">无执行日志</el-text>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="selectedExecution?.execution_status === 'processing'"
          type="danger"
          @click="cancelExecution(selectedExecution)"
        >
          取消执行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Download,
  Search,
  View,
  Close
} from '@element-plus/icons-vue'
import { taskApi, executionApi } from '@/api'
import type { TaskExecution, AnalysisTask } from '@/types/api'

const router = useRouter()

// 响应式数据
const loading = ref(false)
const detailDialogVisible = ref(false)

const filters = reactive({
  task_id: '',
  status: '',
  trigger_type: '',
  date_range: null as [string, string] | null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const sortConfig = reactive({
  prop: 'started_at',
  order: 'descending'
})

const tableData = ref<TaskExecution[]>([])
const taskOptions = ref<AnalysisTask[]>([])
const selectedExecution = ref<TaskExecution | null>(null)

// 方法
const refreshData = () => {
  loadData()
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      task_id: filters.task_id ? parseInt(filters.task_id) : undefined,
      status: filters.status || undefined,
      trigger_type: filters.trigger_type || undefined,
      start_date: filters.date_range?.[0],
      end_date: filters.date_range?.[1],
      sort_by: sortConfig.prop,
      sort_order: sortConfig.order === 'ascending' ? 'asc' : 'desc'
    }
    
    const response = await executionApi.getList(params)
    tableData.value = response.items
    pagination.total = response.total
  } catch (error) {
    console.error('获取执行历史失败:', error)
    ElMessage.error('获取执行历史失败')
  } finally {
    loading.value = false
  }
}

const loadTaskOptions = async () => {
  try {
    const response = await taskApi.getList({ page: 1, size: 1000 })
    taskOptions.value = response.items
  } catch (error) {
    console.error('获取任务列表失败:', error)
  }
}

const searchData = () => {
  pagination.page = 1
  loadData()
}

const resetFilters = () => {
  Object.assign(filters, {
    task_id: '',
    status: '',
    trigger_type: '',
    date_range: null
  })
  pagination.page = 1
  loadData()
}

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  sortConfig.prop = prop
  sortConfig.order = order
  loadData()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadData()
}

const viewDetail = (execution: TaskExecution) => {
  selectedExecution.value = execution
  detailDialogVisible.value = true
}

const viewTaskDetail = (taskId: string) => {
  router.push({ name: 'TaskDetail', params: { id: taskId } })
}

const cancelExecution = async (execution: TaskExecution) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消执行 "${execution.id}" 吗？`,
      '确认取消',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await executionApi.cancel(execution.id)
    ElMessage.success('执行已取消')
    loadData()
    
    if (detailDialogVisible.value) {
      detailDialogVisible.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消执行失败:', error)
      ElMessage.error('取消执行失败')
    }
  }
}

const exportData = async () => {
  try {
    const params = {
      task_id: filters.task_id || undefined,
      status: filters.status || undefined,
      trigger_type: filters.trigger_type || undefined,
      start_date: filters.date_range?.[0],
      end_date: filters.date_range?.[1]
    }
    
    const blob = await executionApi.export(params)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `execution_history_${new Date().toISOString().slice(0, 10)}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 工具方法
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    'pending': '等待中',
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消'
  }
  return labelMap[status] || status
}

const getTriggerTypeLabel = (triggerType: string) => {
  const labelMap: Record<string, string> = {
    'manual': '手动',
    'scheduled': '定时',
    'webhook': 'Webhook',
    'api': 'API'
  }
  return labelMap[triggerType] || triggerType
}

const formatTime = (time: string) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const formatDuration = (seconds: number) => {
  if (!seconds) return '0秒'
  
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return remainingSeconds > 0 ? `${minutes}分${remainingSeconds}秒` : `${minutes}分钟`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
  }
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

// 生命周期
onMounted(() => {
  loadTaskOptions()
  loadData()
})
</script>

<style scoped>
.execution-history {
  padding: 0;
}

.filter-card,
.table-card {
  margin-bottom: 20px;
}

.path-text {
  font-family: 'Courier New', monospace;
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.execution-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.result-section,
.error-section,
.logs-section {
  margin-top: 20px;
}

.result-section h4,
.error-section h4,
.logs-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.result-content,
.error-content {
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.result-content pre,
.error-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.logs-content {
  background: var(--el-fill-color-darker);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.log-item {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
  padding: 2px 0;
}

.log-time {
  color: var(--el-text-color-regular);
  min-width: 150px;
  flex-shrink: 0;
}

.log-level {
  min-width: 60px;
  flex-shrink: 0;
  font-weight: bold;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.log-info .log-level {
  color: var(--el-color-info);
}

.log-warning .log-level {
  color: var(--el-color-warning);
}

.log-error .log-level {
  color: var(--el-color-danger);
}

.log-debug .log-level {
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .el-form--inline .el-form-item {
    display: block;
    margin-right: 0;
    margin-bottom: 15px;
  }
  
  .el-form--inline .el-form-item .el-select,
  .el-form--inline .el-form-item .el-date-picker {
    width: 100% !important;
  }
}
</style>