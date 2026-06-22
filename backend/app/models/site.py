"""
站点模型 - WordPress站点管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Site(Base):
    """WordPress站点模型"""
    
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="站点名称")
    url = Column(String(500), nullable=False, comment="站点URL")
    description = Column(Text, nullable=True, comment="站点描述")
    
    # WordPress连接信息
    wp_url = Column(String(500), nullable=False, comment="WordPress地址")
    wp_username = Column(String(100), nullable=False, comment="WordPress用户名")
    wp_password = Column(String(255), nullable=False, comment="WordPress应用密码")
    wp_rest_url = Column(String(500), nullable=True, comment="REST API地址")
    
    # WooCommerce配置
    wc_consumer_key = Column(String(255), nullable=True, comment="WooCommerce Consumer Key")
    wc_consumer_secret = Column(String(255), nullable=True, comment="WooCommerce Consumer Secret")
    
    # 站点配置
    language = Column(String(10), default="zh-CN", comment="站点语言")
    currency = Column(String(10), default="CNY", comment="站点货币")
    price_markup = Column(Integer, default=30, comment="加价百分比")
    
    # 页面构建器
    page_builder = Column(String(50), default="elementor", comment="页面构建器: elementor/bricks/gutenberg")
    
    # SEO配置
    seo_title_template = Column(String(200), nullable=True, comment="SEO标题模板")
    seo_description_template = Column(Text, nullable=True, comment="SEO描述模板")
    
    # 状态
    status = Column(String(20), default="active", comment="状态: active/inactive/error")
    last_sync_at = Column(DateTime, nullable=True, comment="最后同步时间")
    
    # 扩展配置
    config = Column(JSON, default=dict, comment="扩展配置")
    
    # 关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="sites")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Site {self.name}>"
