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

    def install(self) -> None:
        """插件安装时调用（生命周期钩子）"""
        pass

    def uninstall(self) -> None:
        """插件卸载时调用"""
        pass

    def enable(self) -> None:
        """插件启用时调用（生命周期钩子）"""
        pass

    def disable(self) -> None:
        """插件禁用时调用（生命周期钩子）"""
        pass

    def upgrade(self, old_version: str, new_version: str) -> None:
        """插件升级时调用（生命周期钩子）

        Args:
            old_version: 旧版本号
            new_version: 新版本号
        """
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


# ===========================================================================
# 任务3：插件化架构完善
# 插件元数据存储、插件市场、依赖管理、生命周期钩子、事件系统、配置管理
# ===========================================================================
import os
import json
import time
import asyncio
from typing import Set, Tuple


class PluginEventType(str, Enum):
    """插件事件类型"""
    CUSTOM = "custom"  # 自定义事件
    LIFECYCLE = "lifecycle"  # 生命周期事件
    SYSTEM = "system"  # 系统事件


@dataclass
class PluginEvent:
    """插件事件"""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    event_type: PluginEventType = PluginEventType.CUSTOM
    timestamp: float = field(default_factory=time.time)
    source: str = ""  # 事件来源（插件名）


class PluginEventBus:
    """插件事件总线 - 插件可注册事件监听器、触发自定义事件"""

    def __init__(self):
        self._listeners: Dict[str, List[Dict[str, Any]]] = {}
        self._history: List[PluginEvent] = []
        self._max_history = 1000

    def subscribe(self, event_name: str, callback: Callable, priority: int = 10) -> None:
        """订阅事件

        Args:
            event_name: 事件名称
            callback: 回调函数，接收 PluginEvent 参数
            priority: 优先级（数字越小越先执行）
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append({
            "callback": callback,
            "priority": priority,
        })
        # 按优先级排序
        self._listeners[event_name].sort(key=lambda x: x["priority"])
        logger.debug(f"Subscribed to event: {event_name}")

    def unsubscribe(self, event_name: str, callback: Callable) -> bool:
        """取消订阅事件

        Returns:
            是否成功取消
        """
        if event_name not in self._listeners:
            return False
        original = len(self._listeners[event_name])
        self._listeners[event_name] = [
            l for l in self._listeners[event_name]
            if l["callback"] != callback
        ]
        return len(self._listeners[event_name]) < original

    def publish(self, event: PluginEvent) -> int:
        """发布事件

        Args:
            event: 插件事件对象

        Returns:
            成功触发的监听器数量
        """
        # 记录历史
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        count = 0
        listeners = self._listeners.get(event.name, [])
        for listener in listeners:
            try:
                listener["callback"](event)
                count += 1
            except Exception as e:
                logger.error(f"Error in event listener for '{event.name}': {e}")
        return count

    def publish_simple(self, event_name: str, data: Dict[str, Any] = None,
                       source: str = "", event_type: PluginEventType = PluginEventType.CUSTOM) -> int:
        """简化发布事件

        Args:
            event_name: 事件名称
            data: 事件数据
            source: 事件来源
            event_type: 事件类型

        Returns:
            成功触发的监听器数量
        """
        return self.publish(PluginEvent(
            name=event_name,
            data=data or {},
            source=source,
            event_type=event_type,
        ))

    def get_listeners(self, event_name: str) -> List[Dict[str, Any]]:
        """获取事件的所有监听器"""
        return list(self._listeners.get(event_name, []))

    def has_listeners(self, event_name: str) -> bool:
        """检查事件是否有监听器"""
        return len(self._listeners.get(event_name, [])) > 0

    def get_event_history(self, event_name: str = None, limit: int = 100) -> List[PluginEvent]:
        """获取事件历史

        Args:
            event_name: 事件名称，None则返回所有
            limit: 返回数量上限

        Returns:
            事件历史列表
        """
        if event_name:
            events = [e for e in self._history if e.name == event_name]
        else:
            events = list(self._history)
        return events[-limit:]

    def clear_history(self) -> None:
        """清空事件历史"""
        self._history.clear()

    def clear_listeners(self, event_name: str = None) -> None:
        """清空监听器

        Args:
            event_name: 事件名称，None则清空所有
        """
        if event_name:
            self._listeners.pop(event_name, None)
        else:
            self._listeners.clear()

    def get_stats(self) -> Dict[str, int]:
        """获取事件总线统计"""
        return {
            "event_types": len(self._listeners),
            "total_listeners": sum(len(v) for v in self._listeners.values()),
            "history_count": len(self._history),
        }


class PluginMetadataStore:
    """插件元数据存储 - 模拟数据库存储（可替换为真实DB后端）

    提供插件元数据的持久化能力，将插件信息存储到数据库或配置文件。
    此实现使用内存字典模拟，可通过子类化替换为 SQLAlchemy 后端。
    """

    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}

    def save(self, plugin_name: str, metadata: Dict[str, Any]) -> bool:
        """保存插件元数据

        Args:
            plugin_name: 插件名称
            metadata: 元数据字典

        Returns:
            是否成功
        """
        self._storage[plugin_name] = {
            "name": plugin_name,
            "metadata": dict(metadata),
            "updated_at": time.time(),
        }
        logger.debug(f"Saved metadata for plugin: {plugin_name}")
        return True

    def load(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """加载插件元数据

        Returns:
            元数据字典，不存在返回None
        """
        entry = self._storage.get(plugin_name)
        return dict(entry["metadata"]) if entry else None

    def delete(self, plugin_name: str) -> bool:
        """删除插件元数据

        Returns:
            是否成功删除
        """
        if plugin_name in self._storage:
            del self._storage[plugin_name]
            return True
        return False

    def exists(self, plugin_name: str) -> bool:
        """检查元数据是否存在"""
        return plugin_name in self._storage

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """列出所有插件元数据"""
        return {k: dict(v["metadata"]) for k, v in self._storage.items()}

    def update_field(self, plugin_name: str, key: str, value: Any) -> bool:
        """更新单个元数据字段

        Returns:
            是否成功
        """
        if plugin_name not in self._storage:
            return False
        self._storage[plugin_name]["metadata"][key] = value
        self._storage[plugin_name]["updated_at"] = time.time()
        return True

    def count(self) -> int:
        """获取存储的插件数量"""
        return len(self._storage)


@dataclass
class PluginConfigField:
    """插件配置字段定义"""
    key: str
    label: str = ""
    field_type: str = "string"  # string, int, float, bool, select, textarea
    default: Any = None
    options: List[Any] = field(default_factory=list)  # select 类型的选项
    description: str = ""
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    placeholder: str = ""


class PluginConfigManager:
    """插件配置管理器 - 每个插件可有自己的配置项和配置页面"""

    def __init__(self):
        self._schemas: Dict[str, List[PluginConfigField]] = {}
        self._values: Dict[str, Dict[str, Any]] = {}

    def register_schema(self, plugin_name: str, fields: List[PluginConfigField]) -> None:
        """注册配置模式

        Args:
            plugin_name: 插件名称
            fields: 配置字段列表
        """
        self._schemas[plugin_name] = list(fields)
        # 初始化默认值
        if plugin_name not in self._values:
            self._values[plugin_name] = {}
            for f in fields:
                if f.default is not None:
                    self._values[plugin_name][f.key] = f.default

    def get_schema(self, plugin_name: str) -> List[PluginConfigField]:
        """获取配置模式"""
        return list(self._schemas.get(plugin_name, []))

    def get_config_page(self, plugin_name: str) -> Dict[str, Any]:
        """获取配置页面数据（用于前端渲染）

        Args:
            plugin_name: 插件名称

        Returns:
            配置页面数据，包含字段定义和当前值
        """
        schema = self._schemas.get(plugin_name, [])
        values = self._values.get(plugin_name, {})
        return {
            "plugin": plugin_name,
            "fields": [
                {
                    "key": f.key,
                    "label": f.label,
                    "type": f.field_type,
                    "default": f.default,
                    "options": list(f.options),
                    "description": f.description,
                    "required": f.required,
                    "min": f.min_value,
                    "max": f.max_value,
                    "placeholder": f.placeholder,
                    "value": values.get(f.key, f.default),
                }
                for f in schema
            ],
        }

    def _validate(self, field: PluginConfigField, value: Any) -> Any:
        """校验并转换值，校验失败返回None"""
        try:
            if field.field_type == "int":
                v = int(value)
                if field.min_value is not None and v < field.min_value:
                    return None
                if field.max_value is not None and v > field.max_value:
                    return None
                return v
            elif field.field_type == "float":
                v = float(value)
                if field.min_value is not None and v < field.min_value:
                    return None
                if field.max_value is not None and v > field.max_value:
                    return None
                return v
            elif field.field_type == "bool":
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ("true", "1", "yes", "on")
            elif field.field_type == "select":
                if value in field.options:
                    return value
                return None
            else:  # string, textarea
                return str(value)
        except (ValueError, TypeError):
            return None

    def set_value(self, plugin_name: str, key: str, value: Any) -> bool:
        """设置单个配置值

        Returns:
            是否成功
        """
        if plugin_name not in self._schemas:
            return False
        field = next((f for f in self._schemas[plugin_name] if f.key == key), None)
        if field is None:
            return False
        validated = self._validate(field, value)
        if validated is None and field.required and value in (None, ""):
            return False
        if validated is None and field.field_type in ("int", "float", "select"):
            return False
        if plugin_name not in self._values:
            self._values[plugin_name] = {}
        self._values[plugin_name][key] = validated
        return True

    def set_values(self, plugin_name: str, values: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """批量设置配置值

        Returns:
            (是否全部成功, 失败的键列表)
        """
        if plugin_name not in self._schemas:
            return False, list(values.keys())
        failed = []
        for k, v in values.items():
            if not self.set_value(plugin_name, k, v):
                failed.append(k)
        return len(failed) == 0, failed

    def get_value(self, plugin_name: str, key: str, default: Any = None) -> Any:
        """获取单个配置值"""
        values = self._values.get(plugin_name, {})
        return values.get(key, default)

    def get_all_values(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件所有配置值"""
        return dict(self._values.get(plugin_name, {}))

    def reset_to_defaults(self, plugin_name: str) -> bool:
        """重置为默认值

        Returns:
            是否成功
        """
        if plugin_name not in self._schemas:
            return False
        self._values[plugin_name] = {
            f.key: f.default for f in self._schemas[plugin_name] if f.default is not None
        }
        return True

    def remove_plugin(self, plugin_name: str) -> bool:
        """移除插件配置

        Returns:
            是否成功移除
        """
        existed = plugin_name in self._schemas
        self._schemas.pop(plugin_name, None)
        self._values.pop(plugin_name, None)
        return existed

    def has_schema(self, plugin_name: str) -> bool:
        """检查插件是否有配置模式"""
        return plugin_name in self._schemas


class DependencyResolver:
    """插件依赖管理器 - 检查插件间依赖关系"""

    def __init__(self):
        # 依赖图: plugin_name -> [依赖的插件名]
        self._dependencies: Dict[str, List[str]] = {}

    def register(self, plugin_name: str, dependencies: List[str]) -> None:
        """注册插件依赖

        Args:
            plugin_name: 插件名称
            dependencies: 依赖的插件名列表
        """
        self._dependencies[plugin_name] = list(dependencies)

    def unregister(self, plugin_name: str) -> None:
        """取消注册插件依赖"""
        self._dependencies.pop(plugin_name, None)

    def get_dependencies(self, plugin_name: str) -> List[str]:
        """获取直接依赖"""
        return list(self._dependencies.get(plugin_name, []))

    def check_dependencies(self, plugin_name: str, installed: Set[str]) -> Tuple[bool, List[str]]:
        """检查依赖是否满足

        Args:
            plugin_name: 插件名称
            installed: 已安装的插件名集合

        Returns:
            (是否满足, 缺失的依赖列表)
        """
        deps = self._dependencies.get(plugin_name, [])
        missing = [d for d in deps if d not in installed]
        return len(missing) == 0, missing

    def get_all_dependencies(self, plugin_name: str) -> List[str]:
        """获取所有传递依赖（递归）"""
        visited: Set[str] = set()
        result: List[str] = []
        self._collect_deps(plugin_name, visited, result)
        return result

    def _collect_deps(self, plugin_name: str, visited: Set[str], result: List[str]) -> None:
        if plugin_name in visited:
            return
        visited.add(plugin_name)
        for dep in self._dependencies.get(plugin_name, []):
            if dep not in result:
                result.append(dep)
            self._collect_deps(dep, visited, result)

    def detect_cycle(self, plugin_name: str) -> bool:
        """检测依赖循环

        Returns:
            是否存在循环依赖
        """
        visited: Set[str] = set()
        stack: Set[str] = set()
        return self._has_cycle(plugin_name, visited, stack)

    def _has_cycle(self, plugin_name: str, visited: Set[str], stack: Set[str]) -> bool:
        visited.add(plugin_name)
        stack.add(plugin_name)
        for dep in self._dependencies.get(plugin_name, []):
            if dep not in visited:
                if self._has_cycle(dep, visited, stack):
                    return True
            elif dep in stack:
                return True
        stack.discard(plugin_name)
        return False

    def topological_sort(self, plugin_names: List[str]) -> List[str]:
        """拓扑排序（依赖在前）

        Args:
            plugin_names: 待排序的插件名列表

        Returns:
            排序后的插件名列表
        """
        in_degree = {p: 0 for p in plugin_names}
        graph = {p: [] for p in plugin_names}
        for p in plugin_names:
            for dep in self._dependencies.get(p, []):
                if dep in graph and dep != p:
                    graph[dep].append(p)
                    in_degree[p] += 1
        # 拓扑排序（Kahn算法）
        queue = [p for p in plugin_names if in_degree[p] == 0]
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return result

    def get_dependents(self, plugin_name: str) -> List[str]:
        """获取依赖于该插件的其他插件

        Args:
            plugin_name: 插件名称

        Returns:
            依赖此插件的插件名列表
        """
        return [
            p for p, deps in self._dependencies.items()
            if plugin_name in deps
        ]

    def can_uninstall(self, plugin_name: str) -> Tuple[bool, List[str]]:
        """检查插件是否可卸载（无其他插件依赖它）

        Returns:
            (是否可卸载, 依赖它的插件列表)
        """
        dependents = self.get_dependents(plugin_name)
        return len(dependents) == 0, dependents


@dataclass
class MarketplacePlugin:
    """市场插件信息"""
    name: str
    slug: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    download_url: str = ""
    homepage: str = ""
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    rating: float = 0.0
    downloads: int = 0
    last_updated: float = 0.0
    requires: str = ""
    size: int = 0  # 字节


class PluginMarketplace:
    """插件市场 - 本地目录扫描 + 远程仓库拉取"""

    def __init__(self, local_dir: str = "", remote_url: str = ""):
        self.local_dir = local_dir
        self.remote_url = remote_url
        self._local_cache: Dict[str, MarketplacePlugin] = {}
        self._remote_cache: Dict[str, MarketplacePlugin] = {}

    def scan_local(self) -> List[MarketplacePlugin]:
        """扫描本地插件目录

        Returns:
            本地插件列表
        """
        results = []
        if not self.local_dir or not os.path.isdir(self.local_dir):
            return results
        for entry in os.listdir(self.local_dir):
            plugin_path = os.path.join(self.local_dir, entry)
            if not os.path.isdir(plugin_path):
                continue
            manifest = os.path.join(plugin_path, "plugin.json")
            if not os.path.isfile(manifest):
                continue
            try:
                with open(manifest, "r", encoding="utf-8") as f:
                    data = json.load(f)
                plugin = MarketplacePlugin(
                    name=data.get("name", entry),
                    slug=data.get("slug", entry),
                    version=data.get("version", "1.0.0"),
                    description=data.get("description", ""),
                    author=data.get("author", ""),
                    category=data.get("category", "general"),
                    tags=data.get("tags", []),
                    download_url=plugin_path,
                )
                results.append(plugin)
                self._local_cache[plugin.slug] = plugin
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Error scanning plugin {entry}: {e}")
        return results

    def fetch_remote(self, fetcher: Callable[[], List[Dict[str, Any]]] = None) -> List[MarketplacePlugin]:
        """从远程仓库拉取插件列表

        Args:
            fetcher: 可注入的获取函数（用于测试/自定义HTTP客户端）

        Returns:
            远程插件列表
        """
        if fetcher is None:
            # 默认返回空列表（真实场景会发HTTP请求到 self.remote_url）
            return []
        try:
            data_list = fetcher()
        except Exception as e:
            logger.error(f"Error fetching remote plugins: {e}")
            return []
        results = []
        for data in data_list:
            plugin = MarketplacePlugin(
                name=data.get("name", ""),
                slug=data.get("slug", ""),
                version=data.get("version", "1.0.0"),
                description=data.get("description", ""),
                author=data.get("author", ""),
                download_url=data.get("download_url", ""),
                homepage=data.get("homepage", ""),
                category=data.get("category", "general"),
                tags=data.get("tags", []),
                rating=float(data.get("rating", 0.0)),
                downloads=int(data.get("downloads", 0)),
            )
            results.append(plugin)
            if plugin.slug:
                self._remote_cache[plugin.slug] = plugin
        return results

    def search(self, keyword: str, source: str = "all") -> List[MarketplacePlugin]:
        """搜索插件

        Args:
            keyword: 搜索关键词
            source: 搜索来源 (all/local/remote)

        Returns:
            匹配的插件列表
        """
        keyword_lower = keyword.lower()
        results = []
        pools = []
        if source in ("all", "local"):
            pools.extend(self._local_cache.values())
        if source in ("all", "remote"):
            pools.extend(self._remote_cache.values())
        for p in pools:
            if (keyword_lower in p.name.lower()
                    or keyword_lower in p.description.lower()
                    or any(keyword_lower in t.lower() for t in p.tags)):
                results.append(p)
        return results

    def get_plugin(self, slug: str) -> Optional[MarketplacePlugin]:
        """获取插件信息"""
        if slug in self._local_cache:
            return self._local_cache[slug]
        return self._remote_cache.get(slug)

    def get_categories(self) -> Dict[str, int]:
        """获取分类统计"""
        cats = {}
        for p in list(self._local_cache.values()) + list(self._remote_cache.values()):
            cats[p.category] = cats.get(p.category, 0) + 1
        return cats

    def clear_cache(self) -> None:
        """清空缓存"""
        self._local_cache.clear()
        self._remote_cache.clear()

    def get_local_plugins(self) -> List[MarketplacePlugin]:
        """获取所有本地插件"""
        return list(self._local_cache.values())

    def get_remote_plugins(self) -> List[MarketplacePlugin]:
        """获取所有远程插件"""
        return list(self._remote_cache.values())


class PluginLifecycleManager:
    """插件生命周期管理器 - 整合元数据存储、依赖管理、事件系统、配置管理

    提供完整的插件安装/卸载/启用/禁用/升级流程，并触发对应的生命周期钩子。
    """

    def __init__(self, hook_manager: HookManager):
        self.hook_manager = hook_manager
        self.metadata_store = PluginMetadataStore()
        self.dependency_resolver = DependencyResolver()
        self.event_bus = PluginEventBus()
        self.config_manager = PluginConfigManager()
        self._plugins: Dict[str, PluginInfo] = {}
        self._instances: Dict[str, PluginBase] = {}

    def _emit(self, event_name: str, plugin_name: str, data: Dict[str, Any] = None) -> None:
        """发布生命周期事件"""
        self.event_bus.publish_simple(
            event_name,
            data=data or {"plugin": plugin_name},
            source=plugin_name,
            event_type=PluginEventType.LIFECYCLE,
        )

    def install(self, plugin_info: PluginInfo, instance: PluginBase = None,
                dependencies: List[str] = None) -> Tuple[bool, str]:
        """安装插件

        Args:
            plugin_info: 插件信息
            instance: 插件实例（可选）
            dependencies: 依赖的插件名列表（可选）

        Returns:
            (是否成功, 消息)
        """
        name = plugin_info.name
        if name in self._plugins:
            return False, f"插件 {name} 已安装"

        # 注册依赖
        if dependencies:
            self.dependency_resolver.register(name, dependencies)
            # 检查依赖是否满足
            installed = set(self._plugins.keys())
            ok, missing = self.dependency_resolver.check_dependencies(name, installed)
            if not ok:
                return False, f"缺少依赖: {', '.join(missing)}"

        # 设置安装中状态
        plugin_info.status = PluginStatus.INSTALLING
        plugin_info.installed_at = time.time()
        self._plugins[name] = plugin_info

        try:
            # 调用插件实例的 install 钩子
            if instance is not None:
                instance.hook_manager = self.hook_manager
                instance.install()
                self._instances[name] = instance

            # 保存元数据
            self.metadata_store.save(name, {
                "version": plugin_info.version,
                "description": plugin_info.description,
                "author": plugin_info.author,
                "installed_at": plugin_info.installed_at,
            })

            # 触发钩子和事件
            self.hook_manager.do_action(f"install_{name}")
            self.hook_manager.do_action("plugin_installed", name)
            self._emit("plugin.installed", name, {"version": plugin_info.version})

            plugin_info.status = PluginStatus.INACTIVE
            logger.info(f"插件已安装: {name} v{plugin_info.version}")
            return True, f"插件 {name} 安装成功"

        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            # 回滚
            self._plugins.pop(name, None)
            self._instances.pop(name, None)
            self.dependency_resolver.unregister(name)
            logger.error(f"安装插件 {name} 失败: {e}")
            return False, f"安装失败: {e}"

    def uninstall(self, plugin_name: str, force: bool = False) -> Tuple[bool, str]:
        """卸载插件

        Args:
            plugin_name: 插件名称
            force: 是否强制卸载（忽略依赖）

        Returns:
            (是否成功, 消息)
        """
        if plugin_name not in self._plugins:
            return False, f"插件 {plugin_name} 未安装"

        # 检查是否有其他插件依赖它
        if not force:
            ok, dependents = self.dependency_resolver.can_uninstall(plugin_name)
            if not ok:
                return False, f"无法卸载，被以下插件依赖: {', '.join(dependents)}"

        plugin_info = self._plugins[plugin_name]

        try:
            # 先禁用
            if plugin_info.status == PluginStatus.ACTIVE:
                self.disable(plugin_name)

            # 调用插件实例的 uninstall 钩子
            instance = self._instances.get(plugin_name)
            if instance is not None:
                instance.uninstall()

            # 触发钩子和事件
            self.hook_manager.do_action(f"uninstall_{plugin_name}")
            self.hook_manager.do_action("plugin_uninstalled", plugin_name)
            self._emit("plugin.uninstalled", plugin_name)

            # 清理
            self._plugins.pop(plugin_name, None)
            self._instances.pop(plugin_name, None)
            self.metadata_store.delete(plugin_name)
            self.config_manager.remove_plugin(plugin_name)
            self.dependency_resolver.unregister(plugin_name)

            logger.info(f"插件已卸载: {plugin_name}")
            return True, f"插件 {plugin_name} 卸载成功"

        except Exception as e:
            logger.error(f"卸载插件 {plugin_name} 失败: {e}")
            return False, f"卸载失败: {e}"

    def enable(self, plugin_name: str) -> Tuple[bool, str]:
        """启用插件

        Returns:
            (是否成功, 消息)
        """
        if plugin_name not in self._plugins:
            return False, f"插件 {plugin_name} 未安装"

        plugin_info = self._plugins[plugin_name]
        if plugin_info.status == PluginStatus.ACTIVE:
            return True, f"插件 {plugin_name} 已是启用状态"

        try:
            # 调用插件实例的 enable 钩子
            instance = self._instances.get(plugin_name)
            if instance is not None:
                instance.enable()
                instance.register_hooks()

            # 触发钩子和事件
            self.hook_manager.do_action(f"enable_{plugin_name}")
            self.hook_manager.do_action("plugin_enabled", plugin_name)
            self._emit("plugin.enabled", plugin_name)

            plugin_info.status = PluginStatus.ACTIVE
            plugin_info.activated_at = time.time()

            logger.info(f"插件已启用: {plugin_name}")
            return True, f"插件 {plugin_name} 启用成功"

        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            logger.error(f"启用插件 {plugin_name} 失败: {e}")
            return False, f"启用失败: {e}"

    def disable(self, plugin_name: str) -> Tuple[bool, str]:
        """禁用插件

        Returns:
            (是否成功, 消息)
        """
        if plugin_name not in self._plugins:
            return False, f"插件 {plugin_name} 未安装"

        plugin_info = self._plugins[plugin_name]
        if plugin_info.status != PluginStatus.ACTIVE:
            return True, f"插件 {plugin_name} 已是禁用状态"

        try:
            # 调用插件实例的 disable 钩子
            instance = self._instances.get(plugin_name)
            if instance is not None:
                instance.disable()

            # 触发钩子和事件
            self.hook_manager.do_action(f"disable_{plugin_name}")
            self.hook_manager.do_action("plugin_disabled", plugin_name)
            self._emit("plugin.disabled", plugin_name)

            plugin_info.status = PluginStatus.INACTIVE
            plugin_info.activated_at = None

            logger.info(f"插件已禁用: {plugin_name}")
            return True, f"插件 {plugin_name} 禁用成功"

        except Exception as e:
            logger.error(f"禁用插件 {plugin_name} 失败: {e}")
            return False, f"禁用失败: {e}"

    def upgrade(self, plugin_name: str, new_version: str) -> Tuple[bool, str]:
        """升级插件

        Args:
            plugin_name: 插件名称
            new_version: 新版本号

        Returns:
            (是否成功, 消息)
        """
        if plugin_name not in self._plugins:
            return False, f"插件 {plugin_name} 未安装"

        plugin_info = self._plugins[plugin_name]
        old_version = plugin_info.version

        if old_version == new_version:
            return False, f"版本号相同 ({new_version})"

        was_active = plugin_info.status == PluginStatus.ACTIVE
        plugin_info.status = PluginStatus.UPDATING

        try:
            # 调用插件实例的 upgrade 钩子
            instance = self._instances.get(plugin_name)
            if instance is not None:
                instance.upgrade(old_version, new_version)
                instance.version = new_version

            # 更新版本
            plugin_info.version = new_version
            self.metadata_store.update_field(plugin_name, "version", new_version)

            # 触发钩子和事件
            self.hook_manager.do_action(f"upgrade_{plugin_name}", old_version, new_version)
            self.hook_manager.do_action("plugin_upgraded", plugin_name)
            self._emit("plugin.upgraded", plugin_name,
                       {"old_version": old_version, "new_version": new_version})

            # 恢复状态
            plugin_info.status = PluginStatus.ACTIVE if was_active else PluginStatus.INACTIVE

            logger.info(f"插件已升级: {plugin_name} {old_version} -> {new_version}")
            return True, f"插件 {plugin_name} 升级成功"

        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            logger.error(f"升级插件 {plugin_name} 失败: {e}")
            return False, f"升级失败: {e}"

    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        return self._plugins.get(plugin_name)

    def get_instance(self, plugin_name: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self._instances.get(plugin_name)

    def get_all_plugins(self) -> Dict[str, PluginInfo]:
        """获取所有插件"""
        return dict(self._plugins)

    def get_active_plugins(self) -> Dict[str, PluginInfo]:
        """获取所有启用的插件"""
        return {
            name: p for name, p in self._plugins.items()
            if p.status == PluginStatus.ACTIVE
        }

    def is_active(self, plugin_name: str) -> bool:
        """检查插件是否启用"""
        plugin = self._plugins.get(plugin_name)
        return plugin is not None and plugin.status == PluginStatus.ACTIVE

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._plugins)
        active = sum(1 for p in self._plugins.values() if p.status == PluginStatus.ACTIVE)
        inactive = sum(1 for p in self._plugins.values() if p.status == PluginStatus.INACTIVE)
        errors = sum(1 for p in self._plugins.values() if p.status == PluginStatus.ERROR)
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "errors": errors,
            "metadata_count": self.metadata_store.count(),
            "event_stats": self.event_bus.get_stats(),
        }


# 全局生命周期管理器实例
plugin_lifecycle_manager = PluginLifecycleManager(hook_manager)
plugin_event_bus = plugin_lifecycle_manager.event_bus
plugin_metadata_store = plugin_lifecycle_manager.metadata_store
plugin_config_manager = plugin_lifecycle_manager.config_manager
plugin_dependency_resolver = plugin_lifecycle_manager.dependency_resolver


# 异步方法供 Celery 任务调用
async def async_install_plugin(plugin_info: PluginInfo, instance: PluginBase = None,
                               dependencies: List[str] = None) -> Tuple[bool, str]:
    """异步安装插件"""
    return await asyncio.to_thread(
        plugin_lifecycle_manager.install, plugin_info, instance, dependencies
    )


async def async_uninstall_plugin(plugin_name: str, force: bool = False) -> Tuple[bool, str]:
    """异步卸载插件"""
    return await asyncio.to_thread(
        plugin_lifecycle_manager.uninstall, plugin_name, force
    )


async def async_enable_plugin(plugin_name: str) -> Tuple[bool, str]:
    """异步启用插件"""
    return await asyncio.to_thread(plugin_lifecycle_manager.enable, plugin_name)


async def async_disable_plugin(plugin_name: str) -> Tuple[bool, str]:
    """异步禁用插件"""
    return await asyncio.to_thread(plugin_lifecycle_manager.disable, plugin_name)


async def async_upgrade_plugin(plugin_name: str, new_version: str) -> Tuple[bool, str]:
    """异步升级插件"""
    return await asyncio.to_thread(
        plugin_lifecycle_manager.upgrade, plugin_name, new_version
    )


async def async_publish_event(event_name: str, data: Dict[str, Any] = None,
                              source: str = "") -> int:
    """异步发布事件"""
    return await asyncio.to_thread(
        plugin_event_bus.publish_simple, event_name, data or {}, source
    )
