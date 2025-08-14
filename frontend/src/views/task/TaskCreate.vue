<template>
  <div class="task-create">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h1 class="page-title">{{ isEdit ? '编辑任务' : '创建任务' }}</h1>
      </div>
      <div class="header-actions">
        <el-button @click="resetForm">重置</el-button>
        <el-button 
          type="primary" 
          @click="submitForm" 
          :loading="submitLoading"
        >
          {{ isEdit ? '更新任务' : '创建任务' }}
        </el-button>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="page-container">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="task-form"
      >
        <!-- 基本信息 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="任务名称" prop="name">
                <el-input
                  v-model="form.name"
                  placeholder="请输入任务名称"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
            </el-col>

          </el-row>
          
          <el-form-item label="任务描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入任务描述"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-row :gutter="20">

            <el-col :xs="24" :sm="12">
              <el-form-item label="状态">
                <el-switch
                  v-model="form.is_active"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 配置信息 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><Setting /></el-icon>
              <span>配置信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="AI模型" prop="ai_model_id">
                <el-select
                  v-model="form.ai_model_id"
                  placeholder="请选择AI模型"
                  style="width: 100%"
                  filterable
                  @focus="loadModelConfigs"
                >
                  <el-option
                    v-for="model in modelConfigs"
                    :key="model.id"
                    :label="`${model.name} (${model.model_type})`"
                    :value="model.id"
                    :disabled="!model.is_active"
                  >
                    <div class="model-option">
                      <span class="model-name">{{ model.name }}</span>
                      <el-tag size="small" :type="model.is_active ? 'success' : 'danger'">
                        {{ model.is_active ? '可用' : '不可用' }}
                      </el-tag>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="存储凭证" prop="storage_credential_id">
                <el-select
                  v-model="form.storage_credential_id"
                  placeholder="请选择存储凭证"
                  style="width: 100%"
                  filterable
                  @focus="loadStorageConfigs"
                >
                  <el-option
                    v-for="storage in storageConfigs"
                    :key="storage.id"
                    :label="`${storage.name} (${storage.protocol_type})`"
                    :value="storage.id"
                    :disabled="!storage.is_active"
                  >
                    <div class="storage-option">
                      <span class="storage-name">{{ storage.name }}</span>
                      <el-tag size="small" :type="storage.is_active ? 'success' : 'danger'">
                        {{ storage.is_active ? '可用' : '不可用' }}
                      </el-tag>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="Webhook" prop="webhook_id">
                <el-select
                  v-model="form.webhook_id"
                  placeholder="请选择Webhook（可选）"
                  style="width: 100%"
                  filterable
                  clearable
                  @focus="loadWebhookConfigs"
                >
                  <el-option
                    v-for="webhook in webhookConfigs"
                    :key="webhook.id"
                    :label="webhook.name"
                    :value="webhook.id"
                    :disabled="!webhook.is_active"
                  >
                    <div class="webhook-option">
                      <span class="webhook-name">{{ webhook.name }}</span>
                      <el-tag size="small" :type="webhook.is_active ? 'success' : 'danger'">
                        {{ webhook.is_active ? '可用' : '不可用' }}
                      </el-tag>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="超时时间" prop="timeout">
                <el-input-number
                  v-model="form.timeout"
                  :min="30"
                  :max="3600"
                  :step="30"
                  style="width: 100%"
                  controls-position="right"
                />
                <div class="form-tip">单位：秒，范围：30-3600秒</div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 分析配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><DocumentCopy /></el-icon>
              <span>分析配置</span>
            </div>
          </template>
          
          <el-form-item label="文件路径" prop="file_path">
            <el-input
              v-model="form.file_path"
              placeholder="请输入文件路径或文件夹路径"
              maxlength="500"
            >
              <template #append>
                <el-button :icon="FolderOpened" @click="selectPath">选择</el-button>
              </template>
            </el-input>
            <div class="form-tip">
              支持单个文件或文件夹路径，文件夹将递归处理所有支持的文件类型
            </div>
          </el-form-item>
          
          <el-form-item label="文件类型过滤">
            <el-checkbox-group v-model="form.file_extensions">
              <el-checkbox label=".txt">文本文件</el-checkbox>
              <el-checkbox label=".md">Markdown</el-checkbox>
              <el-checkbox label=".doc">Word文档</el-checkbox>
              <el-checkbox label=".docx">Word文档</el-checkbox>
              <el-checkbox label=".pdf">PDF文档</el-checkbox>
              <el-checkbox label=".csv">CSV文件</el-checkbox>
              <el-checkbox label=".json">JSON文件</el-checkbox>
              <el-checkbox label=".xml">XML文件</el-checkbox>
            </el-checkbox-group>
            <div class="form-tip">
              不选择则处理所有支持的文件类型
            </div>
          </el-form-item>
          
          <el-form-item label="分析提示词" prop="analysis_prompt">
            <el-input
              v-model="form.analysis_prompt"
              type="textarea"
              :rows="6"
              placeholder="请输入分析提示词，描述你希望AI如何分析文件内容"
              maxlength="2000"
              show-word-limit
            />
            <div class="form-tip">
              提示词将指导AI如何分析文件内容，请尽可能详细和具体
            </div>
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="最大Token数">
                <el-input-number
                  v-model="form.max_tokens"
                  :min="100"
                  :max="32000"
                  :step="100"
                  style="width: 100%"
                  controls-position="right"
                />
                <div class="form-tip">AI响应的最大Token数量</div>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="温度参数">
                <el-slider
                  v-model="form.temperature"
                  :min="0"
                  :max="2"
                  :step="0.1"
                  show-input
                  :input-size="'small'"
                />
                <div class="form-tip">控制AI响应的随机性，0-2之间</div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 调度配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><Timer /></el-icon>
              <span>调度配置</span>
            </div>
          </template>
          
          <el-form-item label="调度类型">
            <el-radio-group v-model="form.schedule_type">
              <el-radio label="manual">手动执行</el-radio>
              <el-radio label="cron">定时执行</el-radio>
              <el-radio label="interval">间隔执行</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item 
            v-if="form.schedule_type === 'cron'" 
            label="Cron表达式" 
            prop="cron_expression"
          >
            <el-input
              v-model="form.cron_expression"
              placeholder="请输入Cron表达式，如：0 0 * * *"
            >
              <template #append>
                <el-button @click="showCronHelper">帮助</el-button>
              </template>
            </el-input>
            <div class="form-tip">
              Cron表达式格式：分 时 日 月 周，例如：0 0 * * * 表示每天0点执行
            </div>
          </el-form-item>
          
          <el-form-item 
            v-if="form.schedule_type === 'interval'" 
            label="执行间隔" 
            prop="interval_seconds"
          >
            <el-input-number
              v-model="form.interval_seconds"
              :min="60"
              :max="86400"
              :step="60"
              style="width: 200px"
              controls-position="right"
            />
            <span class="ml-10">秒</span>
            <div class="form-tip">执行间隔时间，范围：60秒-86400秒（1天）</div>
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="最大重试次数">
                <el-input-number
                  v-model="form.max_retries"
                  :min="0"
                  :max="10"
                  style="width: 100%"
                  controls-position="right"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="重试间隔">
                <el-input-number
                  v-model="form.retry_delay"
                  :min="1"
                  :max="300"
                  style="width: 100%"
                  controls-position="right"
                />
                <div class="form-tip">单位：秒</div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 高级配置 -->
        <el-card class="form-section" shadow="never">
          <template #header>
            <div class="section-header">
              <el-icon><Tools /></el-icon>
              <span>高级配置</span>
            </div>
          </template>
          
          <el-form-item label="元数据">
            <div class="metadata-editor">
              <div 
                v-for="(item, index) in form.metadata" 
                :key="index" 
                class="metadata-item"
              >
                <el-input
                  v-model="item.key"
                  placeholder="键"
                  style="width: 200px"
                />
                <el-input
                  v-model="item.value"
                  placeholder="值"
                  style="width: 300px; margin-left: 10px"
                />
                <el-button
                  type="danger"
                  :icon="Delete"
                  size="small"
                  style="margin-left: 10px"
                  @click="removeMetadata(index)"
                />
              </div>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                @click="addMetadata"
              >
                添加元数据
              </el-button>
            </div>
            <div class="form-tip">
              自定义元数据，用于存储任务相关的额外信息
            </div>
          </el-form-item>
          
          <el-form-item label="标签">
            <el-tag
              v-for="tag in form.tags"
              :key="tag"
              closable
              @close="removeTag(tag)"
              style="margin-right: 10px"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="tagInputVisible"
              ref="tagInputRef"
              v-model="tagInputValue"
              size="small"
              style="width: 100px"
              @keyup.enter="addTag"
              @blur="addTag"
            />
            <el-button
              v-else
              size="small"
              @click="showTagInput"
            >
              + 添加标签
            </el-button>
            <div class="form-tip">
              为任务添加标签，便于分类和搜索
            </div>
          </el-form-item>
        </el-card>
      </el-form>
    </div>

    <!-- Cron帮助对话框 -->
    <el-dialog
      v-model="cronHelperVisible"
      title="Cron表达式帮助"
      width="600px"
    >
      <div class="cron-helper">
        <h4>Cron表达式格式：</h4>
        <p><code>分 时 日 月 周</code></p>
        
        <h4>常用示例：</h4>
        <ul>
          <li><code>0 0 * * *</code> - 每天0点执行</li>
          <li><code>0 */2 * * *</code> - 每2小时执行一次</li>
          <li><code>0 9 * * 1-5</code> - 工作日上午9点执行</li>
          <li><code>0 0 1 * *</code> - 每月1号0点执行</li>
          <li><code>0 0 * * 0</code> - 每周日0点执行</li>
        </ul>
        
        <h4>字段说明：</h4>
        <ul>
          <li>分：0-59</li>
          <li>时：0-23</li>
          <li>日：1-31</li>
          <li>月：1-12</li>
          <li>周：0-7（0和7都表示周日）</li>
        </ul>
        
        <h4>特殊字符：</h4>
        <ul>
          <li><code>*</code> - 匹配任意值</li>
          <li><code>?</code> - 不指定值</li>
          <li><code>-</code> - 范围，如1-5</li>
          <li><code>,</code> - 列举，如1,3,5</li>
          <li><code>/</code> - 步长，如*/2</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import {
  ArrowLeft,
  InfoFilled,
  Setting,
  DocumentCopy,
  Timer,
  Tools,
  FolderOpened,
  Delete,
  Plus
} from '@element-plus/icons-vue'
import { taskApi, modelConfigApi, storageConfigApi, webhookApi } from '@/api'
import type { AnalysisTask, AnalysisTaskCreate, AIModel, StorageCredential, Webhook } from '@/types/api'

const route = useRoute()
const router = useRouter()

// 响应式数据
const formRef = ref<FormInstance>()
const submitLoading = ref(false)
const cronHelperVisible = ref(false)
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const tagInputRef = ref()

// 配置选项
const modelConfigs = ref<AIModel[]>([])
const storageConfigs = ref<StorageCredential[]>([])
const webhookConfigs = ref<Webhook[]>([])

// 计算属性
const isEdit = computed(() => !!route.params.id)
const taskId = computed(() => route.params.id as string)

// 表单数据
const form = reactive<AnalysisTaskCreate & {
  file_extensions: string[]
  metadata: { key: string; value: string }[]
  tags: string[]
  max_retries?: number
  retry_delay?: number
  schedule_type?: string
  temperature?: number
  interval_seconds?: number
  timeout?: number
  file_path?: string
  max_tokens?: number
}>({
  name: '',
  description: '',
  is_active: true,
  ai_model_id: 0,
  storage_credential_id: 0,
  webhook_id: 0,
  file_extensions: [],
  analysis_prompt: '',
  is_scheduled: false,
  cron_expression: '',
  data_extraction_config: {},
  prompt_template: '',
  feishu_config: {},
  field_mapping: {},
  metadata: [],
  tags: [],
  max_retries: 3,
  retry_delay: 60,
  schedule_type: 'cron',
  temperature: 0.7,
  interval_seconds: 3600,
  timeout: 300,
  file_path: '',
  max_tokens: 4000
})

// 表单验证规则
const rules = {
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
  analysis_prompt: [
    { required: true, message: '请输入分析提示词', trigger: 'blur' },
    { min: 10, max: 2000, message: '长度在 10 到 2000 个字符', trigger: 'blur' }
  ],
  cron_expression: [
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (form.is_scheduled && !value) {
          callback(new Error('请输入Cron表达式'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  interval_seconds: [
    {
      validator: (rule: any, value: number, callback: Function) => {
        if (form.schedule_type === 'interval' && (!value || value < 60)) {
          callback(new Error('执行间隔不能少于60秒'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 方法
const loadModelConfigs = async () => {
  if (modelConfigs.value.length > 0) return
  
  try {
    const response = await modelConfigApi.getList({ page: 1, size: 100 })
    modelConfigs.value = response.items
  } catch (error) {
    console.error('加载AI模型配置失败:', error)
  }
}

const loadStorageConfigs = async () => {
  if (storageConfigs.value.length > 0) return
  
  try {
    const response = await storageConfigApi.getList({ page: 1, size: 100 })
    storageConfigs.value = response.items
  } catch (error) {
    console.error('加载存储配置失败:', error)
  }
}

const loadWebhookConfigs = async () => {
  if (webhookConfigs.value.length > 0) return
  
  try {
    const response = await webhookApi.getList({ page: 1, size: 100 })
    webhookConfigs.value = response.items
  } catch (error) {
    console.error('加载Webhook配置失败:', error)
  }
}

const loadTaskData = async () => {
  if (!isEdit.value) return
  
  try {
    const task = await taskApi.getById(parseInt(taskId.value))
    
    // 填充表单数据
    Object.assign(form, {
      ...task,
      file_extensions: [],
      metadata: [],
      tags: []
    })
  } catch (error) {
    console.error('加载任务数据失败:', error)
    ElMessage.error('加载任务数据失败')
  }
}

const selectPath = () => {
  // 这里可以集成文件选择器
  ElMessage.info('文件选择器功能待实现')
}

const addMetadata = () => {
  form.metadata.push({ key: '', value: '' })
}

const removeMetadata = (index: number) => {
  form.metadata.splice(index, 1)
}

const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

const addTag = () => {
  const tag = tagInputValue.value.trim()
  if (tag && !form.tags.includes(tag)) {
    form.tags.push(tag)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

const removeTag = (tag: string) => {
  const index = form.tags.indexOf(tag)
  if (index > -1) {
    form.tags.splice(index, 1)
  }
}

const showCronHelper = () => {
  cronHelperVisible.value = true
}

const resetForm = () => {
  formRef.value?.resetFields()
  form.metadata = []
  form.tags = []
  form.file_extensions = []
}

const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitLoading.value = true
    
    // 准备提交数据
    const submitData = {
      ...form,
      metadata: form.metadata.reduce((acc: Record<string, any>, item: any) => {
        if (item.key && item.value) {
          acc[item.key] = item.value
        }
        return acc
      }, {} as Record<string, any>),
      file_extensions: form.file_extensions.length > 0 ? form.file_extensions : undefined
    }
    
    if (isEdit.value) {
      await taskApi.update(parseInt(taskId.value), submitData)
      ElMessage.success('任务更新成功')
    } else {
      await taskApi.create(submitData)
      ElMessage.success('任务创建成功')
    }
    
    router.push({ name: 'TaskList' })
  } catch (error) {
    console.error('提交任务失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const goBack = () => {
  router.push({ name: 'TaskList' })
}

// 生命周期
onMounted(() => {
  loadModelConfigs()
  loadStorageConfigs()
  loadWebhookConfigs()
  loadTaskData()
})
</script>

<style scoped>
.task-create {
  padding: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-form {
  max-width: 1200px;
}

.form-section {
  margin-bottom: 20px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.model-option,
.storage-option,
.webhook-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.metadata-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.metadata-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.metadata-item:last-child {
  margin-bottom: 0;
}

.cron-helper h4 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.cron-helper h4:first-child {
  margin-top: 0;
}

.cron-helper p {
  margin: 5px 0;
}

.cron-helper ul {
  margin: 10px 0;
  padding-left: 20px;
}

.cron-helper li {
  margin: 5px 0;
}

.cron-helper code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

@media (max-width: 768px) {
  .task-form {
    max-width: 100%;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .metadata-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .metadata-item .el-input {
    width: 100% !important;
    margin-left: 0 !important;
  }
}
</style>