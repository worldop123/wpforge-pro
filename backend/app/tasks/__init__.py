"""
Celery任务系统 - 异步任务队列
"""
from celery import Celery
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "wpforge",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 任务超时时间1小时
    task_soft_time_limit=3300,  # 软超时时间
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=86400,  # 结果过期时间24小时
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])


def get_task_function(task_type: str):
    """根据任务类型获取任务函数"""
    task_map = {
        "scraping": "app.tasks.scraping_tasks.scrape_products_task",
        "translation": "app.tasks.translation_tasks.translate_products_task",
        "import": "app.tasks.import_tasks.import_to_wordpress_task",
        "seo": "app.tasks.seo_tasks.optimize_seo_task",
        "cloning": "app.tasks.cloning_tasks.clone_site_task",
        "pricing": "app.tasks.pricing_tasks.calculate_prices_task",
    }
    
    task_path = task_map.get(task_type)
    if not task_path:
        return None
    
    try:
        module_name, func_name = task_path.rsplit(".", 1)
        module = __import__(module_name, fromlist=[func_name])
        return getattr(module, func_name)
    except (ImportError, AttributeError):
        return None


# 导入任务模块以注册
try:
    from app.tasks import scraping_tasks  # noqa: F401
    from app.tasks import translation_tasks  # noqa: F401
    from app.tasks import import_tasks  # noqa: F401
    from app.tasks import seo_tasks  # noqa: F401
    from app.tasks import cloning_tasks  # noqa: F401
except ImportError:
    pass
