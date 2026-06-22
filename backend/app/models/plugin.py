"""
插件模型 - 插件管理
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Plugin(Base):
    """插件模型"""
    
    __tablename__ = "plugins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="插件名称")
    slug = Column(String(100), unique=True, index=True, comment="插件标识")
    version = Column(String(50), default="1.0.0", comment="版本号")
    description = Column(Text, nullable=True, comment="插件描述")
    
    # 作者信息
    author = Column(String(200), nullable=True, comment="作者")
    author_url = Column(String(500), nullable=True, comment="作者网址")
    plugin_url = Column(String(500), nullable=True, comment="插件网址")
    
    # 分类
    category = Column(String(50), default="general", comment="插件分类")
    tags = Column(JSON, default=list, comment="标签")
    
    # 状态
    is_active = Column(Boolean, default=False, comment="是否启用")
    is_installed = Column(Boolean, default=False, comment="是否已安装")
    
    # 配置
    settings = Column(JSON, default=dict, comment="插件设置")
    requirements = Column(JSON, default=list, comment="依赖要求")
    
    # 文件路径
    plugin_path = Column(String(500), nullable=True, comment="插件目录路径")
    main_file = Column(String(200), nullable=True, comment="主文件")
    
    # 元数据
    meta_data = Column(JSON, default=dict, comment="元数据")
    
    # 时间戳
    installed_at = Column(DateTime, nullable=True, comment="安装时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Plugin {self.name}>"


class PluginSetting(Base):
    """插件设置模型"""
    
    __tablename__ = "plugin_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    plugin_id = Column(Integer, ForeignKey("plugins.id"), nullable=False)
    plugin = relationship("Plugin", backref="settings_entries")
    
    key = Column(String(100), nullable=False, comment="设置键")
    value = Column(Text, nullable=True, comment="设置值")
    value_type = Column(String(20), default="string", comment="值类型")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<PluginSetting {self.key}>"
