"""
Celery 应用入口
重新导出 app.tasks 中的 celery_app，便于使用 `celery -A app.celery worker` 启动
"""
from app.tasks import celery_app as celery

__all__ = ["celery"]
