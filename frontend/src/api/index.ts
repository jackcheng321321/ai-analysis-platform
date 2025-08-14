import { request } from '@/utils/request'
import type {
  AIModel,
  AIModelCreate,
  AIModelUpdate,
  StorageCredential,
  StorageCredentialCreate,
  StorageCredentialUpdate,
  Webhook,
  WebhookCreate,
  WebhookUpdate,
  AnalysisTask,
  AnalysisTaskCreate,
  AnalysisTaskUpdate,
  TaskExecution,
  DashboardStats,
  ExecutionStats,
  PaginatedResponse
} from '@/types/api'

// AI模型配置API
export const aiModelApi = {
  // 获取AI模型列表
  getList(params?: { page?: number; size?: number; search?: string }): Promise<PaginatedResponse<AIModel>> {
    return request.get('/ai-models', params)
  },
  
  // 获取AI模型详情
  getById(id: number): Promise<AIModel> {
    return request.get(`/ai-models/${id}`)
  },
  
  // 创建AI模型
  create(data: AIModelCreate): Promise<AIModel> {
    return request.post('/ai-models', data)
  },
  
  // 更新AI模型
  update(id: number, data: Partial<AIModelCreate>): Promise<AIModel> {
    return request.put(`/ai-models/${id}`, data)
  },
  
  // 删除AI模型
  delete(id: number): Promise<void> {
    return request.delete(`/ai-models/${id}`)
  },
  
  // 测试AI模型连接
  testConnection(data: { api_endpoint: string; api_key: string; model_type: string }): Promise<{ success: boolean; message: string }> {
    return request.post('/ai-models/test-connection', data)
  }
}

// 模型配置API别名
export const modelConfigApi = aiModelApi

// 存储凭证API
export const storageApi = {
  // 获取存储凭证列表
  getList(params?: { page?: number; size?: number; search?: string }): Promise<PaginatedResponse<StorageCredential>> {
    return request.get('/storage-credentials', params)
  },
  
  // 获取存储凭证详情
  getById(id: number): Promise<StorageCredential> {
    return request.get(`/storage-credentials/${id}`)
  },
  
  // 创建存储凭证
  create(data: StorageCredentialCreate): Promise<StorageCredential> {
    return request.post('/storage-credentials', data)
  },
  
  // 更新存储凭证
  update(id: number, data: Partial<StorageCredentialCreate>): Promise<StorageCredential> {
    return request.put(`/storage-credentials/${id}`, data)
  },
  
  // 删除存储凭证
  delete(id: number): Promise<void> {
    return request.delete(`/storage-credentials/${id}`)
  },
  
  // 测试存储连接
  testConnection(data: { server_address: string; protocol_type: string; username: string; password: string }): Promise<{ success: boolean; message: string }> {
    return request.post('/storage-credentials/test-connection', data)
  }
}

// 存储配置API别名
export const storageConfigApi = storageApi

// Webhook API
export const webhookApi = {
  // 获取Webhook列表
  getList(params?: { page?: number; size?: number; search?: string }): Promise<PaginatedResponse<Webhook>> {
    return request.get('/webhooks', params)
  },
  
  // 获取Webhook详情
  getById(id: number): Promise<Webhook> {
    return request.get(`/webhooks/${id}`)
  },
  
  // 创建Webhook
  create(data: WebhookCreate): Promise<Webhook> {
    return request.post('/webhooks', data)
  },
  
  // 更新Webhook
  update(id: number, data: Partial<WebhookCreate>): Promise<Webhook> {
    return request.put(`/webhooks/${id}`, data)
  },
  
  // 删除Webhook
  delete(id: number): Promise<void> {
    return request.delete(`/webhooks/${id}`)
  },
  
  // 获取Webhook请求日志
  getLogs(webhookId: number, params?: { page?: number; size?: number; start_date?: string; end_date?: string }): Promise<PaginatedResponse<any>> {
    return request.get(`/webhooks/${webhookId}/logs`, params)
  },
  
  // 重试Webhook
  retry(id: number): Promise<void> {
    return request.post(`/webhooks/logs/${id}/retry`)
  },
  
  // 清除Webhook日志
  clearLogs(webhookId: number): Promise<void> {
    return request.delete(`/webhooks/${webhookId}/logs`)
  },
  
  // 测试Webhook
  test(id: number): Promise<{ success: boolean; message: string }> {
    return request.post(`/webhooks/${id}/test`)
  },
  
  // 测试Webhook URL
  testUrl(data: { url: string; method: string; headers: Record<string, string>; timeout?: number }): Promise<{ success: boolean; message: string }> {
    return request.post('/webhooks/test-url', data)
  },
  
  // 测试Webhook连接
  testConnection(id: number): Promise<{ success: boolean; message: string }> {
    return request.post(`/webhooks/${id}/test-connection`)
  },
  
  // 获取Webhook统计信息
  getStats(params: { webhook_id: number; days?: number }): Promise<{ total: number; success: number; failed: number; pending: number }> {
    return request.get('/webhooks/stats', params)
  }
}

// 分析任务API
export const taskApi = {
  // 获取任务列表
  getList(params?: { page?: number; size?: number; search?: string; status?: string }): Promise<PaginatedResponse<AnalysisTask>> {
    return request.get('/tasks', params)
  },
  
  // 获取任务详情
  getById(id: number): Promise<AnalysisTask> {
    return request.get(`/tasks/${id}`)
  },
  
  // 创建任务
  create(data: AnalysisTaskCreate): Promise<AnalysisTask> {
    return request.post('/tasks', data)
  },
  
  // 更新任务
  update(id: number, data: Partial<AnalysisTaskCreate>): Promise<AnalysisTask> {
    return request.put(`/tasks/${id}`, data)
  },
  
  // 删除任务
  delete(id: number): Promise<void> {
    return request.delete(`/tasks/${id}`)
  },
  
  // 启用/禁用任务
  toggleStatus(id: number, isActive: boolean): Promise<AnalysisTask> {
    return request.patch(`/tasks/${id}/status`, { is_active: isActive })
  },
  
  // 手动执行任务
  execute(id: number, payload?: any): Promise<{ execution_id: number }> {
    return request.post(`/tasks/${id}/execute`, { payload })
  },
  
  // 测试JSONPath配置
  testJsonPath(data: { sample_data: any; extraction_config: any }): Promise<{ extracted_data: any }> {
    return request.post('/tasks/test-jsonpath', data)
  },
  
  // 获取任务统计信息
  getStats(params: { task_id: string; start_date?: string; end_date?: string }): Promise<any> {
    return request.get(`/tasks/${params.task_id}/stats`, { start_date: params.start_date, end_date: params.end_date })
  },
  
  // 获取任务执行记录
  getExecutions(params: { task_id: string; page?: number; size?: number }): Promise<PaginatedResponse<TaskExecution>> {
    return request.get(`/tasks/${params.task_id}/executions`, params)
  }
}

// 任务执行记录API
export const executionApi = {
  // 获取执行记录列表
  getList(params?: { 
    page?: number; 
    size?: number; 
    task_id?: number; 
    status?: string; 
    start_date?: string; 
    end_date?: string 
  }): Promise<PaginatedResponse<TaskExecution>> {
    return request.get('/executions', params)
  },
  
  // 获取执行记录详情
  getById(id: number): Promise<TaskExecution> {
    return request.get(`/executions/${id}`)
  },
  
  // 重新执行任务
  retry(id: number): Promise<{ execution_id: number }> {
    return request.post(`/executions/${id}/retry`)
  },
  
  // 取消执行
  cancel(id: number): Promise<void> {
    return request.post(`/executions/${id}/cancel`)
  },
  
  // 导出执行记录
  export(params?: any): Promise<Blob> {
    return request.get('/executions/export', params, { responseType: 'blob' })
  },
  
  // 下载执行结果
  downloadResult(id: number): Promise<Blob> {
    return request.get(`/executions/${id}/result`, {}, { responseType: 'blob' })
  },
  
  // 删除执行记录
  delete(id: number): Promise<void> {
    return request.delete(`/executions/${id}`)
  }
}

// 监控统计API
export const monitoringApi = {
  // 获取仪表板统计数据
  getDashboardStats(): Promise<DashboardStats> {
    return request.get('/monitoring/dashboard')
  },
  
  // 获取执行统计数据
  getExecutionStats(params?: { 
    start_date?: string; 
    end_date?: string; 
    task_id?: number 
  }): Promise<ExecutionStats[]> {
    return request.get('/monitoring/execution-stats', params)
  },
  
  // 获取Token使用统计
  getTokenStats(params?: { 
    start_date?: string; 
    end_date?: string; 
    model_id?: number 
  }): Promise<any[]> {
    return request.get('/monitoring/token-stats', params)
  },
  
  // 获取错误统计
  getErrorStats(params?: { 
    start_date?: string; 
    end_date?: string 
  }): Promise<any[]> {
    return request.get('/monitoring/error-stats', params)
  },
  
  // 获取概览统计
  getOverviewStats(params?: any): Promise<any> {
    return request.get('/analytics/overview', params)
  },
  
  // 获取执行趋势
  getExecutionTrend(params?: any): Promise<any> {
    return request.get('/analytics/execution-trend', params)
  },
  
  // 获取成功率趋势
  getSuccessRateTrend(params?: any): Promise<any> {
    return request.get('/analytics/success-rate-trend', params)
  },
  
  // 获取任务类型分布
  getTaskTypeDistribution(params?: any): Promise<any> {
    return request.get('/analytics/task-type-distribution', params)
  },
  
  // 获取Token趋势
  getTokenTrend(params?: any): Promise<any> {
    return request.get('/analytics/token-trend', params)
  },
  
  // 获取执行时长分布
  getDurationDistribution(params?: any): Promise<any> {
    return request.get('/analytics/duration-distribution', params)
  },
  
  // 获取文件类型分布
  getFileTypeDistribution(params?: any): Promise<any> {
    return request.get('/analytics/file-type-distribution', params)
  },
  
  // 获取任务统计
  getTaskStats(params?: any): Promise<any> {
    return request.get('/analytics/task-stats', params)
  },
  
  // 导出报告
  exportReport(params?: any): Promise<Blob> {
    return request.get('/analytics/export-report', params, { responseType: 'blob' })
  },
  
  // 导出任务统计
  exportTaskStats(params?: any): Promise<Blob> {
    return request.get('/analytics/export-task-stats', params, { responseType: 'blob' })
  }
}

// 分析统计API别名
export const analyticsApi = monitoringApi

// 系统配置API
export const systemApi = {
  // 获取系统信息
  getSystemInfo(): Promise<any> {
    return request.get('/system/info')
  },
  
  // 获取健康检查
  getHealthCheck(): Promise<{ status: string; checks: any }> {
    return request.get('/system/health')
  }
}