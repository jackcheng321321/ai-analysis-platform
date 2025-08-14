-- AI综合分析管理平台 - 数据库设计
-- PostgreSQL 15+

-- 创建数据库（如果需要）
-- CREATE DATABASE ai_analysis_platform;
-- \c ai_analysis_platform;

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 创建枚举类型
CREATE TYPE model_type_enum AS ENUM (
    'openai_compatible',
    'google_gemini', 
    'anthropic_claude',
    'local_model',
    'azure_openai',
    'moonshot',
    'zhipu',
    'baidu_qianfan'
);

CREATE TYPE protocol_type_enum AS ENUM (
    'smb',
    'nfs', 
    'ftp',
    'sftp',
    'webdav',
    'http',
    'https'
);

CREATE TYPE execution_status_enum AS ENUM (
    'pending',
    'processing',
    'success',
    'failed',
    'timeout',
    'cancelled'
);

-- ================================
-- 1. AI模型配置表
-- ================================
CREATE TABLE ai_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200),
    model_type model_type_enum NOT NULL,
    api_endpoint TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    api_version VARCHAR(20),
    default_params JSONB DEFAULT '{}',
    max_tokens INTEGER DEFAULT 4000,
    supports_multimodal BOOLEAN DEFAULT false,
    cost_per_1k_tokens DECIMAL(10,6) DEFAULT 0,
    rate_limit_rpm INTEGER DEFAULT 60,
    rate_limit_tpm INTEGER DEFAULT 60000,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_ai_models_type ON ai_models(model_type);
CREATE INDEX idx_ai_models_active ON ai_models(is_active);
CREATE INDEX idx_ai_models_created_at ON ai_models(created_at);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ai_models_updated_at BEFORE UPDATE
    ON ai_models FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- 2. 存储凭证配置表
-- ================================
CREATE TABLE storage_credentials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200),
    server_address TEXT NOT NULL,
    protocol_type protocol_type_enum NOT NULL,
    port INTEGER,
    username VARCHAR(100) NOT NULL,
    password_encrypted TEXT NOT NULL,
    additional_config JSONB DEFAULT '{}', -- 额外配置，如域名、工作组等
    connection_timeout INTEGER DEFAULT 30,
    read_timeout INTEGER DEFAULT 300,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_storage_credentials_protocol ON storage_credentials(protocol_type);
CREATE INDEX idx_storage_credentials_active ON storage_credentials(is_active);
CREATE INDEX idx_storage_credentials_created_at ON storage_credentials(created_at);

-- 创建更新时间触发器
CREATE TRIGGER update_storage_credentials_updated_at BEFORE UPDATE
    ON storage_credentials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- 3. Webhook配置表
-- ================================
CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    webhook_id VARCHAR(50) UNIQUE NOT NULL DEFAULT ('wh_' || encode(gen_random_bytes(16), 'hex')),
    description TEXT,
    secret_token VARCHAR(100), -- 用于验证请求签名
    allowed_ips TEXT[], -- 允许的IP地址列表
    rate_limit_per_minute INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE UNIQUE INDEX idx_webhooks_webhook_id ON webhooks(webhook_id);
CREATE INDEX idx_webhooks_active ON webhooks(is_active);
CREATE INDEX idx_webhooks_created_at ON webhooks(created_at);

-- 创建更新时间触发器
CREATE TRIGGER update_webhooks_updated_at BEFORE UPDATE
    ON webhooks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- 4. AI分析任务表
-- ================================
CREATE TABLE analysis_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    webhook_id INTEGER REFERENCES webhooks(id) ON DELETE SET NULL,
    ai_model_id INTEGER REFERENCES ai_models(id) ON DELETE RESTRICT,
    storage_credential_id INTEGER REFERENCES storage_credentials(id) ON DELETE SET NULL,
    
    -- 数据提取配置
    data_extraction_config JSONB NOT NULL DEFAULT '{}', -- JSONPath配置
    
    -- 文件获取配置
    file_url_variable VARCHAR(100), -- 从提取的数据中获取文件URL的变量名
    file_size_limit_mb INTEGER DEFAULT 100,
    supported_file_types TEXT[] DEFAULT ARRAY['txt', 'pdf', 'docx', 'xlsx', 'jpg', 'png', 'gif'],
    
    -- AI分析配置
    prompt_template TEXT NOT NULL,
    model_parameters JSONB DEFAULT '{}', -- 覆盖默认模型参数
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 60,
    
    -- 飞书集成配置
    feishu_config JSONB NOT NULL DEFAULT '{}', -- 飞书API配置
    field_mapping JSONB NOT NULL DEFAULT '{}', -- 字段映射配置
    
    -- 任务状态和统计
    is_active BOOLEAN DEFAULT true,
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    total_tokens_used BIGINT DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0,
    avg_execution_time_ms INTEGER DEFAULT 0,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_analysis_tasks_webhook ON analysis_tasks(webhook_id);
CREATE INDEX idx_analysis_tasks_model ON analysis_tasks(ai_model_id);
CREATE INDEX idx_analysis_tasks_active ON analysis_tasks(is_active);
CREATE INDEX idx_analysis_tasks_created_at ON analysis_tasks(created_at);
CREATE INDEX idx_analysis_tasks_last_executed ON analysis_tasks(last_executed_at);

-- 创建更新时间触发器
CREATE TRIGGER update_analysis_tasks_updated_at BEFORE UPDATE
    ON analysis_tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- 5. 任务执行记录表
-- ================================
CREATE TABLE task_executions (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES analysis_tasks(id) ON DELETE CASCADE,
    execution_id VARCHAR(50) UNIQUE NOT NULL DEFAULT ('exec_' || encode(gen_random_bytes(12), 'hex')),
    
    -- 输入数据
    webhook_payload JSONB,
    extracted_data JSONB,
    file_url TEXT,
    file_size_bytes BIGINT,
    file_type VARCHAR(20),
    file_content_preview TEXT, -- 文件内容预览（前1000字符）
    
    -- AI处理
    prompt_sent TEXT,
    ai_response TEXT,
    ai_response_metadata JSONB, -- AI响应的元数据
    tokens_used INTEGER,
    cost DECIMAL(10,6),
    
    -- 回写结果
    feishu_task_id VARCHAR(100),
    feishu_response JSONB,
    fields_updated JSONB,
    
    -- 执行状态
    execution_status execution_status_enum DEFAULT 'pending',
    error_message TEXT,
    error_code VARCHAR(50),
    retry_count INTEGER DEFAULT 0,
    
    -- 时间统计
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_fetched_at TIMESTAMP WITH TIME ZONE,
    ai_called_at TIMESTAMP WITH TIME ZONE,
    ai_responded_at TIMESTAMP WITH TIME ZONE,
    feishu_updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_task_executions_task_id ON task_executions(task_id);
CREATE INDEX idx_task_executions_status ON task_executions(execution_status);
CREATE INDEX idx_task_executions_started_at ON task_executions(started_at);
CREATE INDEX idx_task_executions_execution_id ON task_executions(execution_id);
CREATE INDEX idx_task_executions_feishu_task ON task_executions(feishu_task_id);

-- 按日期分区（可选，用于大量数据）
-- CREATE INDEX idx_task_executions_started_at_date ON task_executions(DATE(started_at));

-- ================================
-- 6. Webhook请求日志表
-- ================================
CREATE TABLE webhook_logs (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER REFERENCES webhooks(id) ON DELETE CASCADE,
    request_id VARCHAR(50) UNIQUE NOT NULL DEFAULT ('req_' || encode(gen_random_bytes(12), 'hex')),
    
    -- 请求信息
    source_ip INET,
    user_agent TEXT,
    request_headers JSONB,
    request_payload JSONB,
    request_size_bytes INTEGER,
    
    -- 响应信息
    response_status INTEGER,
    response_time_ms INTEGER,
    
    -- 处理结果
    is_valid BOOLEAN DEFAULT true,
    validation_errors TEXT[],
    task_execution_id INTEGER REFERENCES task_executions(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_webhook_logs_webhook_id ON webhook_logs(webhook_id);
CREATE INDEX idx_webhook_logs_created_at ON webhook_logs(created_at);
CREATE INDEX idx_webhook_logs_source_ip ON webhook_logs(source_ip);
CREATE INDEX idx_webhook_logs_request_id ON webhook_logs(request_id);

-- ================================
-- 7. 系统配置表
-- ================================
CREATE TABLE system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    created_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE UNIQUE INDEX idx_system_configs_key ON system_configs(config_key);

-- 创建更新时间触发器
CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE
    ON system_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- 8. 用户表（简化版，后续可扩展）
-- ================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- 创建更新时间触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================
-- 9. 创建视图
-- ================================

-- 任务执行统计视图
CREATE VIEW task_execution_stats AS
SELECT 
    t.id as task_id,
    t.name as task_name,
    COUNT(e.id) as total_executions,
    COUNT(CASE WHEN e.execution_status = 'success' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN e.execution_status = 'failed' THEN 1 END) as failed_executions,
    COALESCE(SUM(e.tokens_used), 0) as total_tokens,
    COALESCE(SUM(e.cost), 0) as total_cost,
    COALESCE(AVG(e.execution_time_ms), 0) as avg_execution_time,
    MAX(e.started_at) as last_execution_at
FROM analysis_tasks t
LEFT JOIN task_executions e ON t.id = e.task_id
GROUP BY t.id, t.name;

-- Webhook统计视图
CREATE VIEW webhook_stats AS
SELECT 
    w.id as webhook_id,
    w.name as webhook_name,
    w.webhook_id as webhook_url_id,
    COUNT(l.id) as total_requests,
    COUNT(CASE WHEN l.response_status = 200 THEN 1 END) as successful_requests,
    COUNT(CASE WHEN l.response_status != 200 THEN 1 END) as failed_requests,
    COALESCE(AVG(l.response_time_ms), 0) as avg_response_time,
    MAX(l.created_at) as last_request_at
FROM webhooks w
LEFT JOIN webhook_logs l ON w.id = l.webhook_id
GROUP BY w.id, w.name, w.webhook_id;

-- ================================
-- 10. 插入初始数据
-- ================================

-- 插入默认管理员用户
INSERT INTO users (username, email, password_hash, full_name, is_admin) VALUES 
('admin', 'admin@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJK9.K33m', '系统管理员', true);
-- 默认密码: admin123

-- 插入系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES 
('encryption_key', '"your-encryption-key-here"', '数据加密密钥'),
('webhook_base_url', '"https://your-domain.com/api/v1/webhooks"', 'Webhook基础URL'),
('max_file_size_mb', '100', '最大文件大小限制（MB）'),
('default_retry_count', '3', '默认重试次数'),
('token_cost_tracking', 'true', '是否启用Token成本跟踪');

-- 插入示例AI模型配置（需要手动更新API密钥）
INSERT INTO ai_models (name, display_name, model_type, api_endpoint, api_key_encrypted, default_params, description) VALUES 
('gpt-4o', 'GPT-4o', 'openai_compatible', 'https://api.openai.com/v1/chat/completions', 'ENCRYPTED_API_KEY_HERE', '{"temperature": 0.7, "max_tokens": 4000}', 'OpenAI GPT-4o模型'),
('moonshot-v1-8k', 'Moonshot Kimi', 'openai_compatible', 'https://api.moonshot.cn/v1/chat/completions', 'ENCRYPTED_API_KEY_HERE', '{"temperature": 0.3, "max_tokens": 8000}', 'Moonshot Kimi模型'),
('glm-4', '智谱GLM-4', 'zhipu', 'https://open.bigmodel.cn/api/paas/v4/chat/completions', 'ENCRYPTED_API_KEY_HERE', '{"temperature": 0.7, "max_tokens": 4000}', '智谱GLM-4模型');

-- 插入示例存储凭证（需要手动更新密码）
INSERT INTO storage_credentials (name, display_name, server_address, protocol_type, username, password_encrypted, description) VALUES 
('company_nas', '公司NAS服务器', 'smb://192.168.1.100/shared', 'smb', 'nas_user', 'ENCRYPTED_PASSWORD_HERE', '公司内部NAS存储'),
('ftp_server', 'FTP文件服务器', 'ftp://files.company.com', 'ftp', 'ftp_user', 'ENCRYPTED_PASSWORD_HERE', 'FTP文件服务器');

-- ================================
-- 11. 创建函数和存储过程
-- ================================

-- 清理过期日志的函数
CREATE OR REPLACE FUNCTION cleanup_old_logs(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 删除过期的webhook日志
    DELETE FROM webhook_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- 删除过期的任务执行记录（保留更长时间）
    DELETE FROM task_executions 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * (days_to_keep * 3)
    AND execution_status IN ('success', 'failed');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 更新任务统计的函数
CREATE OR REPLACE FUNCTION update_task_stats(task_id_param INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE analysis_tasks SET
        total_executions = (
            SELECT COUNT(*) FROM task_executions WHERE task_id = task_id_param
        ),
        successful_executions = (
            SELECT COUNT(*) FROM task_executions 
            WHERE task_id = task_id_param AND execution_status = 'success'
        ),
        failed_executions = (
            SELECT COUNT(*) FROM task_executions 
            WHERE task_id = task_id_param AND execution_status = 'failed'
        ),
        total_tokens_used = (
            SELECT COALESCE(SUM(tokens_used), 0) FROM task_executions 
            WHERE task_id = task_id_param AND execution_status = 'success'
        ),
        total_cost = (
            SELECT COALESCE(SUM(cost), 0) FROM task_executions 
            WHERE task_id = task_id_param AND execution_status = 'success'
        ),
        avg_execution_time_ms = (
            SELECT COALESCE(AVG(execution_time_ms), 0) FROM task_executions 
            WHERE task_id = task_id_param AND execution_status = 'success'
        ),
        last_executed_at = (
            SELECT MAX(started_at) FROM task_executions WHERE task_id = task_id_param
        )
    WHERE id = task_id_param;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器，自动更新任务统计
CREATE OR REPLACE FUNCTION trigger_update_task_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        PERFORM update_task_stats(NEW.task_id);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM update_task_stats(OLD.task_id);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_task_executions_stats
    AFTER INSERT OR UPDATE OR DELETE ON task_executions
    FOR EACH ROW EXECUTE FUNCTION trigger_update_task_stats();

-- ================================
-- 12. 权限设置
-- ================================

-- 创建应用用户角色
CREATE ROLE ai_analysis_app;
GRANT CONNECT ON DATABASE ai_analysis_platform TO ai_analysis_app;
GRANT USAGE ON SCHEMA public TO ai_analysis_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_analysis_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_analysis_app;

-- 创建只读用户角色
CREATE ROLE ai_analysis_readonly;
GRANT CONNECT ON DATABASE ai_analysis_platform TO ai_analysis_readonly;
GRANT USAGE ON SCHEMA public TO ai_analysis_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ai_analysis_readonly;

-- ================================
-- 13. 性能优化建议
-- ================================

-- 定期执行的维护命令（建议加入定时任务）
-- VACUUM ANALYZE; -- 更新统计信息
-- REINDEX DATABASE ai_analysis_platform; -- 重建索引
-- SELECT cleanup_old_logs(30); -- 清理30天前的日志

-- 监控查询（用于性能分析）
-- SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE tablename IN ('task_executions', 'webhook_logs');
-- SELECT * FROM pg_stat_user_tables WHERE relname IN ('task_executions', 'webhook_logs');

COMMIT;

-- 数据库设计完成
-- 总表数: 8个核心表 + 2个视图
-- 预计支持: 百万级任务执行记录，千万级Webhook请求日志
-- 扩展性: 支持水平分区、读写分离等优化方案