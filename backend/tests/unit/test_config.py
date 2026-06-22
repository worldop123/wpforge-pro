"""
配置模块测试
"""
import pytest

from app.core.config import Settings


def test_settings_creation():
    """测试设置对象创建"""
    settings = Settings()
    assert settings is not None


def test_settings_default_values():
    """测试默认配置值"""
    settings = Settings()

    # 检查默认值
    assert settings.PROJECT_NAME == "WPForge"
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "INFO"


def test_settings_database_url():
    """测试数据库URL配置"""
    settings = Settings()

    # 数据库URL应该被正确解析
    assert settings.DATABASE_URL is not None
    assert isinstance(settings.DATABASE_URL, str)


def test_settings_redis_url():
    """测试Redis URL配置"""
    settings = Settings()

    # Redis URL应该被正确解析
    assert settings.REDIS_URL is not None
    assert isinstance(settings.REDIS_URL, str)


def test_settings_jwt_config():
    """测试JWT配置"""
    settings = Settings()

    assert settings.JWT_SECRET is not None
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7


def test_settings_ai_config():
    """测试AI配置"""
    settings = Settings()

    assert settings.AI_PROVIDER is not None
    assert isinstance(settings.AI_PROVIDER, str)


def test_settings_proxy_config():
    """测试代理配置"""
    settings = Settings()

    assert settings.PROXY_ENABLED == False
    assert settings.PROXY_PROVIDER is not None


def test_settings_scraping_config():
    """测试采集配置"""
    settings = Settings()

    assert settings.SCRAPING_CONCURRENCY > 0
    assert settings.SCRAPING_DELAY_MIN > 0
    assert settings.SCRAPING_DELAY_MAX >= settings.SCRAPING_DELAY_MIN
    assert settings.SCRAPING_TIMEOUT > 0
    assert settings.SCRAPING_RETRY_TIMES >= 0
