"""
插件化架构系统
钩子系统（Hooks/Filters）、插件管理器、插件市场基础框架
"""
import importlib
import inspect
from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from app.core.logging import get_logger

logger = get_logger(__name__)


class HookType(str, Enum):
    """钩子类型"""
    ACTION = "action"  # 动作钩子，执行操作
    FILTER = "filter"  # 过滤钩子，修改数据


class PluginStatus(str, Enum):
    """插件状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    INSTALLING = "installing"
    UPDATING = "updating"


@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    author_url: str = ""
    plugin_url: str = ""
    requires: str = ""  # 最低WPForge版本
    tested: str = ""  # 最高测试版本
    license: str = "GPL v3"
    text_domain: str = ""
    domain_path: str = ""
    status: PluginStatus = PluginStatus.INACTIVE
    hooks: List[str] = field(default_factory=list)
    filters: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    activated_at: Optional[float] = None
    installed_at: Optional[float] = None


class HookManager:
    """钩子管理器"""
    
    def __init__(self):
        self._actions: Dict[str, List[Dict[str, Any]]] = {}
        self._filters: Dict[str, List[Dict[str, Any]]] = {}
        self._did_action: Dict[str, int] = {}
        self._current_filter: Optional[str] = None
        self._current_priority: int = 0
    
    def add_action(self, 
                   hook: str,
                   callback: Callable,
                   priority: int = 10,
                   accepted_args: int = 1) -> None:
        """
        添加动作钩子
        
        Args:
            hook: 钩子名称
            callback: 回调函数
            priority: 优先级（数字越小越先执行）
            accepted_args: 接受的参数数量
        """
        if hook not in self._actions:
            self._actions[hook] = []
        
        self._actions[hook].append({
            "callback": callback,
            "priority": priority,
            "accepted_args": accepted_args,
        })
        
        # 按优先级排序
        self._actions[hook].sort(key=lambda x: x["priority"])
        
        logger.debug(f"Added action hook: {hook} (priority: {priority})")
    
    def add_filter(self,
                   hook: str,
                   callback: Callable,
                   priority: int = 10,
                   accepted_args: int = 1) -> None:
        """
        添加过滤钩子
        
        Args:
            hook: 钩子名称
            callback: 回调函数
            priority: 优先级
            accepted_args: 接受的参数数量
        """
        if hook not in self._filters:
            self._filters[hook] = []
        
        self._filters[hook].append({
            "callback": callback,
            "priority": priority,
            "accepted_args": accepted_args,
        })
        
        # 按优先级排序
        self._filters[hook].sort(key=lambda x: x["priority"])
        
        logger.debug(f"Added filter hook: {hook} (priority: {priority})")
    
    def remove_action(self, hook: str, callback: Callable, priority: int = 10) -> bool:
        """
        移除动作钩子
        
        Args:
            hook: 钩子名称
            callback: 回调函数
            priority: 优先级
            
        Returns:
            是否成功移除
        """
        if hook not in self._actions:
            return False
        
        original_count = len(self._actions[hook])
        self._actions[hook] = [
            h for h in self._actions[hook]
            if not (h["callback"] == callback and h["priority"] == priority)
        ]
        
        return len(self._actions[hook]) < original_count
    
    def remove_filter(self, hook: str, callback: Callable, priority: int = 10) -> bool:
        """
        移除过滤钩子
        
        Args:
            hook: 钩子名称
            callback: 回调函数
            priority: 优先级
            
        Returns:
            是否成功移除
        """
        if hook not in self._filters:
            return False
        
        original_count = len(self._filters[hook])
        self._filters[hook] = [
            h for h in self._filters[hook]
            if not (h["callback"] == callback and h["priority"] == priority)
        ]
        
        return len(self._filters[hook]) < original_count
    
    def do_action(self, hook: str, *args, **kwargs) -> None:
        """
        执行动作钩子
        
        Args:
            hook: 钩子名称
            *args: 参数
            **kwargs: 关键字参数
        """
        # 记录执行次数
        if hook not in self._did_action:
            self._did_action[hook] = 0
        self._did_action[hook] += 1
        
        if hook not in self._actions:
            return
        
        previous_filter = self._current_filter
        self._current_filter = hook
        
        try:
            for action in self._actions[hook]:
                self._current_priority = action["priority"]
                
                callback = action["callback"]
                accepted_args = action["accepted_args"]
                
                # 限制参数数量
                if accepted_args == 1:
                    callback_args = args[:1]
                else:
                    callback_args = args[:accepted_args]
                
                try:
                    callback(*callback_args, **kwargs)
                except Exception as e:
                    logger.error(f"Error in action hook '{hook}': {e}")
        finally:
            self._current_filter = previous_filter
    
    def apply_filters(self, hook: str, value: Any, *args) -> Any:
        """
        应用过滤钩子
        
        Args:
            hook: 钩子名称
            value: 要过滤的值
            *args: 额外参数
            
        Returns:
            过滤后的值
        """
        if hook not in self._filters:
            return value
        
        previous_filter = self._current_filter
        self._current_filter = hook
        
        try:
            for filter_hook in self._filters[hook]:
                self._current_priority = filter_hook["priority"]
                
                callback = filter_hook["callback"]
                accepted_args = filter_hook["accepted_args"]
                
                # 准备参数
                if accepted_args == 1:
                    callback_args = [value]
                else:
                    callback_args = [value] + list(args[:accepted_args - 1])
                
                try:
                    value = callback(*callback_args)
                except Exception as e:
                    logger.error(f"Error in filter hook '{hook}': {e}")
        finally:
            self._current_filter = previous_filter
        
        return value
    
    def has_action(self, hook: str, callback: Optional[Callable] = None) -> bool:
        """
        检查是否有动作钩子
        
        Args:
            hook: 钩子名称
            callback: 可选的回调函数
            
        Returns:
            是否存在
        """
        if hook not in self._actions:
            return False
        
        if callback is None:
            return len(self._actions[hook]) > 0
        
        return any(
            h["callback"] == callback
            for h in self._actions[hook]
        )
    
    def has_filter(self, hook: str, callback: Optional[Callable] = None) -> bool:
        """
        检查是否有过滤钩子
        
        Args:
            hook: 钩子名称
            callback: 可选的回调函数
            
        Returns:
            是否存在
        """
        if hook not in self._filters:
            return False
        
        if callback is None:
            return len(self._filters[hook]) > 0
        
        return any(
            h["callback"] == callback
            for h in self._filters[hook]
        )
    
    def did_action(self, hook: str) -> int:
        """
        获取动作执行次数
        
        Args:
            hook: 钩子名称
            
        Returns:
            执行次数
        """
        return self._did_action.get(hook, 0)
    
    def doing_action(self, hook: Optional[str] = None) -> bool:
        """
        检查是否正在执行某个动作
        
        Args:
            hook: 钩子名称，None则检查是否在执行任何钩子
            
        Returns:
            是否正在执行
        """
        if hook is None:
            return self._current_filter is not None
        return self._current_filter == hook
    
    def current_filter(self) -> Optional[str]:
        """获取当前正在执行的钩子"""
        return self._current_filter
    
    def get_all_hooks(self) -> Dict[str, List[str]]:
        """获取所有钩子"""
        return {
            "actions": list(self._actions.keys()),
            "filters": list(self._filters.keys()),
        }
    
    def get_hook_count(self) -> Dict[str, int]:
        """获取钩子数量统计"""
        return {
            "actions": sum(len(v) for v in self._actions.values()),
            "filters": sum(len(v) for v in self._filters.values()),
            "action_hooks": len(self._actions),
            "filter_hooks": len(self._filters),
        }


class PluginManager:
    """插件管理器"""
    
    def __init__(self, hook_manager: HookManager):
        self.hook_manager = hook_manager
        self._plugins: Dict[str, PluginInfo] = {}
        self._plugin_instances: Dict[str, Any] = {}
        self._plugin_dirs: List[str] = []
    
    def register_plugin(self, plugin_info: PluginInfo, plugin_instance: Any = None) -> None:
        """
        注册插件
        
        Args:
            plugin_info: 插件信息
            plugin_instance: 插件实例
        """
        self._plugins[plugin_info.name] = plugin_info
        
        if plugin_instance:
            self._plugin_instances[plugin_info.name] = plugin_instance
        
        logger.info(f"Registered plugin: {plugin_info.name} v{plugin_info.version}")
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """
        激活插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功激活
        """
        if plugin_name not in self._plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin = self._plugins[plugin_name]
        
        if plugin.status == PluginStatus.ACTIVE:
            logger.warning(f"Plugin already active: {plugin_name}")
            return True
        
        try:
            # 执行激活钩子
            self.hook_manager.do_action(f"activate_{plugin_name}")
            self.hook_manager.do_action("plugin_activated", plugin_name)
            
            plugin.status = PluginStatus.ACTIVE
            import time
            plugin.activated_at = time.time()
            
            logger.info(f"Plugin activated: {plugin_name}")
            return True
            
        except Exception as e:
            plugin.status = PluginStatus.ERROR
            plugin.error_message = str(e)
            logger.error(f"Failed to activate plugin {plugin_name}: {e}")
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """
        停用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功停用
        """
        if plugin_name not in self._plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin = self._plugins[plugin_name]
        
        if plugin.status != PluginStatus.ACTIVE:
            logger.warning(f"Plugin not active: {plugin_name}")
            return True
        
        try:
            # 执行停用钩子
            self.hook_manager.do_action(f"deactivate_{plugin_name}")
            self.hook_manager.do_action("plugin_deactivated", plugin_name)
            
            plugin.status = PluginStatus.INACTIVE
            plugin.activated_at = None
            
            logger.info(f"Plugin deactivated: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate plugin {plugin_name}: {e}")
            return False
    
    def install_plugin(self, plugin_name: str, plugin_data: Dict[str, Any]) -> bool:
        """
        安装插件（简化实现）
        
        Args:
            plugin_name: 插件名称
            plugin_data: 插件数据
            
        Returns:
            是否成功安装
        """
        try:
            plugin_info = PluginInfo(
                name=plugin_name,
                version=plugin_data.get("version", "1.0.0"),
                description=plugin_data.get("description", ""),
                author=plugin_data.get("author", ""),
            )
            
            import time
            plugin_info.installed_at = time.time()
            
            self._plugins[plugin_name] = plugin_info
            
            self.hook_manager.do_action("plugin_installed", plugin_name)
            
            logger.info(f"Plugin installed: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install plugin {plugin_name}: {e}")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否成功卸载
        """
        if plugin_name not in self._plugins:
            logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        try:
            # 先停用
            if self._plugins[plugin_name].status == PluginStatus.ACTIVE:
                self.deactivate_plugin(plugin_name)
            
            # 执行卸载钩子
            self.hook_manager.do_action(f"uninstall_{plugin_name}")
            self.hook_manager.do_action("plugin_uninstalled", plugin_name)
            
            # 移除插件
            del self._plugins[plugin_name]
            
            if plugin_name in self._plugin_instances:
                del self._plugin_instances[plugin_name]
            
            logger.info(f"Plugin uninstalled: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        return self._plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInfo]:
        """获取所有插件"""
        return self._plugins.copy()
    
    def get_active_plugins(self) -> Dict[str, PluginInfo]:
        """获取所有激活的插件"""
        return {
            name: plugin
            for name, plugin in self._plugins.items()
            if plugin.status == PluginStatus.ACTIVE
        }
    
    def is_plugin_active(self, plugin_name: str) -> bool:
        """检查插件是否激活"""
        if plugin_name not in self._plugins:
            return False
        return self._plugins[plugin_name].status == PluginStatus.ACTIVE
    
    def get_plugin_instance(self, plugin_name: str) -> Optional[Any]:
        """获取插件实例"""
        return self._plugin_instances.get(plugin_name)
    
    def update_plugin_settings(self, plugin_name: str, settings: Dict[str, Any]) -> bool:
        """
        更新插件设置
        
        Args:
            plugin_name: 插件名称
            settings: 设置字典
            
        Returns:
            是否成功
        """
        if plugin_name not in self._plugins:
            return False
        
        self._plugins[plugin_name].settings.update(settings)
        return True
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """获取插件统计"""
        total = len(self._plugins)
        active = sum(1 for p in self._plugins.values() if p.status == PluginStatus.ACTIVE)
        inactive = sum(1 for p in self._plugins.values() if p.status == PluginStatus.INACTIVE)
        errors = sum(1 for p in self._plugins.values() if p.status == PluginStatus.ERROR)
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "errors": errors,
        }


class PluginBase:
    """插件基类"""
    
    def __init__(self, hook_manager: HookManager):
        self.hook_manager = hook_manager
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = ""
        self.author = ""
    
    def activate(self) -> None:
        """插件激活时调用"""
        pass
    
    def deactivate(self) -> None:
        """插件停用时调用"""
        pass
    
    def uninstall(self) -> None:
        """插件卸载时调用"""
        pass
    
    def register_hooks(self) -> None:
        """注册钩子（子类实现）"""
        pass
    
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        return PluginInfo(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
        )


# 常用钩子名称常量
class Hooks:
    """常用钩子名称"""
    
    # 系统钩子
    INIT = "init"
    SHUTDOWN = "shutdown"
    ADMIN_INIT = "admin_init"
    
    # 插件钩子
    PLUGIN_ACTIVATED = "plugin_activated"
    PLUGIN_DEACTIVATED = "plugin_deactivated"
    PLUGIN_INSTALLED = "plugin_installed"
    PLUGIN_UNINSTALLED = "plugin_uninstalled"
    
    # 站点钩子
    SITE_CREATED = "site_created"
    SITE_UPDATED = "site_updated"
    SITE_DELETED = "site_deleted"
    
    # 产品钩子
    PRODUCT_CREATED = "product_created"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"
    PRODUCT_IMPORTED = "product_imported"
    
    # 采集钩子
    SCRAPING_STARTED = "scraping_started"
    SCRAPING_COMPLETED = "scraping_completed"
    SCRAPING_FAILED = "scraping_failed"
    
    # 翻译钩子
    TRANSLATION_STARTED = "translation_started"
    TRANSLATION_COMPLETED = "translation_completed"
    TRANSLATION_FAILED = "translation_failed"
    
    # SEO钩子
    SEO_OPTIMIZED = "seo_optimized"
    SEO_AUDIT_COMPLETED = "seo_audit_completed"
    
    # 导入钩子
    IMPORT_STARTED = "import_started"
    IMPORT_COMPLETED = "import_completed"
    IMPORT_FAILED = "import_failed"
    
    # 内容过滤钩子
    THE_CONTENT = "the_content"
    THE_TITLE = "the_title"
    THE_EXCERPT = "the_excerpt"
    
    # 价格钩子
    PRODUCT_PRICE = "product_price"
    PRODUCT_SALE_PRICE = "product_sale_price"
    
    # 页面构建器钩子
    PAGE_BUILDER_BEFORE_RENDER = "page_builder_before_render"
    PAGE_BUILDER_AFTER_RENDER = "page_builder_after_render"
    
    # 监控钩子
    MONITOR_ALERT = "monitor_alert"
    MONITOR_CHECK_COMPLETED = "monitor_check_completed"


# 全局实例
hook_manager = HookManager()
plugin_manager = PluginManager(hook_manager)


def add_action(hook: str, callback: Callable, priority: int = 10, accepted_args: int = 1) -> None:
    """便捷函数：添加动作钩子"""
    hook_manager.add_action(hook, callback, priority, accepted_args)


def add_filter(hook: str, callback: Callable, priority: int = 10, accepted_args: int = 1) -> None:
    """便捷函数：添加过滤钩子"""
    hook_manager.add_filter(hook, callback, priority, accepted_args)


def do_action(hook: str, *args, **kwargs) -> None:
    """便捷函数：执行动作钩子"""
    hook_manager.do_action(hook, *args, **kwargs)


def apply_filters(hook: str, value: Any, *args) -> Any:
    """便捷函数：应用过滤钩子"""
    return hook_manager.apply_filters(hook, value, *args)
