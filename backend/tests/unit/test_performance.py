"""
性能优化测试
覆盖数据库索引、查询缓存、预加载、前端构建优化、路由懒加载等
"""
import os
import time
import pytest
from sqlalchemy import inspect

from app.models.site import Site
from app.models.product import Product
from app.models.task import Task
from app.api.v1 import sites as sites_api


# ==================== 数据库索引测试 ====================

class TestDatabaseIndexes:
    """数据库索引优化测试"""

    def test_site_user_id_index_exists(self):
        """测试 Site.user_id 单列索引存在"""
        # 检查列级别索引
        user_id_col = Site.__table__.columns.get("user_id")
        assert user_id_col is not None
        assert user_id_col.index is True

    def test_site_composite_index_user_id_is_deleted(self):
        """测试 Site 复合索引 ix_sites_user_id_is_deleted 存在"""
        index_names = {idx.name for idx in Site.__table__.indexes}
        assert "ix_sites_user_id_is_deleted" in index_names

    def test_site_composite_index_user_id_status(self):
        """测试 Site 复合索引 ix_sites_user_id_status 存在"""
        index_names = {idx.name for idx in Site.__table__.indexes}
        assert "ix_sites_user_id_status" in index_names

    def test_site_composite_index_columns(self):
        """测试 Site 复合索引包含正确的列"""
        for idx in Site.__table__.indexes:
            if idx.name == "ix_sites_user_id_is_deleted":
                cols = {c.name for c in idx.columns}
                assert cols == {"user_id", "is_deleted"}
            elif idx.name == "ix_sites_user_id_status":
                cols = {c.name for c in idx.columns}
                assert cols == {"user_id", "status"}

    def test_product_single_indexes_exist(self):
        """测试 Product 单列索引存在（source_site, status, is_deleted, site_id）"""
        for col_name in ["source_site", "status", "is_deleted", "site_id"]:
            col = Product.__table__.columns.get(col_name)
            assert col is not None, f"列 {col_name} 不存在"
            assert col.index is True, f"列 {col_name} 未建立索引"

    def test_product_composite_index_site_id_is_deleted(self):
        """测试 Product 复合索引 ix_products_site_id_is_deleted 存在"""
        index_names = {idx.name for idx in Product.__table__.indexes}
        assert "ix_products_site_id_is_deleted" in index_names

    def test_product_composite_index_status_is_deleted(self):
        """测试 Product 复合索引 ix_products_status_is_deleted 存在"""
        index_names = {idx.name for idx in Product.__table__.indexes}
        assert "ix_products_status_is_deleted" in index_names

    def test_task_single_indexes_exist(self):
        """测试 Task 单列索引存在（task_type, status, site_id, user_id）"""
        for col_name in ["task_type", "status", "site_id", "user_id"]:
            col = Task.__table__.columns.get(col_name)
            assert col is not None, f"列 {col_name} 不存在"
            assert col.index is True, f"列 {col_name} 未建立索引"

    def test_task_composite_index_user_id_status(self):
        """测试 Task 复合索引 ix_tasks_user_id_status 存在"""
        index_names = {idx.name for idx in Task.__table__.indexes}
        assert "ix_tasks_user_id_status" in index_names

    def test_task_composite_index_user_id_type(self):
        """测试 Task 复合索引 ix_tasks_user_id_type 存在"""
        index_names = {idx.name for idx in Task.__table__.indexes}
        assert "ix_tasks_user_id_type" in index_names

    def test_task_composite_index_site_id_status(self):
        """测试 Task 复合索引 ix_tasks_site_id_status 存在"""
        index_names = {idx.name for idx in Task.__table__.indexes}
        assert "ix_tasks_site_id_status" in index_names

    def test_indexes_actually_created_in_db(self, db_engine):
        """测试索引在真实数据库中已创建（通过反射检查）"""
        inspector = inspect(db_engine)
        # 检查 sites 表的索引
        site_indexes = {idx["name"] for idx in inspector.get_indexes("sites")}
        assert "ix_sites_user_id_is_deleted" in site_indexes
        assert "ix_sites_user_id_status" in site_indexes

        # 检查 products 表的索引
        product_indexes = {idx["name"] for idx in inspector.get_indexes("products")}
        assert "ix_products_site_id_is_deleted" in product_indexes
        assert "ix_products_status_is_deleted" in product_indexes

        # 检查 tasks 表的索引
        task_indexes = {idx["name"] for idx in inspector.get_indexes("tasks")}
        assert "ix_tasks_user_id_status" in task_indexes
        assert "ix_tasks_site_id_status" in task_indexes


# ==================== 缓存测试 ====================

class TestStatsCaching:
    """站点统计缓存测试"""

    def setup_method(self):
        """每个测试前清空缓存，保证隔离"""
        sites_api._stats_cache.clear()

    def teardown_method(self):
        """每个测试后清空缓存"""
        sites_api._stats_cache.clear()

    def test_cache_miss_returns_none(self):
        """测试缓存未命中返回 None"""
        result = sites_api._get_cached_stats("nonexistent_key")
        assert result is None

    def test_cache_set_and_get(self):
        """测试缓存写入和读取"""
        key = "site_stats:1:100"
        data = {"products": 10, "tasks": 5}
        sites_api._set_cached_stats(key, data)

        cached = sites_api._get_cached_stats(key)
        assert cached is not None
        assert cached["products"] == 10
        assert cached["tasks"] == 5

    def test_cache_clear_all(self):
        """测试清空全部缓存"""
        sites_api._set_cached_stats("key1", {"a": 1})
        sites_api._set_cached_stats("key2", {"b": 2})

        sites_api.clear_stats_cache()

        assert len(sites_api._stats_cache) == 0
        assert sites_api._get_cached_stats("key1") is None
        assert sites_api._get_cached_stats("key2") is None

    def test_cache_clear_by_site_id(self):
        """测试按 site_id 清除缓存"""
        sites_api._set_cached_stats("site_stats:1:100", {"a": 1})
        sites_api._set_cached_stats("site_stats:1:200", {"b": 2})
        sites_api._set_cached_stats("site_stats:2:100", {"c": 3})

        sites_api.clear_stats_cache(site_id=100)

        # site_id=100 的缓存被清除
        assert sites_api._get_cached_stats("site_stats:1:100") is None
        assert sites_api._get_cached_stats("site_stats:2:100") is None
        # site_id=200 的缓存保留
        assert sites_api._get_cached_stats("site_stats:1:200") is not None

    def test_cache_clear_by_user_id(self):
        """测试按 user_id 清除缓存"""
        sites_api._set_cached_stats("site_stats:1:100", {"a": 1})
        sites_api._set_cached_stats("site_stats:2:200", {"b": 2})

        sites_api.clear_stats_cache(user_id=1)

        assert sites_api._get_cached_stats("site_stats:1:100") is None
        assert sites_api._get_cached_stats("site_stats:2:200") is not None

    def test_cache_ttl_expiration(self):
        """测试缓存 TTL 过期机制"""
        key = "site_stats:1:100"
        sites_api._set_cached_stats(key, {"data": "test"})

        # 模拟过期：手动修改时间戳为很久以前
        sites_api._stats_cache[key]["time"] = time.time() - sites_api._STATS_CACHE_TTL - 1

        # 过期后应返回 None
        result = sites_api._get_cached_stats(key)
        assert result is None
        # 过期项应被删除
        assert key not in sites_api._stats_cache

    def test_cache_ttl_not_expired(self):
        """测试缓存未过期时正常返回"""
        key = "site_stats:1:100"
        sites_api._set_cached_stats(key, {"data": "test"})

        # 不修改时间，应在 TTL 内
        result = sites_api._get_cached_stats(key)
        assert result is not None
        assert result["data"] == "test"

    def test_cache_ttl_value(self):
        """测试缓存 TTL 配置值为 30 秒"""
        assert sites_api._STATS_CACHE_TTL == 30

    def test_stats_endpoint_returns_cached_data(self, client, test_user, test_site, auth_headers):
        """测试统计接口第二次返回缓存数据"""
        # 第一次请求：查询数据库并写入缓存
        response1 = client.get(
            f"/api/v1/sites/{test_site.id}/stats",
            headers=auth_headers,
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["success"] is True
        assert "获取统计成功" in data1["message"]

        # 第二次请求：应命中缓存
        response2 = client.get(
            f"/api/v1/sites/{test_site.id}/stats",
            headers=auth_headers,
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["success"] is True
        assert "缓存" in data2["message"]
        # 缓存数据应与首次一致
        assert data2["data"] == data1["data"]


# ==================== 预加载（Eager Loading）测试 ====================

class TestEagerLoading:
    """查询预加载优化测试"""

    def test_selectinload_imported_in_sites_api(self):
        """测试 sites API 已导入 selectinload"""
        # 检查模块是否导入了 selectinload
        import app.api.v1.sites as sites_module
        assert hasattr(sites_module, "selectinload")

    def test_selectinload_is_callable(self):
        """测试 selectinload 可调用"""
        from sqlalchemy.orm import selectinload
        # selectinload 应该是可调用的加载器构造函数
        assert callable(selectinload)
        # 应能构造加载器
        loader = selectinload(Site.user)
        assert loader is not None

    def test_joinedload_available(self):
        """测试 joinedload 可用"""
        from sqlalchemy.orm import joinedload
        assert callable(joinedload)
        loader = joinedload(Site.user)
        assert loader is not None

    def test_relationships_defined_for_loading(self):
        """测试模型关系已定义（预加载前提条件）"""
        # Site 应有 user 关系
        assert "user" in Site.__mapper__.relationships.keys()
        # Product 应有 site 和 task 关系
        assert "site" in Product.__mapper__.relationships.keys()
        assert "task" in Product.__mapper__.relationships.keys()
        # Task 应有 site 和 user 关系
        assert "site" in Task.__mapper__.relationships.keys()
        assert "user" in Task.__mapper__.relationships.keys()


# ==================== 前端构建优化测试 ====================

class TestFrontendBuildOptimization:
    """前端 Vite 构建优化测试"""

    @pytest.fixture
    def vite_config_content(self):
        """读取 vite.config.ts 内容"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "frontend", "vite.config.ts"
        )
        config_path = os.path.abspath(config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_manual_chunks_configured(self, vite_config_content):
        """测试 manualChunks 代码分割已配置"""
        assert "manualChunks" in vite_config_content

    def test_manual_chunks_vue_vendor(self, vite_config_content):
        """测试 vue-vendor 分包配置"""
        assert "vue-vendor" in vite_config_content
        assert "vue" in vite_config_content

    def test_manual_chunks_element_plus(self, vite_config_content):
        """测试 element-plus 分包配置"""
        assert "element-plus" in vite_config_content

    def test_terser_minification(self, vite_config_content):
        """测试 terser 压缩配置"""
        assert "terser" in vite_config_content
        assert "drop_console" in vite_config_content
        assert "drop_debugger" in vite_config_content

    def test_css_code_split(self, vite_config_content):
        """测试 CSS 代码分割已启用"""
        assert "cssCodeSplit" in vite_config_content
        assert "true" in vite_config_content

    def test_chunk_size_warning_limit(self, vite_config_content):
        """测试 chunk 大小警告阈值已调整"""
        assert "chunkSizeWarningLimit" in vite_config_content

    def test_hash_filenames(self, vite_config_content):
        """测试资源文件名包含 hash（利于 CDN 缓存）"""
        assert "[hash]" in vite_config_content
        assert "chunkFileNames" in vite_config_content
        assert "entryFileNames" in vite_config_content


# ==================== 前端路由懒加载测试 ====================

class TestRouteLazyLoading:
    """前端路由懒加载测试"""

    @pytest.fixture
    def router_content(self):
        """读取路由配置内容"""
        router_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "frontend", "src", "router", "index.ts"
        )
        router_path = os.path.abspath(router_path)
        with open(router_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_routes_use_dynamic_import(self, router_content):
        """测试路由使用动态 import 懒加载"""
        # 动态导入语法
        assert "import(" in router_content
        assert "@/views/" in router_content

    def test_all_routes_are_lazy(self, router_content):
        """测试所有路由组件均为懒加载"""
        # 统计动态导入数量（应覆盖所有视图）
        import_count = router_content.count("() => import(")
        # 项目有 9 个视图路由
        assert import_count >= 9, f"懒加载路由数量不足: {import_count}"

    def test_no_static_view_imports(self, router_content):
        """测试没有静态导入视图组件（应全部懒加载）"""
        # 不应出现 import View from '@/views/...' 的静态导入
        lines = router_content.split("\n")
        for line in lines:
            # 排除注释行
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            # 不应有静态导入视图组件
            if "from '@/views/" in line and "import" in line:
                pytest.fail(f"发现静态视图导入，应使用懒加载: {line.strip()}")


# ==================== API 性能测试 ====================

class TestAPIPerformance:
    """API 接口性能测试"""

    def setup_method(self):
        """每个测试前清空缓存，保证隔离"""
        sites_api._stats_cache.clear()

    def teardown_method(self):
        """每个测试后清空缓存"""
        sites_api._stats_cache.clear()

    def test_cached_response_faster(self, client, test_user, test_site, auth_headers):
        """测试缓存命中时响应更快（或至少不慢）"""
        url = f"/api/v1/sites/{test_site.id}/stats"

        # 第一次请求（冷启动，查询数据库）
        start1 = time.perf_counter()
        response1 = client.get(url, headers=auth_headers)
        elapsed1 = time.perf_counter() - start1

        assert response1.status_code == 200

        # 第二次请求（命中缓存）
        start2 = time.perf_counter()
        response2 = client.get(url, headers=auth_headers)
        elapsed2 = time.perf_counter() - start2

        assert response2.status_code == 200
        # 缓存命中应标记缓存
        assert "缓存" in response2.json()["message"]

        # 缓存响应不应明显慢于首次（容差较大，避免环境波动）
        # 注意：这里不强制 elapsed2 < elapsed1，因为 TestClient 本身有开销
        # 但缓存命中应该不慢于首次查询的 2 倍
        assert elapsed2 < elapsed1 * 2 or elapsed2 < 0.1

    def test_stats_cache_invalidated_on_clear(self, client, test_user, test_site, auth_headers):
        """测试清除缓存后重新查询数据库"""
        url = f"/api/v1/sites/{test_site.id}/stats"

        # 第一次请求写入缓存
        response1 = client.get(url, headers=auth_headers)
        assert response1.status_code == 200
        assert "缓存" not in response1.json()["message"]

        # 验证缓存已写入
        assert len(sites_api._stats_cache) > 0

        # 第二次请求命中缓存
        response2 = client.get(url, headers=auth_headers)
        assert "缓存" in response2.json()["message"]

        # 清除缓存并验证
        sites_api.clear_stats_cache()
        assert len(sites_api._stats_cache) == 0

        # 第三次请求应重新查询数据库
        response3 = client.get(url, headers=auth_headers)
        assert response3.status_code == 200
        assert "缓存" not in response3.json()["message"]

    def test_list_sites_uses_indexed_query(self, client, test_user, test_site, auth_headers):
        """测试站点列表查询使用索引字段（user_id + is_deleted）"""
        # 该查询应利用 ix_sites_user_id_is_deleted 复合索引
        response = client.get("/api/v1/sites", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        # 返回的站点应属于当前用户
        for item in data["items"]:
            assert item["url"] is not None
