"""
翻译模型 - 翻译管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Translation(Base):
    """翻译记录模型"""
    
    __tablename__ = "translations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text, nullable=False, comment="源文本")
    translated_text = Column(Text, nullable=True, comment="翻译后的文本")
    
    source_language = Column(String(10), default="auto", comment="源语言")
    target_language = Column(String(10), nullable=False, comment="目标语言")
    
    # 翻译引擎
    engine = Column(String(50), default="ai", comment="翻译引擎: ai/google/deepl等")
    model = Column(String(100), nullable=True, comment="使用的AI模型")
    
    # 质量评分
    quality_score = Column(Integer, nullable=True, comment="质量评分 0-100")
    is_polished = Column(Boolean, default=False, comment="是否经过AI润色")
    
    # 关联
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product = relationship("Product", backref="translations")
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    task = relationship("Task", backref="translations")
    
    # 元数据
    meta_data = Column(JSON, default=dict, comment="元数据")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Translation {self.source_language} -> {self.target_language}>"


class TranslationTerm(Base):
    """术语库模型"""
    
    __tablename__ = "translation_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    source_term = Column(String(500), nullable=False, comment="源术语")
    target_term = Column(String(500), nullable=False, comment="目标术语")
    
    source_language = Column(String(10), default="en", comment="源语言")
    target_language = Column(String(10), nullable=False, comment="目标语言")
    
    category = Column(String(100), nullable=True, comment="术语分类")
    context = Column(String(500), nullable=True, comment="使用场景/上下文")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="translation_terms")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        # 唯一约束：同一语言对的源术语唯一
    )
    
    def __repr__(self):
        return f"<TranslationTerm {self.source_term} -> {self.target_term}>"
