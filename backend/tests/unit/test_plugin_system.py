"""
插件系统测试
"""
import os
import json
import asyncio
import tempfile
import shutil
import pytest
from app.services.plugin_system import (
    PluginManager,
    PluginBase,
    HookManager,
    PluginInfo,
    PluginStatus,
    HookType,
    hook_manager,
    plugin_manager,
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
    plugin_lifecycle_manager,
    plugin_event_bus,
    plugin_metadata_store,
    plugin_config_manager,
    plugin_dependency_resolver,
    async_install_plugin,
    async_uninstall_plugin,
    async_enable_plugin,
    async_disable_plugin,
    async_upgrade_plugin,
    async_publish_event,
)
from app.plugins import (
    SEOEnhancerPlugin,
    SecurityScannerPlugin,
    BUILTIN_PLUGINS,
)


class TestHookManager:
    """钩子管理器测试"""

    def test_hook_manager_creation(self):
        """测试钩子管理器创建"""
        hm = HookManager()
        assert hm is not None
        assert isinstance(hm._actions, dict)
        assert isinstance(hm._filters, dict)

    def test_add_action(self):
        """测试添加动作钩子"""
        hm = HookManager()

        def test_callback():
            return 'test'

        hm.add_action('test_action', test_callback)
        assert 'test_action' in hm._actions
        assert len(hm._actions['test_action']) == 1

    def test_add_filter(self):
        """测试添加过滤钩子"""
        hm = HookManager()

        def test_filter(value):
            return value.upper()

        hm.add_filter('test_filter', test_filter)
        assert 'test_filter' in hm._filters
        assert len(hm._filters['test_filter']) == 1

    def test_do_action(self):
        """测试执行动作钩子"""
        hm = HookManager()

        results = []

        def callback1():
            results.append('callback1')

        def callback2():
            results.append('callback2')

        hm.add_action('test_action', callback1)
        hm.add_action('test_action', callback2)
        hm.do_action('test_action')

        assert len(results) == 2
        assert 'callback1' in results
        assert 'callback2' in results

    def test_apply_filters(self):
        """测试应用过滤钩子"""
        hm = HookManager()

        def add_prefix(value):
            return 'prefix_' + value

        def add_suffix(value):
            return value + '_suffix'

        hm.add_filter('test_filter', add_prefix)
        hm.add_filter('test_filter', add_suffix)

        result = hm.apply_filters('test_filter', 'test')
        assert result == 'prefix_test_suffix'

    def test_remove_action(self):
        """测试移除动作钩子"""
        hm = HookManager()

        def callback():
            pass

        hm.add_action('test_action', callback)
        assert len(hm._actions['test_action']) == 1

        removed = hm.remove_action('test_action', callback)
        assert removed is True
        assert len(hm._actions['test_action']) == 0

    def test_remove_filter(self):
        """测试移除过滤钩子"""
        hm = HookManager()

        def filter_func(value):
            return value

        hm.add_filter('test_filter', filter_func)
        assert len(hm._filters['test_filter']) == 1

        removed = hm.remove_filter('test_filter', filter_func)
        assert removed is True
        assert len(hm._filters['test_filter']) == 0

    def test_hook_priority(self):
        """测试钩子优先级"""
        hm = HookManager()

        results = []

        def low_priority():
            results.append('low')

        def high_priority():
            results.append('high')

        hm.add_action('test_action', low_priority, priority=20)
        hm.add_action('test_action', high_priority, priority=10)
        hm.do_action('test_action')

        assert results[0] == 'high'
        assert results[1] == 'low'

    def test_has_action(self):
        """测试检查动作钩子"""
        hm = HookManager()

        assert not hm.has_action('test_action')

        def callback():
            pass

        hm.add_action('test_action', callback)
        assert hm.has_action('test_action')
        assert hm.has_action('test_action', callback)

    def test_has_filter(self):
        """测试检查过滤钩子"""
        hm = HookManager()

        assert not hm.has_filter('test_filter')

        def filter_func(value):
            return value

        hm.add_filter('test_filter', filter_func)
        assert hm.has_filter('test_filter')

    def test_did_action(self):
        """测试动作执行次数"""
        hm = HookManager()

        assert hm.did_action('test_action') == 0

        def callback():
            pass

        hm.add_action('test_action', callback)
        hm.do_action('test_action')
        assert hm.did_action('test_action') == 1

        hm.do_action('test_action')
        assert hm.did_action('test_action') == 2

    def test_doing_action(self):
        """测试正在执行动作"""
        hm = HookManager()
        assert hm.doing_action() is False

        in_hook_state = []

        def callback():
            in_hook_state.append(hm.doing_action())
            in_hook_state.append(hm.doing_action('test_action'))

        hm.add_action('test_action', callback)
        hm.do_action('test_action')
        assert in_hook_state[0] is True
        assert in_hook_state[1] is True

    def test_current_filter(self):
        """测试获取当前钩子"""
        hm = HookManager()
        assert hm.current_filter() is None

        captured = []

        def callback():
            captured.append(hm.current_filter())

        hm.add_action('test_action', callback)
        hm.do_action('test_action')
        assert captured[0] == 'test_action'

    def test_get_all_hooks(self):
        """测试获取所有钩子"""
        hm = HookManager()

        def cb():
            pass

        hm.add_action('action1', cb)
        hm.add_filter('filter1', cb)

        all_hooks = hm.get_all_hooks()
        assert isinstance(all_hooks, dict)
        assert 'actions' in all_hooks
        assert 'filters' in all_hooks
        assert 'action1' in all_hooks['actions']
        assert 'filter1' in all_hooks['filters']

    def test_get_hook_count(self):
        """测试钩子数量统计"""
        hm = HookManager()

        def cb():
            pass

        hm.add_action('action1', cb)
        hm.add_action('action1', cb)
        hm.add_filter('filter1', cb)

        counts = hm.get_hook_count()
        assert counts['actions'] == 2
        assert counts['filters'] == 1

    def test_global_hook_manager(self):
        """测试全局钩子管理器实例"""
        assert hook_manager is not None
        assert isinstance(hook_manager, HookManager)


class TestPluginBase:
    """插件基类测试"""

    def test_plugin_base_creation(self):
        """测试插件基类创建"""
        hm = HookManager()
        plugin = PluginBase(hm)
        assert plugin is not None
        assert plugin.hook_manager is hm

    def test_plugin_info(self):
        """测试插件信息"""
        class TestPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.name = "Test Plugin"
                self.version = "1.0.0"
                self.description = "A test plugin"
                self.author = "Test Author"

        hm = HookManager()
        plugin = TestPlugin(hm)
        assert plugin.name == "Test Plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "A test plugin"
        assert plugin.author == "Test Author"

    def test_plugin_activate(self):
        """测试插件激活"""
        class TestPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.activated = False

            def activate(self):
                self.activated = True

        hm = HookManager()
        plugin = TestPlugin(hm)
        plugin.activate()
        assert plugin.activated is True

    def test_plugin_deactivate(self):
        """测试插件停用"""
        class TestPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.deactivated = False

            def deactivate(self):
                self.deactivated = True

        hm = HookManager()
        plugin = TestPlugin(hm)
        plugin.deactivate()
        assert plugin.deactivated is True

    def test_plugin_uninstall(self):
        """测试插件卸载"""
        class TestPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.uninstalled = False

            def uninstall(self):
                self.uninstalled = True

        hm = HookManager()
        plugin = TestPlugin(hm)
        plugin.uninstall()
        assert plugin.uninstalled is True

    def test_plugin_register_hooks(self):
        """测试插件注册钩子"""
        class TestPlugin(PluginBase):
            pass

        hm = HookManager()
        plugin = TestPlugin(hm)
        # Should not raise
        plugin.register_hooks()

    def test_plugin_get_info(self):
        """测试获取插件信息"""
        class TestPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.name = "Test Plugin"
                self.version = "1.0.0"
                self.description = "Test description"
                self.author = "Test Author"

        hm = HookManager()
        plugin = TestPlugin(hm)
        info = plugin.get_info()
        assert isinstance(info, PluginInfo)
        assert info.name == "Test Plugin"
        assert info.version == "1.0.0"


class TestPluginManager:
    """插件管理器测试"""

    def test_plugin_manager_creation(self):
        """测试插件管理器创建"""
        hm = HookManager()
        pm = PluginManager(hm)
        assert pm is not None
        assert isinstance(pm._plugins, dict)
        assert pm.hook_manager is hm

    def test_register_plugin(self):
        """测试注册插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        plugin_info = PluginInfo(
            name="Test Plugin",
            version="1.0.0",
            description="A test plugin",
        )
        pm.register_plugin(plugin_info)

        assert "Test Plugin" in pm._plugins
        assert pm._plugins["Test Plugin"].name == "Test Plugin"

    def test_activate_plugin(self):
        """测试激活插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        plugin_info = PluginInfo(name="Test Plugin", version="1.0.0")
        pm.register_plugin(plugin_info)

        result = pm.activate_plugin("Test Plugin")
        assert result is True
        assert pm._plugins["Test Plugin"].status == PluginStatus.ACTIVE
        assert pm._plugins["Test Plugin"].activated_at is not None

    def test_activate_plugin_already_active(self):
        """测试激活已激活的插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        plugin_info = PluginInfo(name="Test Plugin", version="1.0.0")
        pm.register_plugin(plugin_info)
        pm.activate_plugin("Test Plugin")

        result = pm.activate_plugin("Test Plugin")
        assert result is True

    def test_activate_plugin_not_found(self):
        """测试激活不存在的插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        result = pm.activate_plugin("NonExistent")
        assert result is False

    def test_deactivate_plugin(self):
        """测试停用插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        plugin_info = PluginInfo(name="Test Plugin", version="1.0.0")
        pm.register_plugin(plugin_info)
        pm.activate_plugin("Test Plugin")

        result = pm.deactivate_plugin("Test Plugin")
        assert result is True
        assert pm._plugins["Test Plugin"].status == PluginStatus.INACTIVE
        assert pm._plugins["Test Plugin"].activated_at is None

    def test_deactivate_plugin_not_active(self):
        """测试停用未激活的插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        plugin_info = PluginInfo(name="Test Plugin", version="1.0.0")
        pm.register_plugin(plugin_info)

        result = pm.deactivate_plugin("Test Plugin")
        assert result is True

    def test_deactivate_plugin_not_found(self):
        """测试停用不存在的插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        result = pm.deactivate_plugin("NonExistent")
        assert result is False

    def test_get_plugin(self):
        """测试获取插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        plugin_info = PluginInfo(name="Test Plugin", version="1.0.0")
        pm.register_plugin(plugin_info)

        result = pm.get_plugin("Test Plugin")
        assert result is not None
        assert result.name == "Test Plugin"

    def test_get_plugin_not_found(self):
        """测试获取不存在的插件"""
        hm = HookManager()
        pm = PluginManager(hm)
        result = pm.get_plugin("NonExistent")
        assert result is None

    def test_get_all_plugins(self):
        """测试获取所有插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Plugin 1", version="1.0.0"))
        pm.register_plugin(PluginInfo(name="Plugin 2", version="1.0.0"))

        plugins = pm.get_all_plugins()
        assert isinstance(plugins, dict)
        assert len(plugins) == 2
        assert "Plugin 1" in plugins
        assert "Plugin 2" in plugins

    def test_get_active_plugins(self):
        """测试获取激活的插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Plugin 1", version="1.0.0"))
        pm.register_plugin(PluginInfo(name="Plugin 2", version="1.0.0"))
        pm.activate_plugin("Plugin 1")

        active = pm.get_active_plugins()
        assert isinstance(active, dict)
        assert len(active) == 1
        assert "Plugin 1" in active

    def test_is_plugin_active(self):
        """测试检查插件是否激活"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Test Plugin", version="1.0.0"))

        assert pm.is_plugin_active("Test Plugin") is False
        pm.activate_plugin("Test Plugin")
        assert pm.is_plugin_active("Test Plugin") is True

    def test_is_plugin_active_not_found(self):
        """测试检查不存在插件是否激活"""
        hm = HookManager()
        pm = PluginManager(hm)
        assert pm.is_plugin_active("NonExistent") is False

    def test_install_plugin(self):
        """测试安装插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        result = pm.install_plugin("test-plugin", {
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author",
        })
        assert result is True
        assert "test-plugin" in pm._plugins
        assert pm._plugins["test-plugin"].installed_at is not None

    def test_uninstall_plugin(self):
        """测试卸载插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Test Plugin", version="1.0.0"))
        result = pm.uninstall_plugin("Test Plugin")
        assert result is True
        assert "Test Plugin" not in pm._plugins

    def test_uninstall_plugin_not_found(self):
        """测试卸载不存在的插件"""
        hm = HookManager()
        pm = PluginManager(hm)
        result = pm.uninstall_plugin("NonExistent")
        assert result is False

    def test_uninstall_active_plugin(self):
        """测试卸载已激活的插件"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Test Plugin", version="1.0.0"))
        pm.activate_plugin("Test Plugin")
        result = pm.uninstall_plugin("Test Plugin")
        assert result is True
        assert "Test Plugin" not in pm._plugins

    def test_get_plugin_instance(self):
        """测试获取插件实例"""
        hm = HookManager()
        pm = PluginManager(hm)

        class FakeInstance:
            pass

        instance = FakeInstance()
        pm.register_plugin(
            PluginInfo(name="Test Plugin", version="1.0.0"),
            plugin_instance=instance,
        )

        result = pm.get_plugin_instance("Test Plugin")
        assert result is instance

    def test_update_plugin_settings(self):
        """测试更新插件设置"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Test Plugin", version="1.0.0"))
        result = pm.update_plugin_settings("Test Plugin", {"key": "value"})
        assert result is True
        assert pm._plugins["Test Plugin"].settings.get("key") == "value"

    def test_update_plugin_settings_not_found(self):
        """测试更新不存在插件的设置"""
        hm = HookManager()
        pm = PluginManager(hm)
        result = pm.update_plugin_settings("NonExistent", {"key": "value"})
        assert result is False

    def test_get_plugin_stats(self):
        """测试获取插件统计"""
        hm = HookManager()
        pm = PluginManager(hm)

        pm.register_plugin(PluginInfo(name="Plugin 1", version="1.0.0"))
        pm.register_plugin(PluginInfo(name="Plugin 2", version="1.0.0"))
        pm.activate_plugin("Plugin 1")

        stats = pm.get_plugin_stats()
        assert isinstance(stats, dict)
        assert stats["total"] == 2
        assert stats["active"] == 1
        assert stats["inactive"] == 1
        assert stats["errors"] == 0

    def test_global_plugin_manager(self):
        """测试全局插件管理器实例"""
        assert plugin_manager is not None
        assert isinstance(plugin_manager, PluginManager)


class TestPluginInfo:
    """插件信息测试"""

    def test_plugin_info_creation(self):
        """测试插件信息创建"""
        info = PluginInfo(name="Test Plugin")
        assert info.name == "Test Plugin"
        assert info.version == "1.0.0"
        assert info.status == PluginStatus.INACTIVE
        assert info.hooks == []
        assert info.filters == []
        assert info.settings == {}

    def test_plugin_info_with_all_fields(self):
        """测试带所有字段的插件信息"""
        info = PluginInfo(
            name="Test Plugin",
            version="2.0.0",
            description="A test plugin",
            author="Test Author",
            author_url="https://example.com",
            plugin_url="https://example.com/plugin",
            requires="1.0.0",
            tested="2.0.0",
            license="MIT",
            text_domain="test-plugin",
            domain_path="/languages",
        )
        assert info.name == "Test Plugin"
        assert info.version == "2.0.0"
        assert info.description == "A test plugin"
        assert info.author == "Test Author"
        assert info.license == "MIT"

    def test_plugin_status_enum(self):
        """测试插件状态枚举"""
        assert PluginStatus.ACTIVE == "active"
        assert PluginStatus.INACTIVE == "inactive"
        assert PluginStatus.ERROR == "error"
        assert PluginStatus.INSTALLING == "installing"
        assert PluginStatus.UPDATING == "updating"

    def test_hook_type_enum(self):
        """测试钩子类型枚举"""
        assert HookType.ACTION == "action"
        assert HookType.FILTER == "filter"


# ===========================================================================
# 任务3：插件化架构完善 - 新增测试
# ===========================================================================


class TestPluginEventType:
    """插件事件类型枚举测试"""

    def test_event_type_values(self):
        assert PluginEventType.CUSTOM.value == "custom"
        assert PluginEventType.LIFECYCLE.value == "lifecycle"
        assert PluginEventType.SYSTEM.value == "system"

    def test_event_type_is_str_enum(self):
        assert isinstance(PluginEventType.CUSTOM, str)


class TestPluginEvent:
    """插件事件数据类测试"""

    def test_event_defaults(self):
        event = PluginEvent(name="test.event")
        assert event.name == "test.event"
        assert event.data == {}
        assert event.event_type == PluginEventType.CUSTOM
        assert event.timestamp > 0
        assert event.source == ""

    def test_event_with_data(self):
        event = PluginEvent(
            name="plugin.installed",
            data={"version": "1.0.0"},
            source="seo_enhancer",
            event_type=PluginEventType.LIFECYCLE,
        )
        assert event.data == {"version": "1.0.0"}
        assert event.source == "seo_enhancer"
        assert event.event_type == PluginEventType.LIFECYCLE


class TestPluginEventBus:
    """插件事件总线测试"""

    def test_subscribe_and_publish(self):
        bus = PluginEventBus()
        received = []
        bus.subscribe("test.event", lambda e: received.append(e))
        count = bus.publish_simple("test.event", {"key": "value"})
        assert count == 1
        assert len(received) == 1
        assert received[0].data == {"key": "value"}

    def test_subscribe_priority(self):
        bus = PluginEventBus()
        order = []
        bus.subscribe("evt", lambda e: order.append("low"), priority=20)
        bus.subscribe("evt", lambda e: order.append("high"), priority=10)
        bus.publish_simple("evt")
        assert order == ["high", "low"]

    def test_unsubscribe(self):
        bus = PluginEventBus()
        calls = []

        def cb(e):
            calls.append(e)

        bus.subscribe("evt", cb)
        assert bus.unsubscribe("evt", cb) is True
        bus.publish_simple("evt")
        assert len(calls) == 0

    def test_unsubscribe_not_found(self):
        bus = PluginEventBus()
        assert bus.unsubscribe("nonexistent", lambda e: None) is False

    def test_publish_no_listeners(self):
        bus = PluginEventBus()
        count = bus.publish_simple("no.listeners")
        assert count == 0

    def test_listener_exception_isolated(self):
        bus = PluginEventBus()
        called = []

        def bad_cb(e):
            raise ValueError("boom")

        def good_cb(e):
            called.append("ok")

        bus.subscribe("evt", bad_cb, priority=10)
        bus.subscribe("evt", good_cb, priority=20)
        count = bus.publish_simple("evt")
        # bad_cb 抛异常不计入成功，good_cb 成功
        assert count == 1
        assert called == ["ok"]

    def test_event_history(self):
        bus = PluginEventBus()
        bus.publish_simple("evt1")
        bus.publish_simple("evt2")
        bus.publish_simple("evt1")
        history = bus.get_event_history()
        assert len(history) == 3
        evt1_history = bus.get_event_history("evt1")
        assert len(evt1_history) == 2

    def test_clear_history(self):
        bus = PluginEventBus()
        bus.publish_simple("evt")
        bus.clear_history()
        assert len(bus.get_event_history()) == 0

    def test_clear_listeners(self):
        bus = PluginEventBus()
        bus.subscribe("evt", lambda e: None)
        bus.clear_listeners("evt")
        assert bus.has_listeners("evt") is False

    def test_clear_all_listeners(self):
        bus = PluginEventBus()
        bus.subscribe("evt1", lambda e: None)
        bus.subscribe("evt2", lambda e: None)
        bus.clear_listeners()
        assert bus.get_stats()["event_types"] == 0

    def test_has_listeners(self):
        bus = PluginEventBus()
        assert bus.has_listeners("evt") is False
        bus.subscribe("evt", lambda e: None)
        assert bus.has_listeners("evt") is True

    def test_get_listeners(self):
        bus = PluginEventBus()
        cb = lambda e: None
        bus.subscribe("evt", cb)
        listeners = bus.get_listeners("evt")
        assert len(listeners) == 1
        assert listeners[0]["callback"] == cb

    def test_get_stats(self):
        bus = PluginEventBus()
        bus.subscribe("evt1", lambda e: None)
        bus.subscribe("evt1", lambda e: None)
        bus.publish_simple("evt1")
        stats = bus.get_stats()
        assert stats["event_types"] == 1
        assert stats["total_listeners"] == 2
        assert stats["history_count"] == 1

    def test_history_limit(self):
        bus = PluginEventBus()
        bus._max_history = 5
        for i in range(10):
            bus.publish_simple("evt")
        assert len(bus.get_event_history()) == 5


class TestPluginMetadataStore:
    """插件元数据存储测试"""

    def test_save_and_load(self):
        store = PluginMetadataStore()
        store.save("test-plugin", {"version": "1.0.0", "author": "tester"})
        loaded = store.load("test-plugin")
        assert loaded == {"version": "1.0.0", "author": "tester"}

    def test_load_not_found(self):
        store = PluginMetadataStore()
        assert store.load("nonexistent") is None

    def test_delete(self):
        store = PluginMetadataStore()
        store.save("p1", {"v": 1})
        assert store.delete("p1") is True
        assert store.exists("p1") is False

    def test_delete_not_found(self):
        store = PluginMetadataStore()
        assert store.delete("nonexistent") is False

    def test_exists(self):
        store = PluginMetadataStore()
        assert store.exists("p1") is False
        store.save("p1", {})
        assert store.exists("p1") is True

    def test_list_all(self):
        store = PluginMetadataStore()
        store.save("p1", {"v": 1})
        store.save("p2", {"v": 2})
        all_meta = store.list_all()
        assert len(all_meta) == 2
        assert "p1" in all_meta
        assert "p2" in all_meta

    def test_update_field(self):
        store = PluginMetadataStore()
        store.save("p1", {"version": "1.0.0"})
        assert store.update_field("p1", "version", "2.0.0") is True
        assert store.load("p1")["version"] == "2.0.0"

    def test_update_field_not_found(self):
        store = PluginMetadataStore()
        assert store.update_field("nonexistent", "k", "v") is False

    def test_count(self):
        store = PluginMetadataStore()
        assert store.count() == 0
        store.save("p1", {})
        store.save("p2", {})
        assert store.count() == 2

    def test_load_returns_copy(self):
        store = PluginMetadataStore()
        store.save("p1", {"v": 1})
        loaded = store.load("p1")
        loaded["v"] = 999
        assert store.load("p1")["v"] == 1


class TestPluginConfigField:
    """插件配置字段测试"""

    def test_field_defaults(self):
        field = PluginConfigField(key="test")
        assert field.key == "test"
        assert field.field_type == "string"
        assert field.default is None
        assert field.options == []
        assert field.required is False

    def test_field_full(self):
        field = PluginConfigField(
            key="level",
            label="级别",
            field_type="select",
            default="standard",
            options=["basic", "standard", "aggressive"],
            description="优化级别",
            required=True,
        )
        assert field.label == "级别"
        assert field.options == ["basic", "standard", "aggressive"]
        assert field.required is True


class TestPluginConfigManager:
    """插件配置管理器测试"""

    def _make_schema(self):
        return [
            PluginConfigField(key="name", field_type="string", default="test"),
            PluginConfigField(key="count", field_type="int", default=10, min_value=1, max_value=100),
            PluginConfigField(key="enabled", field_type="bool", default=True),
            PluginConfigField(key="level", field_type="select", default="basic",
                              options=["basic", "standard", "advanced"]),
        ]

    def test_register_schema(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        assert cm.has_schema("p1") is True
        assert len(cm.get_schema("p1")) == 4

    def test_default_values_initialized(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        values = cm.get_all_values("p1")
        assert values["name"] == "test"
        assert values["count"] == 10
        assert values["enabled"] is True

    def test_set_value(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        assert cm.set_value("p1", "count", "50") is True
        assert cm.get_value("p1", "count") == 50

    def test_set_value_int_validation(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        # 超出范围
        assert cm.set_value("p1", "count", 200) is False
        # 非数字
        assert cm.set_value("p1", "count", "abc") is False

    def test_set_value_bool(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        assert cm.set_value("p1", "enabled", "false") is True
        assert cm.get_value("p1", "enabled") is False
        assert cm.set_value("p1", "enabled", "yes") is True
        assert cm.get_value("p1", "enabled") is True

    def test_set_value_select(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        assert cm.set_value("p1", "level", "advanced") is True
        assert cm.get_value("p1", "level") == "advanced"
        # 不在选项中
        assert cm.set_value("p1", "level", "invalid") is False

    def test_set_value_unknown_field(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        assert cm.set_value("p1", "unknown", "x") is False

    def test_set_value_unknown_plugin(self):
        cm = PluginConfigManager()
        assert cm.set_value("nonexistent", "k", "v") is False

    def test_set_values_batch(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        ok, failed = cm.set_values("p1", {"count": 20, "name": "hello"})
        assert ok is True
        assert failed == []

    def test_set_values_batch_partial_failure(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        ok, failed = cm.set_values("p1", {"count": 20, "unknown": "x"})
        assert ok is False
        assert "unknown" in failed

    def test_get_config_page(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        page = cm.get_config_page("p1")
        assert page["plugin"] == "p1"
        assert len(page["fields"]) == 4
        assert page["fields"][0]["key"] == "name"
        assert page["fields"][0]["value"] == "test"

    def test_reset_to_defaults(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        cm.set_value("p1", "count", 50)
        cm.reset_to_defaults("p1")
        assert cm.get_value("p1", "count") == 10

    def test_reset_unknown_plugin(self):
        cm = PluginConfigManager()
        assert cm.reset_to_defaults("nonexistent") is False

    def test_remove_plugin(self):
        cm = PluginConfigManager()
        cm.register_schema("p1", self._make_schema())
        assert cm.remove_plugin("p1") is True
        assert cm.has_schema("p1") is False

    def test_remove_plugin_not_found(self):
        cm = PluginConfigManager()
        assert cm.remove_plugin("nonexistent") is False

    def test_get_value_with_default(self):
        cm = PluginConfigManager()
        assert cm.get_value("p1", "missing", "fallback") == "fallback"


class TestDependencyResolver:
    """插件依赖管理器测试"""

    def test_register_and_get(self):
        dr = DependencyResolver()
        dr.register("plugin_a", ["plugin_b", "plugin_c"])
        deps = dr.get_dependencies("plugin_a")
        assert deps == ["plugin_b", "plugin_c"]

    def test_get_dependencies_empty(self):
        dr = DependencyResolver()
        assert dr.get_dependencies("nonexistent") == []

    def test_check_dependencies_satisfied(self):
        dr = DependencyResolver()
        dr.register("plugin_a", ["plugin_b"])
        ok, missing = dr.check_dependencies("plugin_a", {"plugin_b"})
        assert ok is True
        assert missing == []

    def test_check_dependencies_missing(self):
        dr = DependencyResolver()
        dr.register("plugin_a", ["plugin_b", "plugin_c"])
        ok, missing = dr.check_dependencies("plugin_a", {"plugin_b"})
        assert ok is False
        assert "plugin_c" in missing

    def test_get_all_dependencies_recursive(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        dr.register("b", ["c"])
        all_deps = dr.get_all_dependencies("a")
        assert "b" in all_deps
        assert "c" in all_deps

    def test_detect_cycle_no_cycle(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        dr.register("b", ["c"])
        assert dr.detect_cycle("a") is False

    def test_detect_cycle_with_cycle(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        dr.register("b", ["c"])
        dr.register("c", ["a"])
        assert dr.detect_cycle("a") is True

    def test_topological_sort(self):
        dr = DependencyResolver()
        dr.register("a", ["b", "c"])
        dr.register("b", ["c"])
        sorted_list = dr.topological_sort(["a", "b", "c"])
        # c 应该在 b 和 a 之前
        assert sorted_list.index("c") < sorted_list.index("b")
        assert sorted_list.index("c") < sorted_list.index("a")
        assert sorted_list.index("b") < sorted_list.index("a")

    def test_get_dependents(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        dr.register("c", ["b"])
        dependents = dr.get_dependents("b")
        assert "a" in dependents
        assert "c" in dependents

    def test_can_uninstall_no_dependents(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        ok, deps = dr.can_uninstall("b")
        assert ok is False
        assert "a" in deps

    def test_can_uninstall_ok(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        ok, deps = dr.can_uninstall("a")
        assert ok is True
        assert deps == []

    def test_unregister(self):
        dr = DependencyResolver()
        dr.register("a", ["b"])
        dr.unregister("a")
        assert dr.get_dependencies("a") == []


class TestMarketplacePlugin:
    """市场插件数据类测试"""

    def test_defaults(self):
        mp = MarketplacePlugin(name="Test", slug="test")
        assert mp.name == "Test"
        assert mp.slug == "test"
        assert mp.version == "1.0.0"
        assert mp.tags == []
        assert mp.rating == 0.0
        assert mp.downloads == 0

    def test_full(self):
        mp = MarketplacePlugin(
            name="Test", slug="test", version="2.0.0",
            category="seo", tags=["seo", "marketing"], rating=4.5,
        )
        assert mp.category == "seo"
        assert mp.rating == 4.5
        assert "seo" in mp.tags


class TestPluginMarketplace:
    """插件市场测试"""

    def test_scan_local_empty_dir(self):
        mp = PluginMarketplace(local_dir="/nonexistent/path")
        assert mp.scan_local() == []

    def test_scan_local_with_plugins(self, tmp_path):
        # 创建插件目录与 manifest
        plugin_dir = tmp_path / "my-plugin"
        plugin_dir.mkdir()
        manifest = {"name": "My Plugin", "slug": "my-plugin", "version": "1.2.0",
                    "description": "A test", "author": "Tester", "category": "seo",
                    "tags": ["seo"]}
        (plugin_dir / "plugin.json").write_text(json.dumps(manifest), encoding="utf-8")

        mp = PluginMarketplace(local_dir=str(tmp_path))
        plugins = mp.scan_local()
        assert len(plugins) == 1
        assert plugins[0].name == "My Plugin"
        assert plugins[0].version == "1.2.0"
        assert plugins[0].category == "seo"

    def test_scan_local_invalid_json(self, tmp_path):
        plugin_dir = tmp_path / "bad-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text("not json{", encoding="utf-8")
        mp = PluginMarketplace(local_dir=str(tmp_path))
        plugins = mp.scan_local()
        assert plugins == []

    def test_fetch_remote_with_fetcher(self):
        mp = PluginMarketplace(remote_url="https://example.com/api")
        data = [
            {"name": "Remote1", "slug": "remote1", "version": "1.0.0", "rating": 4.0, "downloads": 100},
            {"name": "Remote2", "slug": "remote2", "version": "2.0.0"},
        ]
        plugins = mp.fetch_remote(fetcher=lambda: data)
        assert len(plugins) == 2
        assert plugins[0].name == "Remote1"
        assert plugins[0].rating == 4.0
        assert plugins[0].downloads == 100

    def test_fetch_remote_no_fetcher(self):
        mp = PluginMarketplace()
        assert mp.fetch_remote() == []

    def test_fetch_remote_error(self):
        def bad_fetcher():
            raise ConnectionError("network down")

        mp = PluginMarketplace()
        assert mp.fetch_remote(fetcher=bad_fetcher) == []

    def test_search(self):
        mp = PluginMarketplace()
        mp._remote_cache["p1"] = MarketplacePlugin(name="SEO Tool", slug="seo-tool",
                                                    description="SEO optimization", tags=["seo"])
        mp._remote_cache["p2"] = MarketplacePlugin(name="Cache", slug="cache",
                                                    description="Caching plugin", tags=["performance"])
        results = mp.search("seo")
        assert len(results) == 1
        assert results[0].slug == "seo-tool"

    def test_get_plugin(self):
        mp = PluginMarketplace()
        mp._local_cache["local1"] = MarketplacePlugin(name="Local", slug="local1")
        mp._remote_cache["remote1"] = MarketplacePlugin(name="Remote", slug="remote1")
        assert mp.get_plugin("local1").name == "Local"
        assert mp.get_plugin("remote1").name == "Remote"
        assert mp.get_plugin("nonexistent") is None

    def test_get_categories(self):
        mp = PluginMarketplace()
        mp._local_cache["p1"] = MarketplacePlugin(name="P1", slug="p1", category="seo")
        mp._remote_cache["p2"] = MarketplacePlugin(name="P2", slug="p2", category="seo")
        mp._remote_cache["p3"] = MarketplacePlugin(name="P3", slug="p3", category="security")
        cats = mp.get_categories()
        assert cats["seo"] == 2
        assert cats["security"] == 1

    def test_clear_cache(self):
        mp = PluginMarketplace()
        mp._local_cache["p1"] = MarketplacePlugin(name="P1", slug="p1")
        mp._remote_cache["p2"] = MarketplacePlugin(name="P2", slug="p2")
        mp.clear_cache()
        assert mp.get_local_plugins() == []
        assert mp.get_remote_plugins() == []


class TestPluginLifecycleManager:
    """插件生命周期管理器测试"""

    def _make_manager(self):
        hm = HookManager()
        return PluginLifecycleManager(hm)

    def test_install_plugin(self):
        mgr = self._make_manager()
        info = PluginInfo(name="test-plugin", version="1.0.0")
        ok, msg = mgr.install(info)
        assert ok is True
        assert mgr.get_plugin("test-plugin") is not None
        assert mgr.metadata_store.exists("test-plugin") is True

    def test_install_duplicate(self):
        mgr = self._make_manager()
        info = PluginInfo(name="test-plugin", version="1.0.0")
        mgr.install(info)
        ok, msg = mgr.install(PluginInfo(name="test-plugin"))
        assert ok is False
        assert "已安装" in msg

    def test_install_with_missing_dependency(self):
        mgr = self._make_manager()
        info = PluginInfo(name="dependent", version="1.0.0")
        ok, msg = mgr.install(info, dependencies=["missing-plugin"])
        assert ok is False
        assert "缺少依赖" in msg

    def test_install_with_satisfied_dependency(self):
        mgr = self._make_manager()
        # 先安装依赖
        mgr.install(PluginInfo(name="base-plugin", version="1.0.0"))
        # 再安装依赖它的插件
        ok, msg = mgr.install(
            PluginInfo(name="dependent-plugin", version="1.0.0"),
            dependencies=["base-plugin"],
        )
        assert ok is True

    def test_enable_plugin(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        ok, msg = mgr.enable("test-plugin")
        assert ok is True
        assert mgr.is_active("test-plugin") is True

    def test_enable_already_active(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        mgr.enable("test-plugin")
        ok, msg = mgr.enable("test-plugin")
        assert ok is True
        assert "已是启用" in msg

    def test_enable_not_installed(self):
        mgr = self._make_manager()
        ok, msg = mgr.enable("nonexistent")
        assert ok is False

    def test_disable_plugin(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        mgr.enable("test-plugin")
        ok, msg = mgr.disable("test-plugin")
        assert ok is True
        assert mgr.is_active("test-plugin") is False

    def test_disable_already_inactive(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        ok, msg = mgr.disable("test-plugin")
        assert ok is True
        assert "已是禁用" in msg

    def test_uninstall_plugin(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        ok, msg = mgr.uninstall("test-plugin")
        assert ok is True
        assert mgr.get_plugin("test-plugin") is None
        assert mgr.metadata_store.exists("test-plugin") is False

    def test_uninstall_not_installed(self):
        mgr = self._make_manager()
        ok, msg = mgr.uninstall("nonexistent")
        assert ok is False

    def test_uninstall_active_plugin(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        mgr.enable("test-plugin")
        ok, msg = mgr.uninstall("test-plugin")
        assert ok is True

    def test_uninstall_with_dependent(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="base", version="1.0.0"))
        mgr.install(PluginInfo(name="dependent", version="1.0.0"), dependencies=["base"])
        # base 被 dependent 依赖，不能卸载
        ok, msg = mgr.uninstall("base")
        assert ok is False
        assert "依赖" in msg
        # 强制卸载
        ok, msg = mgr.uninstall("base", force=True)
        assert ok is True

    def test_upgrade_plugin(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        ok, msg = mgr.upgrade("test-plugin", "2.0.0")
        assert ok is True
        assert mgr.get_plugin("test-plugin").version == "2.0.0"
        assert mgr.metadata_store.load("test-plugin")["version"] == "2.0.0"

    def test_upgrade_same_version(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="test-plugin", version="1.0.0"))
        ok, msg = mgr.upgrade("test-plugin", "1.0.0")
        assert ok is False
        assert "相同" in msg

    def test_upgrade_not_installed(self):
        mgr = self._make_manager()
        ok, msg = mgr.upgrade("nonexistent", "2.0.0")
        assert ok is False

    def test_lifecycle_events_emitted(self):
        mgr = self._make_manager()
        events = []
        mgr.event_bus.subscribe("plugin.installed", lambda e: events.append(e.name))
        mgr.event_bus.subscribe("plugin.enabled", lambda e: events.append(e.name))
        mgr.event_bus.subscribe("plugin.disabled", lambda e: events.append(e.name))
        mgr.event_bus.subscribe("plugin.uninstalled", lambda e: events.append(e.name))

        mgr.install(PluginInfo(name="p1", version="1.0.0"))
        mgr.enable("p1")
        mgr.disable("p1")
        mgr.uninstall("p1")
        assert events == ["plugin.installed", "plugin.enabled", "plugin.disabled", "plugin.uninstalled"]

    def test_install_with_instance_hooks(self):
        mgr = self._make_manager()
        instance = SEOEnhancerPlugin(mgr.hook_manager)
        info = instance.get_info()
        ok, msg = mgr.install(info, instance=instance)
        assert ok is True
        assert instance.installed is True
        assert mgr.get_instance(info.name) is instance

    def test_enable_with_instance_registers_hooks(self):
        mgr = self._make_manager()
        instance = SEOEnhancerPlugin(mgr.hook_manager)
        info = instance.get_info()
        mgr.install(info, instance=instance)
        mgr.enable(info.name)
        # 启用后应注册了 the_title 过滤器
        assert mgr.hook_manager.has_filter("the_title") is True

    def test_get_stats(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="p1", version="1.0.0"))
        mgr.install(PluginInfo(name="p2", version="1.0.0"))
        mgr.enable("p1")
        stats = mgr.get_stats()
        assert stats["total"] == 2
        assert stats["active"] == 1
        assert stats["inactive"] == 1
        assert stats["metadata_count"] == 2

    def test_get_active_plugins(self):
        mgr = self._make_manager()
        mgr.install(PluginInfo(name="p1", version="1.0.0"))
        mgr.install(PluginInfo(name="p2", version="1.0.0"))
        mgr.enable("p1")
        active = mgr.get_active_plugins()
        assert "p1" in active
        assert "p2" not in active


class TestSEOEnhancerPlugin:
    """SEO增强插件测试"""

    def test_plugin_info(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        info = plugin.get_info()
        assert info.name == "SEO增强"
        assert info.version == "1.0.0"
        assert "the_title" in info.filters

    def test_lifecycle_hooks(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        plugin.install()
        assert plugin.installed is True
        plugin.enable()
        assert plugin.enabled is True
        plugin.disable()
        assert plugin.enabled is False
        plugin.uninstall()
        assert plugin.installed is False

    def test_optimize_title_long(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        plugin.enable()
        long_title = "A" * 100
        optimized = plugin.optimize_title(long_title)
        assert len(optimized) <= 60
        assert optimized.endswith("...")

    def test_optimize_title_short(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        plugin.enable()
        short_title = "Short Title"
        assert plugin.optimize_title(short_title) == "Short Title"

    def test_optimize_title_disabled(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        # 未启用，不优化
        long_title = "A" * 100
        assert plugin.optimize_title(long_title) == long_title

    def test_optimize_content(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        plugin.enable()
        content = "line1\n\n\nline2\n  line3  \n"
        optimized = plugin.optimize_content(content)
        assert "\n\n" not in optimized
        assert "line1" in optimized

    def test_seo_score_high(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        result = plugin.get_seo_score(
            content="A" * 500,
            title="A good title for SEO testing",
            meta_description="A" * 100,
        )
        assert result["score"] >= 80
        assert result["level"] == "优秀"

    def test_seo_score_low(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        result = plugin.get_seo_score(
            content="short",
            title="x",
        )
        assert result["score"] < 60
        assert result["level"] == "需改进"

    def test_seo_score_checks_structure(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        result = plugin.get_seo_score(content="content", title="title", meta_description="desc")
        assert "checks" in result
        assert isinstance(result["checks"], list)
        assert len(result["checks"]) > 0

    def test_config_schema(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        schema = plugin.get_config_schema()
        assert len(schema) == 4
        keys = [f.key for f in schema]
        assert "auto_optimize" in keys
        assert "max_title_length" in keys
        assert "optimization_level" in keys

    def test_register_hooks(self):
        hm = HookManager()
        plugin = SEOEnhancerPlugin(hm)
        plugin.register_hooks()
        assert hm.has_filter("the_title") is True
        assert hm.has_filter("the_content") is True


class TestSecurityScannerPlugin:
    """安全扫描插件测试"""

    def test_plugin_info(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        info = plugin.get_info()
        assert info.name == "安全扫描"
        assert "site_created" in info.hooks
        assert "the_content" in info.filters

    def test_lifecycle_hooks(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        plugin.install()
        assert plugin.installed is True
        plugin.enable()
        assert plugin.enabled is True
        plugin.disable()
        assert plugin.enabled is False
        plugin.uninstall()
        assert plugin.installed is False

    def test_scan_clean_content(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        result = plugin.scan_content("This is clean content with no issues.")
        assert result["passed"] is True
        assert result["risk_level"] == "low"
        assert result["issue_count"] == 0

    def test_scan_xss_content(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        result = plugin.scan_content("Hello <script>alert(1)</script> world")
        assert result["passed"] is False
        assert result["risk_level"] == "high"
        assert result["issue_count"] > 0
        xss_issues = [i for i in result["issues"] if i["type"] == "xss"]
        assert len(xss_issues) > 0

    def test_scan_sensitive_info(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        result = plugin.scan_content("The password is hidden here")
        assert result["passed"] is False
        assert result["risk_level"] == "medium"
        sensitive_issues = [i for i in result["issues"] if i["type"] == "sensitive_info"]
        assert len(sensitive_issues) > 0

    def test_scan_batch(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        results = plugin.scan_batch(["clean", "<script>bad</script>"])
        assert len(results) == 2
        assert results[0]["passed"] is True
        assert results[1]["passed"] is False

    def test_scan_history(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        plugin.scan_content("clean")
        plugin.scan_content("<script>bad</script>")
        history = plugin.get_scan_history()
        assert len(history) == 2

    def test_scan_history_limit(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        for i in range(5):
            plugin.scan_content(f"content {i}")
        history = plugin.get_scan_history(limit=2)
        assert len(history) == 2

    def test_security_summary(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        plugin.scan_content("clean")
        plugin.scan_content("<script>bad</script>")
        summary = plugin.get_security_summary()
        assert summary["total_scans"] == 2
        assert summary["passed_scans"] == 1
        assert summary["failed_scans"] == 1
        assert summary["high_risk_count"] == 1

    def test_sanitize_content(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        plugin.enable()
        content = "Hello <script>alert(1)</script> world"
        sanitized = plugin.sanitize_content(content)
        assert "<script>" not in sanitized
        assert "Hello" in sanitized

    def test_sanitize_content_disabled(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        content = "Hello <script>alert(1)</script> world"
        # 未启用，不过滤
        assert plugin.sanitize_content(content) == content

    def test_config_schema(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        schema = plugin.get_config_schema()
        assert len(schema) == 4
        keys = [f.key for f in schema]
        assert "auto_scan" in keys
        assert "scan_depth" in keys

    def test_register_hooks(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        plugin.register_hooks()
        assert hm.has_action("site_created") is True
        assert hm.has_filter("the_content") is True

    def test_scan_count_increments(self):
        hm = HookManager()
        plugin = SecurityScannerPlugin(hm)
        assert plugin.scan_count == 0
        plugin.scan_content("a")
        plugin.scan_content("b")
        assert plugin.scan_count == 2


class TestBuiltinPlugins:
    """内置插件注册表测试"""

    def test_builtin_plugins_registry(self):
        assert "seo_enhancer" in BUILTIN_PLUGINS
        assert "security_scanner" in BUILTIN_PLUGINS
        assert BUILTIN_PLUGINS["seo_enhancer"] is SEOEnhancerPlugin
        assert BUILTIN_PLUGINS["security_scanner"] is SecurityScannerPlugin

    def test_builtin_plugins_are_subclass(self):
        from app.services.plugin_system import PluginBase
        assert issubclass(SEOEnhancerPlugin, PluginBase)
        assert issubclass(SecurityScannerPlugin, PluginBase)


class TestAsyncPluginMethods:
    """异步插件方法测试"""

    def test_async_install_and_enable(self):
        async def run():
            info = PluginInfo(name="async-plugin", version="1.0.0")
            ok, msg = await async_install_plugin(info)
            assert ok is True
            ok, msg = await async_enable_plugin("async-plugin")
            assert ok is True
            assert plugin_lifecycle_manager.is_active("async-plugin") is True

        asyncio.run(run())
        # 清理
        plugin_lifecycle_manager.uninstall("async-plugin", force=True)

    def test_async_disable_and_uninstall(self):
        async def run():
            info = PluginInfo(name="async-test", version="1.0.0")
            await async_install_plugin(info)
            await async_enable_plugin("async-test")
            ok, _ = await async_disable_plugin("async-test")
            assert ok is True
            ok, _ = await async_uninstall_plugin("async-test")
            assert ok is True

        asyncio.run(run())

    def test_async_upgrade(self):
        async def run():
            info = PluginInfo(name="async-upgrade", version="1.0.0")
            await async_install_plugin(info)
            ok, msg = await async_upgrade_plugin("async-upgrade", "2.0.0")
            assert ok is True
            assert plugin_lifecycle_manager.get_plugin("async-upgrade").version == "2.0.0"

        asyncio.run(run())
        plugin_lifecycle_manager.uninstall("async-upgrade", force=True)

    def test_async_publish_event(self):
        async def run():
            received = []
            plugin_event_bus.subscribe("async.event", lambda e: received.append(e))
            count = await async_publish_event("async.event", {"k": "v"}, "tester")
            assert count == 1
            assert len(received) == 1

        asyncio.run(run())
        plugin_event_bus.clear_listeners("async.event")


class TestGlobalInstances:
    """全局实例测试"""

    def test_global_lifecycle_manager(self):
        assert plugin_lifecycle_manager is not None
        assert isinstance(plugin_lifecycle_manager, PluginLifecycleManager)

    def test_global_event_bus(self):
        assert plugin_event_bus is plugin_lifecycle_manager.event_bus
        assert isinstance(plugin_event_bus, PluginEventBus)

    def test_global_metadata_store(self):
        assert plugin_metadata_store is plugin_lifecycle_manager.metadata_store
        assert isinstance(plugin_metadata_store, PluginMetadataStore)

    def test_global_config_manager(self):
        assert plugin_config_manager is plugin_lifecycle_manager.config_manager
        assert isinstance(plugin_config_manager, PluginConfigManager)

    def test_global_dependency_resolver(self):
        assert plugin_dependency_resolver is plugin_lifecycle_manager.dependency_resolver
        assert isinstance(plugin_dependency_resolver, DependencyResolver)


class TestPluginBaseLifecycle:
    """PluginBase 生命周期钩子测试"""

    def test_install_hook(self):
        hm = HookManager()

        class MyPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.installed = False

            def install(self):
                self.installed = True

        plugin = MyPlugin(hm)
        plugin.install()
        assert plugin.installed is True

    def test_enable_hook(self):
        hm = HookManager()

        class MyPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.enabled = False

            def enable(self):
                self.enabled = True

        plugin = MyPlugin(hm)
        plugin.enable()
        assert plugin.enabled is True

    def test_disable_hook(self):
        hm = HookManager()

        class MyPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.disabled = False

            def disable(self):
                self.disabled = True

        plugin = MyPlugin(hm)
        plugin.disable()
        assert plugin.disabled is True

    def test_upgrade_hook(self):
        hm = HookManager()

        class MyPlugin(PluginBase):
            def __init__(self, hook_manager):
                super().__init__(hook_manager)
                self.upgrade_called = False
                self.upgrade_args = None

            def upgrade(self, old_version, new_version):
                self.upgrade_called = True
                self.upgrade_args = (old_version, new_version)

        plugin = MyPlugin(hm)
        plugin.upgrade("1.0.0", "2.0.0")
        assert plugin.upgrade_called is True
        assert plugin.upgrade_args == ("1.0.0", "2.0.0")
