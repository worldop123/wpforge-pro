"""
插件系统模块
重新导出 app.services.plugin_system 中的核心组件，并提供全局实例获取函数
同时提供示例插件
"""
from app.services.plugin_system import (
    HookManager,
    PluginBase,
    PluginManager,
    PluginInfo,
    PluginStatus,
    PluginEventType,
    PluginEvent,
    PluginEventBus,
    PluginMetadataStore,
    PluginConfigField,
    PluginConfigManager,
    DependencyResolver,
    MarketplacePlugin,
    PluginMarketplace,
    PluginLifecycleManager,
    hook_manager,
    plugin_manager,
    plugin_lifecycle_manager,
    plugin_event_bus,
    plugin_metadata_store,
    plugin_config_manager,
    plugin_dependency_resolver,
)

# 示例插件
from app.plugins.seo_enhancer import SEOEnhancerPlugin
from app.plugins.security_scanner import SecurityScannerPlugin


def get_hook_manager() -> HookManager:
    """获取全局钩子管理器单例"""
    return hook_manager


def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器单例"""
    return plugin_manager


def get_lifecycle_manager() -> PluginLifecycleManager:
    """获取全局插件生命周期管理器单例"""
    return plugin_lifecycle_manager


# 内置示例插件注册表
BUILTIN_PLUGINS = {
    "seo_enhancer": SEOEnhancerPlugin,
    "security_scanner": SecurityScannerPlugin,
}


__all__ = [
    "PluginManager",
    "PluginBase",
    "PluginInfo",
    "PluginStatus",
    "HookManager",
    "PluginEventType",
    "PluginEvent",
    "PluginEventBus",
    "PluginMetadataStore",
    "PluginConfigField",
    "PluginConfigManager",
    "DependencyResolver",
    "MarketplacePlugin",
    "PluginMarketplace",
    "PluginLifecycleManager",
    "get_plugin_manager",
    "get_hook_manager",
    "get_lifecycle_manager",
    "hook_manager",
    "plugin_manager",
    "plugin_lifecycle_manager",
    "plugin_event_bus",
    "plugin_metadata_store",
    "plugin_config_manager",
    "plugin_dependency_resolver",
    "SEOEnhancerPlugin",
    "SecurityScannerPlugin",
    "BUILTIN_PLUGINS",
]
