"""
WPForge - WordPress全自动AI仿站原创软件
核心配置模块
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "WPForge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+psycopg2://wpforge:wpforge@localhost:5432/wpforge"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_BROKER_DB: int = 1
    REDIS_BACKEND_DB: int = 2
    
    # Celery配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # JWT配置
    SECRET_KEY: str = "wpforge-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # AI模型配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # 默认AI模型
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-4o-mini"
    
    # Playwright配置
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_SLOW_MO: int = 100
    PLAYWRIGHT_TIMEOUT: int = 30000
    PLAYWRIGHT_USER_DATA_DIR: Optional[str] = None
    
    # 反检测配置
    STEALTH_ENABLED: bool = True
    RANDOM_DELAY_MIN: float = 1.0
    RANDOM_DELAY_MAX: float = 3.0
    HUMAN_LIKE_SCROLL: bool = True
    
    # 采集配置
    MAX_CONCURRENT_SCRAPERS: int = 3
    SCRAPER_DELAY_BETWEEN_REQUESTS: float = 2.0
    MAX_RETRIES: int = 3
    
    # 翻译配置
    DEFAULT_SOURCE_LANG: str = "auto"
    DEFAULT_TARGET_LANG: str = "zh-CN"
    TRANSLATION_BATCH_SIZE: int = 50
    
    # 汇率配置
    EXCHANGE_RATE_API_KEY: Optional[str] = None
    EXCHANGE_RATE_CACHE_TTL: int = 3600  # 1小时
    DEFAULT_CURRENCY: str = "USD"
    TARGET_CURRENCY: str = "CNY"
    
    # WordPress配置
    WP_DEFAULT_USER: str = "admin"
    WP_DEFAULT_PASSWORD: str = "admin"
    
    # 安全配置
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION: int = 300  # 5分钟
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 插件目录
    PLUGINS_DIR: str = "plugins"
    
    # 上传目录
    UPLOAD_DIR: str = "uploads"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
