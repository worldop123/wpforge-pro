"""
配置模块测试

对应 app/core/config.py 中 Settings 类的实际字段。
"""
import pytest

from app.core.config import Settings, get_settings, settings


def test_settings_creation():
    """测试设置对象创建"""
    settings = Settings()
    assert settings is not None


def test_settings_default_values():
    """测试默认配置值"""
    settings = Settings()

    assert settings.APP_NAME == "WPForge"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.ENVIRONMENT == "production"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000


def test_settings_database_url():
    """测试数据库URL配置"""
    settings = Settings()

    assert settings.DATABASE_URL is not None
    assert isinstance(settings.DATABASE_URL, str)
    assert "://" in settings.DATABASE_URL


def test_settings_redis_url():
    """测试Redis URL配置"""
    settings = Settings()

    assert settings.REDIS_URL is not None
    assert isinstance(settings.REDIS_URL, str)
    assert settings.REDIS_BROKER_DB == 1
    assert settings.REDIS_BACKEND_DB == 2


def test_settings_jwt_config():
    """测试JWT配置"""
    settings = Settings()

    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_settings_ai_config():
    """测试AI配置"""
    settings = Settings()

    assert settings.DEFAULT_AI_PROVIDER is not None
    assert isinstance(settings.DEFAULT_AI_PROVIDER, str)
    assert settings.DEFAULT_AI_MODEL is not None
    assert settings.OPENAI_BASE_URL.startswith("http")


def test_settings_playwright_config():
    """测试Playwright配置"""
    settings = Settings()

    assert isinstance(settings.PLAYWRIGHT_HEADLESS, bool)
    assert settings.PLAYWRIGHT_TIMEOUT > 0
    assert settings.PLAYWRIGHT_SLOW_MO >= 0


def test_settings_stealth_config():
    """测试反检测配置"""
    settings = Settings()

    assert isinstance(settings.STEALTH_ENABLED, bool)
    assert settings.RANDOM_DELAY_MIN > 0
    assert settings.RANDOM_DELAY_MAX >= settings.RANDOM_DELAY_MIN


def test_settings_scraping_config():
    """测试采集配置"""
    settings = Settings()

    assert settings.MAX_CONCURRENT_SCRAPERS > 0
    assert settings.SCRAPER_DELAY_BETWEEN_REQUESTS > 0
    assert settings.MAX_RETRIES >= 0


def test_settings_translation_config():
    """测试翻译配置"""
    settings = Settings()

    assert settings.DEFAULT_SOURCE_LANG is not None
    assert settings.DEFAULT_TARGET_LANG is not None
    assert settings.TRANSLATION_BATCH_SIZE > 0


def test_settings_exchange_rate_config():
    """测试汇率配置"""
    settings = Settings()

    assert settings.EXCHANGE_RATE_CACHE_TTL > 0
    assert settings.DEFAULT_CURRENCY is not None
    assert settings.TARGET_CURRENCY is not None


def test_settings_security_config():
    """测试安全配置"""
    settings = Settings()

    assert settings.MAX_LOGIN_ATTEMPTS > 0
    assert settings.LOGIN_LOCKOUT_DURATION > 0
    assert settings.RATE_LIMIT_PER_MINUTE > 0


def test_settings_cors_config():
    """测试CORS配置"""
    settings = Settings()

    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) >= 1


def test_get_settings_singleton():
    """测试配置单例"""
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_global_settings_instance():
    """测试全局配置实例"""
    assert settings is not None
    assert isinstance(settings, Settings)
    assert settings.APP_NAME == "WPForge"
