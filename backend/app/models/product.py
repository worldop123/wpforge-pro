"""
产品模型 - 采集的产品数据
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """产品模型"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), index=True, comment="SKU编码")
    name = Column(String(500), nullable=False, comment="产品名称")
    slug = Column(String(500), index=True, comment="URL别名")
    description = Column(Text, nullable=True, comment="产品描述")
    short_description = Column(Text, nullable=True, comment="简短描述")

    # 价格
    regular_price = Column(Numeric(10, 2), nullable=True, comment="原价")
    sale_price = Column(Numeric(10, 2), nullable=True, comment="促销价")
    price = Column(Numeric(10, 2), nullable=True, comment="当前价格")
    currency = Column(String(10), default="USD", comment="货币")

    # 库存
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    in_stock = Column(Boolean, default=True, comment="是否有库存")
    manage_stock = Column(Boolean, default=False, comment="是否管理库存")

    # 分类和标签
    categories = Column(JSON, default=list, comment="分类列表")
    tags = Column(JSON, default=list, comment="标签列表")

    # 图片
    images = Column(JSON, default=list, comment="图片列表")
    featured_image = Column(String(500), nullable=True, comment="特色图片")
    gallery_images = Column(JSON, default=list, comment="图库图片")

    # 属性和变体
    attributes = Column(JSON, default=list, comment="产品属性")
    variations = Column(JSON, default=list, comment="产品变体")
    is_variable = Column(Boolean, default=False, comment="是否是可变产品")

    # 来源信息
    source_url = Column(String(500), nullable=True, comment="来源URL")
    source_site = Column(String(200), nullable=True, index=True, comment="来源网站")
    source_id = Column(String(100), nullable=True, comment="来源产品ID")

    # 翻译状态
    translated = Column(Boolean, default=False, comment="是否已翻译")
    translation_language = Column(String(10), nullable=True, comment="翻译目标语言")

    # SEO信息
    seo_title = Column(String(200), nullable=True, comment="SEO标题")
    seo_description = Column(Text, nullable=True, comment="SEO描述")
    seo_keywords = Column(String(500), nullable=True, comment="SEO关键词")

    # WordPress同步状态
    wp_post_id = Column(Integer, nullable=True, comment="WordPress文章ID")
    wp_status = Column(String(20), default="draft", comment="WordPress状态")
    last_synced_at = Column(DateTime, nullable=True, comment="最后同步时间")

    # 状态
    status = Column(String(20), default="draft", index=True, comment="状态: draft/published/pending/trash")
    is_deleted = Column(Boolean, default=False, index=True, comment="软删除标记")

    # 扩展数据
    meta_data = Column(JSON, default=dict, comment="元数据")
    raw_data = Column(JSON, default=dict, comment="原始采集数据")

    # 关联
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True, index=True)
    site = relationship("Site", backref="products")
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    task = relationship("Task", backref="products")

    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # 复合索引：站点 + 软删除（常用查询：获取站点的未删除产品）
        Index("ix_products_site_id_is_deleted", "site_id", "is_deleted"),
        # 复合索引：状态 + 软删除（常用查询：按状态过滤产品）
        Index("ix_products_status_is_deleted", "status", "is_deleted"),
    )

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductCategory(Base):
    """产品分类模型"""
    
    __tablename__ = "product_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="分类名称")
    slug = Column(String(200), index=True, comment="分类别名")
    description = Column(Text, nullable=True, comment="分类描述")
    parent_id = Column(Integer, nullable=True, comment="父分类ID")
    
    # 来源信息
    source_id = Column(String(100), nullable=True, comment="来源分类ID")
    source_url = Column(String(500), nullable=True, comment="来源URL")
    
    # WordPress同步
    wp_term_id = Column(Integer, nullable=True, comment="WordPress分类ID")
    
    # 关联
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    site = relationship("Site", backref="categories")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProductCategory {self.name}>"
