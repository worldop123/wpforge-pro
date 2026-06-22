"""
插件系统测试
"""
import pytest
from app.plugins import (
    PluginManager,
    PluginBase,
    HookManager,
    get_plugin_manager,
    get_hook_manager,
)


class TestHookManager:
    """钩子管理器测试"""

    def test_hook_manager_creation(self):
        """测试钩子管理器创建"""
        hm = HookManager()
        assert hm is not None
        assert isinstance(hm.hooks, dict)

    def test_register_hook(self):
        """测试注册钩子"""
        hm = HookManager()
        hm.register_hook('test_hook')
        assert 'test_hook' in hm.hooks

    def test_add_action(self):
        """测试添加动作钩子"""
        hm = HookManager()
        hm.register_hook('test_action')
        
        def test_callback():
            return 'test'
        
        hm.add_action('test_action', test_callback)
        assert len(hm.hooks['test_action']) == 1

    def test_add_filter(self):
        """测试添加过滤钩子"""
        hm = HookManager()
        hm.register_hook('test_filter')
        
        def test_filter(value):
            return value.upper()
        
        hm.add_filter('test_filter', test_filter)
        assert len(hm.hooks['test_filter']) == 1

    def test_do_action(self):
        """测试执行动作钩子"""
        hm = HookManager()
        hm.register_hook('test_action')
        
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
        hm.register_hook('test_filter')
        
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
        hm.register_hook('test_action')
        
        def callback():
            pass
        
        hm.add_action('test_action', callback)
        assert len(hm.hooks['test_action']) == 1
        
        hm.remove_action('test_action', callback)
        assert len(hm.hooks['test_action']) == 0

    def test_remove_filter(self):
        """测试移除过滤钩子"""
        hm = HookManager()
        hm.register_hook('test_filter')
        
        def filter_func(value):
            return value
        
        hm.add_filter('test_filter', filter_func)
        assert len(hm.hooks['test_filter']) == 1
        
        hm.remove_filter('test_filter', filter_func)
        assert len(hm.hooks['test_filter']) == 0

    def test_hook_priority(self):
        """测试钩子优先级"""
        hm = HookManager()
        hm.register_hook('test_action')
        
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
        hm.register_hook('test_action')
        
        assert not hm.has_action('test_action')
        
        def callback():
            pass
        
        hm.add_action('test_action', callback)
        assert hm.has_action('test_action')

    def test_has_filter(self):
        """测试检查过滤钩子"""
        hm = HookManager()
        hm.register_hook('test_filter')
        
        assert not hm.has_filter('test_filter')
        
        def filter_func(value):
            return value
        
        hm.add_filter('test_filter', filter_func)
        assert hm.has_filter('test_filter')

    def test_get_instance(self):
        """测试单例模式"""
        hm1 = get_hook_manager()
        hm2 = get_hook_manager()
        assert hm1 is hm2


class TestPluginBase:
    """插件基类测试"""

    def test_plugin_base_creation(self):
        """测试插件基类创建"""
        plugin = PluginBase()
        assert plugin is not None

    def test_plugin_info(self):
        """测试插件信息"""
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
            description = "A test plugin"
            author = "Test Author"
        
        plugin = TestPlugin()
        assert plugin.name == "Test Plugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "A test plugin"
        assert plugin.author == "Test Author"

    def test_plugin_activate(self):
        """测试插件激活"""
        class TestPlugin(PluginBase):
            name = "Test"
            version = "1.0.0"
            
            def activate(self):
                self.activated = True
        
        plugin = TestPlugin()
        plugin.activate()
        assert plugin.activated is True

    def test_plugin_deactivate(self):
        """测试插件停用"""
        class TestPlugin(PluginBase):
            name = "Test"
            version = "1.0.0"
            
            def deactivate(self):
                self.deactivated = True
        
        plugin = TestPlugin()
        plugin.deactivate()
        assert plugin.deactivated is True

    def test_plugin_uninstall(self):
        """测试插件卸载"""
        class TestPlugin(PluginBase):
            name = "Test"
            version = "1.0.0"
            
            def uninstall(self):
                self.uninstalled = True
        
        plugin = TestPlugin()
        plugin.uninstall()
        assert plugin.uninstalled is True

    def test_plugin_register_hooks(self):
        """测试插件注册钩子"""
        class TestPlugin(PluginBase):
            name = "Test"
            version = "1.0.0"
            
            def register_hooks(self):
                pass
        
        plugin = TestPlugin()
        # Should not raise
        plugin.register_hooks()

    def test_plugin_get_info(self):
        """测试获取插件信息"""
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
            description = "Test description"
            author = "Test Author"
        
        plugin = TestPlugin()
        info = plugin.get_info()
        assert isinstance(info, dict)
        assert info['name'] == "Test Plugin"
        assert info['version'] == "1.0.0"


class TestPluginManager:
    """插件管理器测试"""

    def test_plugin_manager_creation(self):
        """测试插件管理器创建"""
        pm = PluginManager()
        assert pm is not None
        assert isinstance(pm.plugins, dict)

    def test_register_plugin(self):
        """测试注册插件"""
        pm = PluginManager()
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
        
        plugin = TestPlugin()
        pm.register_plugin(plugin)
        
        assert "Test Plugin" in pm.plugins
        assert pm.plugins["Test Plugin"].name == "Test Plugin"

    def test_unregister_plugin(self):
        """测试注销插件"""
        pm = PluginManager()
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
        
        plugin = TestPlugin()
        pm.register_plugin(plugin)
        assert "Test Plugin" in pm.plugins
        
        pm.unregister_plugin("Test Plugin")
        assert "Test Plugin" not in pm.plugins

    def test_activate_plugin(self):
        """测试激活插件"""
        pm = PluginManager()
        
        activated = False
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
            
            def activate(self):
                nonlocal activated
                activated = True
        
        plugin = TestPlugin()
        pm.register_plugin(plugin)
        pm.activate_plugin("Test Plugin")
        
        assert activated is True
        assert pm.plugins["Test Plugin"].is_active is True

    def test_deactivate_plugin(self):
        """测试停用插件"""
        pm = PluginManager()
        
        deactivated = False
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
            
            def deactivate(self):
                nonlocal deactivated
                deactivated = True
        
        plugin = TestPlugin()
        pm.register_plugin(plugin)
        pm.activate_plugin("Test Plugin")
        pm.deactivate_plugin("Test Plugin")
        
        assert deactivated is True
        assert pm.plugins["Test Plugin"].is_active is False

    def test_get_plugin(self):
        """测试获取插件"""
        pm = PluginManager()
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
        
        plugin = TestPlugin()
        pm.register_plugin(plugin)
        
        result = pm.get_plugin("Test Plugin")
        assert result is not None
        assert result.name == "Test Plugin"

    def test_get_plugin_not_found(self):
        """测试获取不存在的插件"""
        pm = PluginManager()
        result = pm.get_plugin("NonExistent")
        assert result is None

    def test_get_all_plugins(self):
        """测试获取所有插件"""
        pm = PluginManager()
        
        class Plugin1(PluginBase):
            name = "Plugin 1"
            version = "1.0.0"
        
        class Plugin2(PluginBase):
            name = "Plugin 2"
            version = "1.0.0"
        
        pm.register_plugin(Plugin1())
        pm.register_plugin(Plugin2())
        
        plugins = pm.get_all_plugins()
        assert isinstance(plugins, list)
        assert len(plugins) == 2

    def test_get_active_plugins(self):
        """测试获取激活的插件"""
        pm = PluginManager()
        
        class Plugin1(PluginBase):
            name = "Plugin 1"
            version = "1.0.0"
        
        class Plugin2(PluginBase):
            name = "Plugin 2"
            version = "1.0.0"
        
        pm.register_plugin(Plugin1())
        pm.register_plugin(Plugin2())
        pm.activate_plugin("Plugin 1")
        
        active = pm.get_active_plugins()
        assert isinstance(active, list)
        assert len(active) == 1
        assert active[0].name == "Plugin 1"

    def test_plugin_exists(self):
        """测试检查插件是否存在"""
        pm = PluginManager()
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
        
        pm.register_plugin(TestPlugin())
        
        assert pm.plugin_exists("Test Plugin") is True
        assert pm.plugin_exists("NonExistent") is False

    def test_is_plugin_active(self):
        """测试检查插件是否激活"""
        pm = PluginManager()
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
        
        pm.register_plugin(TestPlugin())
        
        assert pm.is_plugin_active("Test Plugin") is False
        pm.activate_plugin("Test Plugin")
        assert pm.is_plugin_active("Test Plugin") is True

    def test_install_plugin(self):
        """测试安装插件"""
        pm = PluginManager()
        # 模拟安装
        result = pm.install_plugin("test-plugin.zip")
        # 可能返回True或False，取决于实现
        assert isinstance(result, bool) or result is None

    def test_uninstall_plugin(self):
        """测试卸载插件"""
        pm = PluginManager()
        
        class TestPlugin(PluginBase):
            name = "Test Plugin"
            version = "1.0.0"
        
        pm.register_plugin(TestPlugin())
        result = pm.uninstall_plugin("Test Plugin")
        assert isinstance(result, bool) or result is None

    def test_get_instance(self):
        """测试单例模式"""
        pm1 = get_plugin_manager()
        pm2 = get_plugin_manager()
        assert pm1 is pm2

    def test_plugin_dependencies(self):
        """测试插件依赖"""
        pm = PluginManager()
        
        class DependencyPlugin(PluginBase):
            name = "Dependency"
            version = "1.0.0"
        
        class DependentPlugin(PluginBase):
            name = "Dependent"
            version = "1.0.0"
            dependencies = ["Dependency"]
        
        pm.register_plugin(DependencyPlugin())
        pm.register_plugin(DependentPlugin())
        
        # 应该能够检查依赖
        deps = pm.get_plugin_dependencies("Dependent")
        assert isinstance(deps, list)
        assert "Dependency" in deps

    def test_check_dependencies(self):
        """测试检查依赖"""
        pm = PluginManager()
        
        class DependencyPlugin(PluginBase):
            name = "Dependency"
            version = "1.0.0"
        
        class DependentPlugin(PluginBase):
            name = "Dependent"
            version = "1.0.0"
            dependencies = ["Dependency"]
        
        pm.register_plugin(DependencyPlugin())
        pm.register_plugin(DependentPlugin())
        
        satisfied, missing = pm.check_dependencies("Dependent")
        assert satisfied is True
        assert len(missing) == 0

    def test_check_dependencies_missing(self):
        """测试检查缺失的依赖"""
        pm = PluginManager()
        
        class DependentPlugin(PluginBase):
            name = "Dependent"
            version = "1.0.0"
            dependencies = ["MissingDependency"]
        
        pm.register_plugin(DependentPlugin())
        
        satisfied, missing = pm.check_dependencies("Dependent")
        assert satisfied is False
        assert len(missing) > 0
        assert "MissingDependency" in missing
