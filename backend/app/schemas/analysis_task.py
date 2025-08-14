"""分析任务相关Pydantic模式

定义分析任务的创建、更新、响应等数据验证模式。
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class TriggerType(str, Enum):
    """触发类型枚举"""
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    API = "api"
    FILE_WATCH = "file_watch"


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AnalysisTaskBase(BaseModel):
    """分析任务基础模式"""
    
    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    description: Optional[str] = Field(None, max_length=500, description="任务描述")
    trigger_type: TriggerType = Field(..., description="触发类型")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    
    # 触发配置
    trigger_config: Dict[str, Any] = Field({}, description="触发配置")
    
    # 数据解析配置
    data_parsing_config: Dict[str, Any] = Field({}, description="数据解析配置")
    
    # 文件获取配置
    file_acquisition_config: Optional[Dict[str, Any]] = Field(None, description="文件获取配置")
    
    # AI分析配置
    ai_analysis_config: Dict[str, Any] = Field({}, description="AI分析配置")
    
    # 结果写入配置
    result_writing_config: Dict[str, Any] = Field({}, description="结果写入配置")
    
    # 飞书集成配置
    feishu_config: Optional[Dict[str, Any]] = Field(None, description="飞书配置")
    
    # 执行参数
    timeout: int = Field(300, ge=30, le=3600, description="超时时间（秒）")
    max_retries: int = Field(3, ge=0, le=10, description="最大重试次数")
    retry_delay: int = Field(60, ge=1, le=3600, description="重试延迟（秒）")
    max_concurrency: int = Field(1, ge=1, le=10, description="最大并发数")
    
    # 资源限制
    max_memory_mb: Optional[int] = Field(None, ge=128, le=8192, description="最大内存（MB）")
    max_cpu_percent: Optional[int] = Field(None, ge=10, le=100, description="最大CPU使用率（%）")
    max_execution_time: Optional[int] = Field(None, ge=60, le=7200, description="最大执行时间（秒）")
    
    # 通知设置
    notify_on_success: bool = Field(False, description="成功时通知")
    notify_on_failure: bool = Field(True, description="失败时通知")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="通知配置")
    
    # 日志设置
    log_level: str = Field("INFO", description="日志级别")
    log_retention_days: int = Field(30, ge=1, le=365, description="日志保留天数")
    enable_detailed_logging: bool = Field(True, description="启用详细日志")
    
    # 其他设置
    tags: Optional[List[str]] = Field(None, description="标签")
    category: Optional[str] = Field(None, description="分类")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('任务名称不能为空')
        return v.strip()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'日志级别必须是以下之一: {", ".join(allowed_levels)}')
        return v.upper()
    
    @validator('trigger_config')
    def validate_trigger_config(cls, v, values):
        trigger_type = values.get('trigger_type')
        if trigger_type == TriggerType.WEBHOOK:
            if 'webhook_id' not in v:
                raise ValueError('Webhook触发需要指定webhook_id')
        elif trigger_type == TriggerType.SCHEDULE:
            if 'cron_expression' not in v and 'interval_seconds' not in v:
                raise ValueError('定时触发需要指定cron_expression或interval_seconds')
        return v
    
    @validator('ai_analysis_config')
    def validate_ai_analysis_config(cls, v):
        if 'ai_model_id' not in v:
            raise ValueError('AI分析配置需要指定ai_model_id')
        if 'prompt_template' not in v:
            raise ValueError('AI分析配置需要指定prompt_template')
        return v


class AnalysisTaskCreate(AnalysisTaskBase):
    """分析任务创建模式"""
    
    status: TaskStatus = Field(TaskStatus.DRAFT, description="任务状态")
    is_shared: bool = Field(False, description="是否共享")
    shared_users: Optional[List[int]] = Field(None, description="共享用户ID列表")
    
    # 版本控制
    version_notes: Optional[str] = Field(None, max_length=500, description="版本说明")


class AnalysisTaskUpdate(BaseModel):
    """分析任务更新模式"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="任务名称")
    description: Optional[str] = Field(None, max_length=500, description="任务描述")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    priority: Optional[TaskPriority] = Field(None, description="任务优先级")
    
    # 触发配置
    trigger_config: Optional[Dict[str, Any]] = Field(None, description="触发配置")
    
    # 数据解析配置
    data_parsing_config: Optional[Dict[str, Any]] = Field(None, description="数据解析配置")
    
    # 文件获取配置
    file_acquisition_config: Optional[Dict[str, Any]] = Field(None, description="文件获取配置")
    
    # AI分析配置
    ai_analysis_config: Optional[Dict[str, Any]] = Field(None, description="AI分析配置")
    
    # 结果写入配置
    result_writing_config: Optional[Dict[str, Any]] = Field(None, description="结果写入配置")
    
    # 飞书集成配置
    feishu_config: Optional[Dict[str, Any]] = Field(None, description="飞书配置")
    
    # 执行参数
    timeout: Optional[int] = Field(None, ge=30, le=3600, description="超时时间（秒）")
    max_retries: Optional[int] = Field(None, ge=0, le=10, description="最大重试次数")
    retry_delay: Optional[int] = Field(None, ge=1, le=3600, description="重试延迟（秒）")
    max_concurrency: Optional[int] = Field(None, ge=1, le=10, description="最大并发数")
    
    # 资源限制
    max_memory_mb: Optional[int] = Field(None, ge=128, le=8192, description="最大内存（MB）")
    max_cpu_percent: Optional[int] = Field(None, ge=10, le=100, description="最大CPU使用率（%）")
    max_execution_time: Optional[int] = Field(None, ge=60, le=7200, description="最大执行时间（秒）")
    
    # 通知设置
    notify_on_success: Optional[bool] = Field(None, description="成功时通知")
    notify_on_failure: Optional[bool] = Field(None, description="失败时通知")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="通知配置")
    
    # 日志设置
    log_level: Optional[str] = Field(None, description="日志级别")
    log_retention_days: Optional[int] = Field(None, ge=1, le=365, description="日志保留天数")
    enable_detailed_logging: Optional[bool] = Field(None, description="启用详细日志")
    
    # 共享设置
    is_shared: Optional[bool] = Field(None, description="是否共享")
    shared_users: Optional[List[int]] = Field(None, description="共享用户ID列表")
    
    # 其他设置
    tags: Optional[List[str]] = Field(None, description="标签")
    category: Optional[str] = Field(None, description="分类")
    notes: Optional[str] = Field(None, max_length=1000, description="备注")
    
    # 版本控制
    version_notes: Optional[str] = Field(None, max_length=500, description="版本说明")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('任务名称不能为空')
        return v.strip() if v else v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        if v is not None:
            allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if v.upper() not in allowed_levels:
                raise ValueError(f'日志级别必须是以下之一: {", ".join(allowed_levels)}')
            return v.upper()
        return v


class AnalysisTaskResponse(AnalysisTaskBase):
    """分析任务响应模式"""
    
    id: int = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    creator_id: int = Field(..., description="创建者ID")
    is_shared: bool = Field(..., description="是否共享")
    shared_users: Optional[List[int]] = Field(None, description="共享用户ID列表")
    
    # 版本信息
    version: int = Field(..., description="版本号")
    version_notes: Optional[str] = Field(None, description="版本说明")
    
    # 统计信息
    total_executions: int = Field(0, description="总执行次数")
    successful_executions: int = Field(0, description="成功执行次数")
    failed_executions: int = Field(0, description="失败执行次数")
    average_execution_time: Optional[float] = Field(None, description="平均执行时间（秒）")
    total_tokens_used: int = Field(0, description="使用令牌总数")
    total_cost: float = Field(0.0, description="总成本")
    last_execution_at: Optional[datetime] = Field(None, description="最后执行时间")
    last_success_at: Optional[datetime] = Field(None, description="最后成功时间")
    last_failure_at: Optional[datetime] = Field(None, description="最后失败时间")
    
    # 健康状态
    health_status: Optional[str] = Field(None, description="健康状态")
    last_health_check_at: Optional[datetime] = Field(None, description="最后健康检查时间")
    health_check_error: Optional[str] = Field(None, description="健康检查错误")
    
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskTest(BaseModel):
    """分析任务测试模式"""
    
    test_data: Dict[str, Any] = Field({}, description="测试数据")
    dry_run: bool = Field(True, description="试运行模式")
    skip_file_acquisition: bool = Field(False, description="跳过文件获取")
    skip_result_writing: bool = Field(True, description="跳过结果写入")
    
    @validator('test_data')
    def validate_test_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('测试数据必须是字典格式')
        return v


class AnalysisTaskTestResponse(BaseModel):
    """分析任务测试响应模式"""
    
    success: bool = Field(..., description="是否成功")
    execution_id: Optional[str] = Field(None, description="执行ID")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="解析数据")
    ai_analysis_result: Optional[Dict[str, Any]] = Field(None, description="AI分析结果")
    tokens_used: Optional[int] = Field(None, description="使用令牌数")
    cost: Optional[float] = Field(None, description="成本")
    error_message: Optional[str] = Field(None, description="错误信息")
    logs: Optional[List[str]] = Field(None, description="日志")
    tested_at: datetime = Field(..., description="测试时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskHealthCheck(BaseModel):
    """分析任务健康检查模式"""
    
    task_id: int = Field(..., description="任务ID")
    status: str = Field(..., description="状态")
    dependencies_status: Dict[str, str] = Field({}, description="依赖状态")
    configuration_valid: bool = Field(..., description="配置是否有效")
    error_message: Optional[str] = Field(None, description="错误信息")
    checked_at: datetime = Field(..., description="检查时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskUsage(BaseModel):
    """分析任务使用情况模式"""
    
    task_id: int = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    executions_count: int = Field(0, description="执行次数")
    successful_executions: int = Field(0, description="成功执行次数")
    failed_executions: int = Field(0, description="失败执行次数")
    success_rate: float = Field(0.0, description="成功率")
    average_execution_time: Optional[float] = Field(None, description="平均执行时间")
    total_tokens_used: int = Field(0, description="使用令牌总数")
    total_cost: float = Field(0.0, description="总成本")
    last_execution_at: Optional[datetime] = Field(None, description="最后执行时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskStats(BaseModel):
    """分析任务统计模式"""
    
    total_tasks: int = Field(0, description="总任务数")
    active_tasks: int = Field(0, description="活跃任务数")
    total_executions: int = Field(0, description="总执行次数")
    successful_executions: int = Field(0, description="成功执行次数")
    failed_executions: int = Field(0, description="失败执行次数")
    average_success_rate: float = Field(0.0, description="平均成功率")
    total_tokens_used: int = Field(0, description="使用令牌总数")
    total_cost: float = Field(0.0, description="总成本")
    average_execution_time: Optional[float] = Field(None, description="平均执行时间")
    most_active_task: Optional[str] = Field(None, description="最活跃任务")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskVersion(BaseModel):
    """分析任务版本模式"""
    
    id: int = Field(..., description="版本ID")
    task_id: int = Field(..., description="任务ID")
    version: int = Field(..., description="版本号")
    version_notes: Optional[str] = Field(None, description="版本说明")
    config_snapshot: Dict[str, Any] = Field(..., description="配置快照")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskClone(BaseModel):
    """分析任务克隆模式"""
    
    new_name: str = Field(..., min_length=1, max_length=100, description="新任务名称")
    clone_executions: bool = Field(False, description="克隆执行记录")
    clone_logs: bool = Field(False, description="克隆日志")
    reset_statistics: bool = Field(True, description="重置统计信息")
    
    @validator('new_name')
    def validate_new_name(cls, v):
        if not v.strip():
            raise ValueError('新任务名称不能为空')
        return v.strip()


class AnalysisTaskBatchOperation(BaseModel):
    """分析任务批量操作模式"""
    
    task_ids: List[int] = Field(..., min_items=1, description="任务ID列表")
    operation: str = Field(..., description="操作类型")
    parameters: Dict[str, Any] = Field({}, description="操作参数")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = [
            'activate', 'deactivate', 'pause', 'archive', 'delete',
            'test', 'health_check', 'update_config', 'clone'
        ]
        if v not in allowed_operations:
            raise ValueError(f'操作类型必须是以下之一: {", ".join(allowed_operations)}')
        return v


class AnalysisTaskBatchOperationResponse(BaseModel):
    """分析任务批量操作响应模式"""
    
    operation: str = Field(..., description="操作类型")
    total_processed: int = Field(..., description="处理总数")
    successful_operations: int = Field(..., description="成功操作数")
    failed_operations: int = Field(..., description="失败操作数")
    results: List[Dict[str, Any]] = Field(..., description="结果列表")
    executed_at: datetime = Field(..., description="执行时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskMetrics(BaseModel):
    """分析任务指标模式"""
    
    task_id: int = Field(..., description="任务ID")
    date: datetime = Field(..., description="日期")
    executions_count: int = Field(0, description="执行次数")
    successful_executions: int = Field(0, description="成功执行次数")
    failed_executions: int = Field(0, description="失败执行次数")
    average_execution_time: float = Field(0.0, description="平均执行时间")
    total_tokens_used: int = Field(0, description="使用令牌总数")
    total_cost: float = Field(0.0, description="总成本")
    success_rate: float = Field(0.0, description="成功率")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskFilter(BaseModel):
    """分析任务过滤器模式"""
    
    name: Optional[str] = Field(None, description="名称过滤")
    status: Optional[TaskStatus] = Field(None, description="状态过滤")
    trigger_type: Optional[TriggerType] = Field(None, description="触发类型过滤")
    priority: Optional[TaskPriority] = Field(None, description="优先级过滤")
    creator_id: Optional[int] = Field(None, description="创建者ID过滤")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    category: Optional[str] = Field(None, description="分类过滤")
    is_shared: Optional[bool] = Field(None, description="共享状态过滤")
    created_after: Optional[datetime] = Field(None, description="创建时间之后")
    created_before: Optional[datetime] = Field(None, description="创建时间之前")
    last_execution_after: Optional[datetime] = Field(None, description="最后执行时间之后")
    last_execution_before: Optional[datetime] = Field(None, description="最后执行时间之前")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisTaskSort(BaseModel):
    """分析任务排序模式"""
    
    field: str = Field("created_at", description="排序字段")
    order: str = Field("desc", description="排序顺序")
    
    @validator('field')
    def validate_field(cls, v):
        allowed_fields = [
            'id', 'name', 'status', 'priority', 'created_at', 'updated_at',
            'last_execution_at', 'total_executions', 'successful_executions',
            'failed_executions', 'success_rate', 'average_execution_time',
            'total_cost', 'total_tokens_used'
        ]
        if v not in allowed_fields:
            raise ValueError(f'排序字段必须是以下之一: {", ".join(allowed_fields)}')
        return v
    
    @validator('order')
    def validate_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('排序顺序必须是asc或desc')
        return v.lower()