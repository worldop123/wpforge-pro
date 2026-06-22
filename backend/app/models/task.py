"""
任务模型 - 任务队列管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Task(Base):
    """任务模型"""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True, comment="Celery任务ID")
    name = Column(String(200), nullable=False, comment="任务名称")
    task_type = Column(String(50), nullable=False, comment="任务类型: scrape/translate/import/seo等")
    
    # 状态
    status = Column(String(20), default="pending", comment="状态: pending/running/completed/failed/cancelled")
    progress = Column(Float, default=0, comment="进度百分比 0-100")
    
    # 任务参数和结果
    params = Column(JSON, default=dict, comment="任务参数")
    result = Column(JSON, default=dict, comment="任务结果")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 统计
    total_items = Column(Integer, default=0, comment="总项目数")
    processed_items = Column(Integer, default=0, comment="已处理项目数")
    failed_items = Column(Integer, default=0, comment="失败项目数")
    
    # 时间
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    duration = Column(Float, default=0, comment="耗时（秒）")
    
    # 优先级
    priority = Column(Integer, default=5, comment="优先级 1-10")
    
    # 关联
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    site = relationship("Site", backref="tasks")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="tasks")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Task {self.name} - {self.status}>"


class TaskLog(Base):
    """任务日志模型"""
    
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    task = relationship("Task", backref="logs")
    
    level = Column(String(20), default="info", comment="日志级别: info/warning/error/debug")
    message = Column(Text, nullable=False, comment="日志消息")
    details = Column(JSON, default=dict, comment="详细信息")
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<TaskLog {self.level}: {self.message[:50]}>"
