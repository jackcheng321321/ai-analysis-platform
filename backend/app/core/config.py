from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
import secrets
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "AI综合分析管理平台"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)[:32]  # 32字符用于AES加密
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 数据库配置
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ai_analysis_platform"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=str(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None
    
    @validator("REDIS_URL", pre=True)
    def assemble_redis_connection(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        
        password = values.get("REDIS_PASSWORD")
        auth_part = f":{password}@" if password else ""
        
        return f"redis://{auth_part}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    # Celery配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @validator("CELERY_BROKER_URL", pre=True)
    def assemble_celery_broker(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return values.get("REDIS_URL", "redis://localhost:6379/0")
    
    @validator("CELERY_RESULT_BACKEND", pre=True)
    def assemble_celery_backend(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        return values.get("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT配置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    ALGORITHM: str = "HS256"
    
    # 文件处理配置
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [
        ".txt", ".md", ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mp3", ".wav"
    ]
    TEMP_DIR: str = "/tmp/ai_analysis"
    
    # Webhook配置
    WEBHOOK_BASE_URL: str = "http://localhost:8000/api/v1/webhooks"
    WEBHOOK_SECRET_LENGTH: int = 32
    WEBHOOK_TIMEOUT: int = 30
    
    # AI模型配置
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"
    AI_REQUEST_TIMEOUT: int = 120
    MAX_TOKENS_PER_REQUEST: int = 4000
    
    # 飞书配置
    FEISHU_APP_ID: Optional[str] = None
    FEISHU_APP_SECRET: Optional[str] = None
    FEISHU_BASE_URL: str = "https://open.feishu.cn/open-apis"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # 安全配置
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_TIMEOUT: int = 300  # 5分钟
    
    # 任务配置
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: int = 60  # 秒
    TASK_TIMEOUT: int = 3600  # 1小时
    
    # 邮件配置（可选）
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 开发配置
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return str(self.DATABASE_URL)
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        return str(self.REDIS_URL)
    
    def is_development(self) -> bool:
        """判断是否为开发环境"""
        return self.DEBUG or self.RELOAD
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS允许的源"""
        if self.is_development():
            return ["http://localhost:3000", "http://127.0.0.1:3000"]
        return [str(origin) for origin in self.BACKEND_CORS_ORIGINS]
    
    def get_log_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT,
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.LOG_LEVEL,
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {
                    "level": self.LOG_LEVEL,
                    "handlers": ["console"],
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "sqlalchemy.engine": {
                    "level": "WARNING" if not self.is_development() else "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
        
        # 如果指定了日志文件，添加文件处理器
        if self.LOG_FILE:
            config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": self.LOG_LEVEL,
                "formatter": "detailed",
                "filename": self.LOG_FILE,
                "maxBytes": self.LOG_MAX_SIZE,
                "backupCount": self.LOG_BACKUP_COUNT,
            }
            # 为所有logger添加文件处理器
            for logger_name in config["loggers"]:
                config["loggers"][logger_name]["handlers"].append("file")
        
        return config


# 创建全局设置实例
settings = Settings()

# 确保临时目录存在
Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)