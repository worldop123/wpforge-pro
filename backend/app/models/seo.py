"""
SEO模型 - SEO优化管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SEOAudit(Base):
    """SEO审计模型"""
    
    __tablename__ = "seo_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, comment="审计URL")
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    site = relationship("Site", backref="seo_audits")
    
    # 评分
    overall_score = Column(Integer, default=0, comment="综合评分 0-100")
    content_score = Column(Integer, default=0, comment="内容评分")
    technical_score = Column(Integer, default=0, comment="技术评分")
    performance_score = Column(Integer, default=0, comment="性能评分")
    mobile_score = Column(Integer, default=0, comment="移动端评分")
    
    # 详细数据
    meta_data = Column(JSON, default=dict, comment="元数据检查结果")
    headings = Column(JSON, default=list, comment="标题结构")
    images = Column(JSON, default=list, comment="图片分析")
    links = Column(JSON, default=list, comment="链接分析")
    performance = Column(JSON, default=dict, comment="性能数据")
    
    # 问题列表
    issues = Column(JSON, default=list, comment="发现的问题")
    recommendations = Column(JSON, default=list, comment="优化建议")
    
    # 状态
    status = Column(String(20), default="completed", comment="状态")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SEOAudit {self.url} - {self.overall_score}>"


class SEOSetting(Base):
    """SEO设置模型"""
    
    __tablename__ = "seo_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, unique=True)
    site = relationship("Site", backref="seo_settings", uselist=False)
    
    # 基础设置
    site_title = Column(String(200), nullable=True, comment="站点标题")
    site_description = Column(Text, nullable=True, comment="站点描述")
    site_keywords = Column(String(500), nullable=True, comment="站点关键词")
    
    # 标题模板
    title_template = Column(String(200), nullable=True, comment="标题模板")
    description_template = Column(Text, nullable=True, comment="描述模板")
    
    # 社交媒体
    og_image = Column(String(500), nullable=True, comment="Open Graph图片")
    twitter_card = Column(String(50), default="summary_large_image", comment="Twitter卡片类型")
    
    # 索引控制
    noindex = Column(Boolean, default=False, comment="禁止索引")
    nofollow = Column(Boolean, default=False, comment="禁止追踪")
    
    # 高级设置
    advanced_settings = Column(JSON, default=dict, comment="高级设置")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SEOSetting site_id={self.site_id}>"


class GSCProperty(Base):
    """Google Search Console 属性模型"""
    
    __tablename__ = "gsc_properties"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    site = relationship("Site", backref="gsc_properties")
    
    property_url = Column(String(500), nullable=False, comment="GSC属性URL")
    is_verified = Column(Boolean, default=False, comment="是否已验证")
    verification_method = Column(String(50), nullable=True, comment="验证方式")
    
    # API凭证
    credentials = Column(JSON, default=dict, comment="API凭证")
    
    # 统计数据
    total_clicks = Column(Integer, default=0, comment="总点击数")
    total_impressions = Column(Integer, default=0, comment="总展示数")
    average_position = Column(Float, default=0, comment="平均排名")
    
    # 状态
    status = Column(String(20), default="active", comment="状态")
    
    # 时间戳
    last_sync_at = Column(DateTime, nullable=True, comment="最后同步时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<GSCProperty {self.property_url}>"
