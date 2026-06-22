"""
WordPress服务测试

覆盖:
- ImportMethod, ImportStatus 枚举
- WPConfig, ImportResult 数据类
- WordPressCompatibilityChecker
- WooCommerceImporter
- WordPressMediaImporter
- ImportCheckpointManager
- DataIntegrityChecker
- create_woocommerce_importer 工厂函数
"""
import pytest
import base64
import json
import os
import time
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
from typing import Dict, Any

import httpx

from app.services.wordpress_service import (
    ImportMethod,
    ImportStatus,
    WPConfig,
    ImportResult,
    WordPressCompatibilityChecker,
    WooCommerceImporter,
    WordPressMediaImporter,
    ImportCheckpointManager,
    DataIntegrityChecker,
    create_woocommerce_importer,
)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def make_config(**kwargs) -> WPConfig:
    """创建测试用 WPConfig"""
    defaults = {
        "url": "https://example.com",
        "username": "admin",
        "app_password": "pass",
        "wc_consumer_key": "ck_test",
        "wc_consumer_secret": "cs_test",
    }
    defaults.update(kwargs)
    return WPConfig(**defaults)


def make_mock_response(status_code=200, json_data=None, text="OK") -> MagicMock:
    """创建模拟的 httpx 响应"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text
    resp.content = b"image-data"
    return resp


# ---------------------------------------------------------------------------
# ImportMethod 枚举
# ---------------------------------------------------------------------------
class TestImportMethod:
    def test_values(self):
        assert ImportMethod.REST_API.value == "rest_api"
        assert ImportMethod.WP_CLI.value == "wp_cli"
        assert ImportMethod.DATABASE.value == "database"
        assert ImportMethod.PLUGIN.value == "plugin"

    def test_count(self):
        assert len(list(ImportMethod)) == 4

    def test_is_str_enum(self):
        assert isinstance(ImportMethod.REST_API, str)
        assert ImportMethod.REST_API == "rest_api"


# ---------------------------------------------------------------------------
# ImportStatus 枚举
# ---------------------------------------------------------------------------
class TestImportStatus:
    def test_values(self):
        assert ImportStatus.PENDING.value == "pending"
        assert ImportStatus.RUNNING.value == "running"
        assert ImportStatus.COMPLETED.value == "completed"
        assert ImportStatus.FAILED.value == "failed"
        assert ImportStatus.PARTIAL.value == "partial"
        assert ImportStatus.CANCELLED.value == "cancelled"

    def test_count(self):
        assert len(list(ImportStatus)) == 6

    def test_is_str_enum(self):
        assert isinstance(ImportStatus.PENDING, str)


# ---------------------------------------------------------------------------
# WPConfig 数据类
# ---------------------------------------------------------------------------
class TestWPConfig:
    def test_defaults(self):
        config = WPConfig(url="https://example.com", username="admin", app_password="pass")
        assert config.url == "https://example.com"
        assert config.username == "admin"
        assert config.app_password == "pass"
        assert config.rest_api_url is None
        assert config.wc_consumer_key is None
        assert config.wc_consumer_secret is None
        assert config.version is None
        assert config.php_version is None

    def test_get_rest_url_default(self):
        config = make_config()
        url = config.get_rest_url()
        assert "/wp-json/wp/v2/" in url
        assert url.startswith("https://example.com")

    def test_get_rest_url_custom(self):
        config = make_config(rest_api_url="https://custom.com/api/")
        assert config.get_rest_url() == "https://custom.com/api/"

    def test_get_wc_rest_url(self):
        config = make_config()
        url = config.get_wc_rest_url()
        assert "/wp-json/wc/v3/" in url
        assert url.startswith("https://example.com")

    def test_get_auth_header(self):
        config = make_config(username="admin", app_password="secret")
        header = config.get_auth_header()
        assert "Authorization" in header
        assert header["Authorization"].startswith("Basic ")
        # 验证 base64 编码内容
        encoded = header["Authorization"].replace("Basic ", "")
        decoded = base64.b64decode(encoded).decode()
        assert decoded == "admin:secret"

    def test_get_auth_header_special_chars(self):
        config = make_config(username="user@test", app_password="p@ss w0rd")
        header = config.get_auth_header()
        encoded = header["Authorization"].replace("Basic ", "")
        decoded = base64.b64decode(encoded).decode()
        assert decoded == "user@test:p@ss w0rd"


# ---------------------------------------------------------------------------
# ImportResult 数据类
# ---------------------------------------------------------------------------
class TestImportResult:
    def test_defaults(self):
        result = ImportResult(status=ImportStatus.PENDING)
        assert result.status == ImportStatus.PENDING
        assert result.total == 0
        assert result.imported == 0
        assert result.failed == 0
        assert result.skipped == 0
        assert result.errors == []
        assert result.imported_ids == []
        assert result.failed_items == []
        assert result.start_time > 0
        assert result.end_time is None

    def test_duration_with_end_time(self):
        result = ImportResult(
            status=ImportStatus.COMPLETED,
            start_time=100.0,
            end_time=105.0,
        )
        assert result.duration == 5.0

    def test_duration_without_end_time(self):
        result = ImportResult(status=ImportStatus.RUNNING, start_time=time.time())
        d = result.duration
        assert d >= 0

    def test_success_rate_with_total(self):
        result = ImportResult(
            status=ImportStatus.COMPLETED,
            total=100,
            imported=80,
        )
        assert result.success_rate == 0.8

    def test_success_rate_zero_total(self):
        result = ImportResult(status=ImportStatus.PENDING, total=0)
        assert result.success_rate == 0.0

    def test_success_rate_full(self):
        result = ImportResult(
            status=ImportStatus.COMPLETED,
            total=10,
            imported=10,
        )
        assert result.success_rate == 1.0


# ---------------------------------------------------------------------------
# WordPressCompatibilityChecker
# ---------------------------------------------------------------------------
class TestWordPressCompatibilityChecker:
    def test_version_compare_equal(self):
        checker = WordPressCompatibilityChecker()
        assert checker._version_compare("5.0", "5.0") == 0
        assert checker._version_compare("5.0.1", "5.0.1") == 0

    def test_version_compare_greater(self):
        checker = WordPressCompatibilityChecker()
        assert checker._version_compare("6.0", "5.0") == 1
        assert checker._version_compare("5.1", "5.0") == 1

    def test_version_compare_less(self):
        checker = WordPressCompatibilityChecker()
        assert checker._version_compare("4.0", "5.0") == -1
        assert checker._version_compare("5.0", "5.1") == -1

    def test_version_compare_different_length(self):
        checker = WordPressCompatibilityChecker()
        assert checker._version_compare("5.0.1", "5.0") == 1
        assert checker._version_compare("5.0", "5.0.1") == -1

    def test_version_compare_invalid_parts(self):
        checker = WordPressCompatibilityChecker()
        # 非数字部分应当被当作 0 处理
        assert checker._version_compare("5.x", "5.0") == 0

    @pytest.mark.asyncio
    async def test_check_site_health_success(self):
        checker = WordPressCompatibilityChecker()
        config = make_config()

        wp_response = make_mock_response(200, {"version": "6.0"})
        wc_response = make_mock_response(200, {
            "version": "8.0",
            "environment": {
                "php_version": "8.0",
                "wp_memory_limit": "256M",
                "max_execution_time": "300",
            },
        })

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(side_effect=[wp_response, wc_response])
            mock_client_cls.return_value = mock_client

            result = await checker.check_site_health(config)

        assert result["rest_api_available"] is True
        assert result["wordpress_version"] == "6.0"
        assert result["woocommerce_active"] is True
        assert result["woocommerce_version"] == "8.0"
        assert result["php_version"] == "8.0"
        assert result["compatible"] is True

    @pytest.mark.asyncio
    async def test_check_site_health_connection_error(self):
        checker = WordPressCompatibilityChecker()
        config = make_config()

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(side_effect=Exception("connection error"))
            mock_client_cls.return_value = mock_client

            result = await checker.check_site_health(config)

        assert result["compatible"] is False
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_check_site_health_old_wordpress(self):
        checker = WordPressCompatibilityChecker()
        config = make_config()

        wp_response = make_mock_response(200, {"version": "4.0"})

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(side_effect=[wp_response, Exception("fail")])
            mock_client_cls.return_value = mock_client

            result = await checker.check_site_health(config)

        assert result["compatible"] is False
        assert any("WordPress版本过低" in i for i in result["issues"])

    @pytest.mark.asyncio
    async def test_check_plugin_conflicts_success(self):
        checker = WordPressCompatibilityChecker()
        config = make_config()

        plugins_response = make_mock_response(200, [
            {"plugin": "woocommerce/woocommerce.php", "status": "active"},
            {"plugin": "wordfence/wordfence.php", "status": "active"},
        ])

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(return_value=plugins_response)
            mock_client_cls.return_value = mock_client

            warnings = await checker.check_plugin_conflicts(config)

        assert any("wordfence" in w for w in warnings)

    @pytest.mark.asyncio
    async def test_check_plugin_conflicts_no_conflicts(self):
        checker = WordPressCompatibilityChecker()
        config = make_config()

        plugins_response = make_mock_response(200, [
            {"plugin": "woocommerce/woocommerce.php", "status": "active"},
        ])

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(return_value=plugins_response)
            mock_client_cls.return_value = mock_client

            warnings = await checker.check_plugin_conflicts(config)

        assert warnings == []

    @pytest.mark.asyncio
    async def test_check_plugin_conflicts_error(self):
        checker = WordPressCompatibilityChecker()
        config = make_config()

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(side_effect=Exception("fail"))
            mock_client_cls.return_value = mock_client

            warnings = await checker.check_plugin_conflicts(config)
            assert warnings == []


# ---------------------------------------------------------------------------
# WooCommerceImporter
# ---------------------------------------------------------------------------
class TestWooCommerceImporter:
    def test_init(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        assert importer.config is config
        assert isinstance(importer.compatibility_checker, WordPressCompatibilityChecker)
        assert importer._client is None

    def test_get_client_creates_instance(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        client1 = importer._get_client()
        client2 = importer._get_client()
        assert client1 is client2

    def test_convert_to_wc_product_basic(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {
            "name": "Test Product",
            "description": "A description",
            "sku": "TEST001",
            "regular_price": 29.99,
        }
        result = importer._convert_to_wc_product(product)
        assert result["name"] == "Test Product"
        assert result["description"] == "A description"
        assert result["sku"] == "TEST001"
        assert result["regular_price"] == "29.99"
        assert result["status"] == "publish"
        assert result["type"] == "simple"

    def test_convert_to_wc_product_title_fallback(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"title": "Title Product"}
        result = importer._convert_to_wc_product(product)
        assert result["name"] == "Title Product"

    def test_convert_to_wc_product_price_from_price_field(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "price": 19.99}
        result = importer._convert_to_wc_product(product)
        assert result["regular_price"] == "19.99"

    def test_convert_to_wc_product_sale_price(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "sale_price": 9.99}
        result = importer._convert_to_wc_product(product)
        assert result["sale_price"] == "9.99"

    def test_convert_to_wc_product_stock(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "stock_quantity": 10, "in_stock": True}
        result = importer._convert_to_wc_product(product)
        assert result["stock_quantity"] == 10
        assert result["manage_stock"] is True
        assert result["in_stock"] is True

    def test_convert_to_wc_product_categories_strings(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "categories": ["Electronics", "Gadgets"]}
        result = importer._convert_to_wc_product(product)
        assert result["categories"] == [{"name": "Electronics"}, {"name": "Gadgets"}]

    def test_convert_to_wc_product_categories_dicts(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "categories": [{"id": 1, "name": "Electronics"}]}
        result = importer._convert_to_wc_product(product)
        assert result["categories"] == [{"id": 1, "name": "Electronics"}]

    def test_convert_to_wc_product_tags(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "tags": ["new", "sale"]}
        result = importer._convert_to_wc_product(product)
        assert result["tags"] == [{"name": "new"}, {"name": "sale"}]

    def test_convert_to_wc_product_images(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "images": ["https://img.jpg"]}
        result = importer._convert_to_wc_product(product)
        assert result["images"] == [{"src": "https://img.jpg"}]

    def test_convert_to_wc_product_skip_images(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "images": ["https://img.jpg"]}
        result = importer._convert_to_wc_product(product, skip_images=True)
        assert "images" not in result

    def test_convert_to_wc_product_variable(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "is_variable": True}
        result = importer._convert_to_wc_product(product)
        assert result["type"] == "variable"

    def test_convert_to_wc_product_attributes(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        attrs = [{"name": "Color", "options": ["Red", "Blue"]}]
        product = {"name": "X", "attributes": attrs}
        result = importer._convert_to_wc_product(product)
        assert result["attributes"] == attrs

    def test_convert_to_wc_product_meta_data(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "meta_data": [{"key": "k", "value": "v"}]}
        result = importer._convert_to_wc_product(product)
        assert result["meta_data"] == [{"key": "k", "value": "v"}]

    def test_convert_to_wc_product_custom_status(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "status": "draft"}
        result = importer._convert_to_wc_product(product)
        assert result["status"] == "draft"

    def test_convert_to_wc_product_none_price(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        product = {"name": "X", "regular_price": None, "price": None}
        result = importer._convert_to_wc_product(product)
        assert "regular_price" not in result

    @pytest.mark.asyncio
    async def test_check_connection_success(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            result = await importer.check_connection()
            assert result is True

    @pytest.mark.asyncio
    async def test_check_connection_failure(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(404)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            result = await importer.check_connection()
            assert result is False

    @pytest.mark.asyncio
    async def test_check_connection_exception(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("fail"))
            mock_get.return_value = mock_client
            result = await importer.check_connection()
            assert result is False

    @pytest.mark.asyncio
    async def test_import_product_create_new(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        # SKU 查找返回空, 创建返回 201
        sku_response = make_mock_response(200, [])
        create_response = make_mock_response(201, {"id": 42, "name": "Test"})
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=sku_response)
            mock_client.post = AsyncMock(return_value=create_response)
            mock_get.return_value = mock_client
            success, pid, err = await importer.import_product({"name": "Test", "sku": "S1"})
            assert success is True
            assert pid == 42
            assert err is None

    @pytest.mark.asyncio
    async def test_import_product_update_existing(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        sku_response = make_mock_response(200, [{"id": 99}])
        update_response = make_mock_response(200, {"id": 99, "name": "Updated"})
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=sku_response)
            mock_client.put = AsyncMock(return_value=update_response)
            mock_get.return_value = mock_client
            success, pid, err = await importer.import_product(
                {"name": "Updated", "sku": "S1"}, update_if_exists=True
            )
            assert success is True
            assert pid == 99

    @pytest.mark.asyncio
    async def test_import_product_failure(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        sku_response = make_mock_response(200, [])
        create_response = make_mock_response(400, text="Bad Request")
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=sku_response)
            mock_client.post = AsyncMock(return_value=create_response)
            mock_get.return_value = mock_client
            success, pid, err = await importer.import_product({"name": "X", "sku": "S1"})
            assert success is False
            assert pid is None
            assert "400" in err

    @pytest.mark.asyncio
    async def test_import_product_exception(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            # _find_product_by_sku 内部捕获异常返回 None，所以 get 异常不会传播
            # 需要 post 也抛出异常来测试 import_product 的异常路径
            mock_client.get = AsyncMock(side_effect=Exception("boom"))
            mock_client.post = AsyncMock(side_effect=Exception("post-boom"))
            mock_get.return_value = mock_client
            success, pid, err = await importer.import_product({"name": "X", "sku": "S1"})
            assert success is False
            assert pid is None
            assert "post-boom" in err

    @pytest.mark.asyncio
    async def test_import_product_no_sku(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        create_response = make_mock_response(201, {"id": 1})
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=create_response)
            mock_get.return_value = mock_client
            success, pid, err = await importer.import_product({"name": "X"})
            assert success is True
            assert pid == 1
            # 没有 SKU 不应当调用 get
            mock_client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_find_product_by_sku_found(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200, [{"id": 7}])
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            pid = await importer._find_product_by_sku("ABC")
            assert pid == 7

    @pytest.mark.asyncio
    async def test_find_product_by_sku_not_found(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200, [])
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            pid = await importer._find_product_by_sku("ABC")
            assert pid is None

    @pytest.mark.asyncio
    async def test_find_product_by_sku_exception(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("fail"))
            mock_get.return_value = mock_client
            pid = await importer._find_product_by_sku("ABC")
            assert pid is None

    @pytest.mark.asyncio
    async def test_import_products_batch_all_success(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "import_product") as mock_import:
            mock_import.side_effect = [
                (True, 1, None),
                (True, 2, None),
                (True, 3, None),
            ]
            result = await importer.import_products_batch(
                [{"name": "P1"}, {"name": "P2"}, {"name": "P3"}],
                delay_between=0,
            )
            assert result.status == ImportStatus.COMPLETED
            assert result.total == 3
            assert result.imported == 3
            assert result.failed == 0
            assert result.imported_ids == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_import_products_batch_partial(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "import_product") as mock_import:
            mock_import.side_effect = [
                (True, 1, None),
                (False, None, "error"),
                (True, 3, None),
            ]
            result = await importer.import_products_batch(
                [{"name": "P1"}, {"name": "P2"}, {"name": "P3"}],
                delay_between=0,
            )
            assert result.status == ImportStatus.PARTIAL
            assert result.imported == 2
            assert result.failed == 1
            assert len(result.failed_items) == 1

    @pytest.mark.asyncio
    async def test_import_products_batch_all_failed(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "import_product") as mock_import:
            mock_import.side_effect = [
                (False, None, "err1"),
                (False, None, "err2"),
            ]
            result = await importer.import_products_batch(
                [{"name": "P1"}, {"name": "P2"}],
                delay_between=0,
            )
            assert result.status == ImportStatus.FAILED
            assert result.imported == 0
            assert result.failed == 2

    @pytest.mark.asyncio
    async def test_import_products_batch_empty(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        result = await importer.import_products_batch([], delay_between=0)
        assert result.total == 0
        assert result.imported == 0
        assert result.status == ImportStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_import_products_batch_with_progress_callback(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        progress_calls = []
        with patch.object(importer, "import_product") as mock_import:
            mock_import.side_effect = [(True, 1, None), (True, 2, None)]
            await importer.import_products_batch(
                [{"name": "P1"}, {"name": "P2"}],
                delay_between=0,
                progress_callback=lambda current, total: progress_calls.append((current, total)),
            )
            assert progress_calls == [(1, 2), (2, 2)]

    @pytest.mark.asyncio
    async def test_get_categories_success(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200, [{"id": 1, "name": "Cat"}])
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cats = await importer.get_categories()
            assert cats == [{"id": 1, "name": "Cat"}]

    @pytest.mark.asyncio
    async def test_get_categories_failure(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(404)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cats = await importer.get_categories()
            assert cats == []

    @pytest.mark.asyncio
    async def test_get_categories_exception(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("fail"))
            mock_get.return_value = mock_client
            cats = await importer.get_categories()
            assert cats == []

    @pytest.mark.asyncio
    async def test_create_category_success(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(201, {"id": 5})
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cat_id = await importer.create_category("New Cat")
            assert cat_id == 5

    @pytest.mark.asyncio
    async def test_create_category_with_parent(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(201, {"id": 6})
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cat_id = await importer.create_category("Child", parent_id=5)
            assert cat_id == 6
            # 验证 parent 被传入
            args, kwargs = mock_client.post.call_args
            assert kwargs["json"]["parent"] == 5

    @pytest.mark.asyncio
    async def test_create_category_failure(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(400)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cat_id = await importer.create_category("X")
            assert cat_id is None

    @pytest.mark.asyncio
    async def test_create_category_exception(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=Exception("fail"))
            mock_get.return_value = mock_client
            cat_id = await importer.create_category("X")
            assert cat_id is None

    @pytest.mark.asyncio
    async def test_find_category_by_name_found(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200, [{"id": 3, "name": "Electronics"}])
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cat_id = await importer._find_category_by_name("Electronics")
            assert cat_id == 3

    @pytest.mark.asyncio
    async def test_find_category_by_name_case_insensitive(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200, [{"id": 3, "name": "Electronics"}])
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cat_id = await importer._find_category_by_name("electronics")
            assert cat_id == 3

    @pytest.mark.asyncio
    async def test_find_category_by_name_not_found(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        response = make_mock_response(200, [{"id": 3, "name": "Other"}])
        with patch.object(importer, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=response)
            mock_get.return_value = mock_client
            cat_id = await importer._find_category_by_name("Electronics")
            assert cat_id is None

    @pytest.mark.asyncio
    async def test_close(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        mock_client = AsyncMock()
        importer._client = mock_client
        await importer.close()
        mock_client.aclose.assert_called_once()
        assert importer._client is None

    @pytest.mark.asyncio
    async def test_close_no_client(self):
        config = make_config()
        importer = WooCommerceImporter(config)
        # 没有 client 时不应抛出异常
        await importer.close()
        assert importer._client is None


# ---------------------------------------------------------------------------
# WordPressMediaImporter
# ---------------------------------------------------------------------------
class TestWordPressMediaImporter:
    @pytest.mark.asyncio
    async def test_import_image_success(self):
        config = make_config()
        importer = WordPressMediaImporter(config)
        download_response = make_mock_response(200)
        download_response.content = b"img-data"
        upload_response = make_mock_response(201, {"id": 10})

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(return_value=download_response)
            mock_client.post = AsyncMock(return_value=upload_response)
            mock_client_cls.return_value = mock_client

            media_id = await importer.import_image("https://img.jpg", alt_text="Alt")
            assert media_id == 10

    @pytest.mark.asyncio
    async def test_import_image_download_fail(self):
        config = make_config()
        importer = WordPressMediaImporter(config)
        download_response = make_mock_response(404)

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(return_value=download_response)
            mock_client_cls.return_value = mock_client

            media_id = await importer.import_image("https://img.jpg")
            assert media_id is None

    @pytest.mark.asyncio
    async def test_import_image_exception(self):
        config = make_config()
        importer = WordPressMediaImporter(config)

        with patch("app.services.wordpress_service.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(side_effect=Exception("fail"))
            mock_client_cls.return_value = mock_client

            media_id = await importer.import_image("https://img.jpg")
            assert media_id is None

    @pytest.mark.asyncio
    async def test_import_images_batch(self):
        config = make_config()
        importer = WordPressMediaImporter(config)
        with patch.object(importer, "import_image") as mock_import:
            mock_import.side_effect = [1, None, 3]
            results = await importer.import_images_batch(["a", "b", "c"])
            assert results == [1, None, 3]


# ---------------------------------------------------------------------------
# ImportCheckpointManager
# ---------------------------------------------------------------------------
class TestImportCheckpointManager:
    def test_init(self):
        mgr = ImportCheckpointManager("import-123")
        assert mgr.import_id == "import-123"
        assert mgr.checkpoint_file == "checkpoint_import-123.json"
        assert mgr._checkpoint is None

    def test_save_checkpoint(self, tmp_path):
        mgr = ImportCheckpointManager("test-save")
        with patch("app.services.wordpress_service.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            mgr.save_checkpoint({"current": 5, "total": 10})
            assert mgr._checkpoint is not None
            assert mgr._checkpoint["import_id"] == "test-save"
            assert mgr._checkpoint["progress"]["current"] == 5
            # 文件应当存在
            checkpoint_dir = tmp_path / "checkpoints"
            assert checkpoint_dir.exists()
            files = list(checkpoint_dir.iterdir())
            assert len(files) == 1

    def test_load_checkpoint_exists(self, tmp_path):
        mgr = ImportCheckpointManager("test-load")
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()
        checkpoint_path = checkpoint_dir / "checkpoint_test-load.json"
        data = {
            "import_id": "test-load",
            "timestamp": 123,
            "progress": {"current": 3, "total": 10},
        }
        checkpoint_path.write_text(json.dumps(data))

        with patch("app.services.wordpress_service.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            progress = mgr.load_checkpoint()
            assert progress == {"current": 3, "total": 10}
            assert mgr._checkpoint is not None

    def test_load_checkpoint_not_exists(self, tmp_path):
        mgr = ImportCheckpointManager("test-none")
        with patch("app.services.wordpress_service.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            progress = mgr.load_checkpoint()
            assert progress is None

    def test_clear_checkpoint_exists(self, tmp_path):
        mgr = ImportCheckpointManager("test-clear")
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()
        checkpoint_path = checkpoint_dir / "checkpoint_test-clear.json"
        checkpoint_path.write_text("{}")

        with patch("app.services.wordpress_service.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            mgr.clear_checkpoint()
            assert not checkpoint_path.exists()
            assert mgr._checkpoint is None

    def test_clear_checkpoint_not_exists(self, tmp_path):
        mgr = ImportCheckpointManager("test-clear-none")
        with patch("app.services.wordpress_service.settings") as mock_settings:
            mock_settings.UPLOAD_DIR = str(tmp_path)
            # 不存在时不应抛出异常
            mgr.clear_checkpoint()
            assert mgr._checkpoint is None


# ---------------------------------------------------------------------------
# DataIntegrityChecker
# ---------------------------------------------------------------------------
class TestDataIntegrityChecker:
    def test_validate_product_valid(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({
            "name": "Test Product",
            "price": 29.99,
        })
        assert errors == []
        assert warnings == []

    def test_validate_product_missing_name(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({"price": 10})
        assert any("名称" in e for e in errors)

    def test_validate_product_empty_name(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({"name": "", "title": ""})
        assert any("名称" in e for e in errors)

    def test_validate_product_title_as_name(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({"title": "Product"})
        assert errors == []

    def test_validate_product_negative_price(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({
            "name": "X",
            "price": -10,
        })
        assert any("负数" in e for e in errors)

    def test_validate_product_invalid_price(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({
            "name": "X",
            "price": "not-a-number",
        })
        assert any("无效" in e for e in errors)

    def test_validate_product_none_price(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({
            "name": "X",
            "price": None,
        })
        assert errors == []

    def test_validate_product_long_sku(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({
            "name": "X",
            "sku": "S" * 101,
        })
        assert any("SKU" in w for w in warnings)

    def test_validate_product_many_images(self):
        checker = DataIntegrityChecker()
        errors, warnings = checker.validate_product({
            "name": "X",
            "images": ["img"] * 101,
        })
        assert any("图片" in w for w in warnings)

    def test_check_import_consistency_full(self):
        checker = DataIntegrityChecker()
        result = checker.check_import_consistency(
            source_products=[{"name": "P1"}, {"name": "P2"}],
            imported_ids=[1, 2],
            wc_products=[],
        )
        assert result["total_source"] == 2
        assert result["total_imported"] == 2
        assert result["integrity_score"] == 1.0
        assert result["missing"] == []

    def test_check_import_consistency_partial(self):
        checker = DataIntegrityChecker()
        result = checker.check_import_consistency(
            source_products=[{"name": "P1"}, {"name": "P2"}, {"name": "P3"}],
            imported_ids=[1, 2],
            wc_products=[],
        )
        assert result["total_source"] == 3
        assert result["total_imported"] == 2
        assert result["integrity_score"] == 2 / 3

    def test_check_import_consistency_empty(self):
        checker = DataIntegrityChecker()
        result = checker.check_import_consistency(
            source_products=[],
            imported_ids=[],
            wc_products=[],
        )
        assert result["total_source"] == 0
        assert result["total_imported"] == 0
        assert result["integrity_score"] == 1.0


# ---------------------------------------------------------------------------
# create_woocommerce_importer 工厂函数
# ---------------------------------------------------------------------------
class TestCreateWooCommerceImporter:
    def test_create_with_all_params(self):
        importer = create_woocommerce_importer(
            url="https://example.com",
            username="admin",
            app_password="pass",
            wc_consumer_key="ck",
            wc_consumer_secret="cs",
        )
        assert isinstance(importer, WooCommerceImporter)
        assert importer.config.url == "https://example.com"
        assert importer.config.username == "admin"
        assert importer.config.app_password == "pass"
        assert importer.config.wc_consumer_key == "ck"
        assert importer.config.wc_consumer_secret == "cs"

    def test_create_without_wc_credentials(self):
        importer = create_woocommerce_importer(
            url="https://example.com",
            username="admin",
            app_password="pass",
        )
        assert isinstance(importer, WooCommerceImporter)
        assert importer.config.wc_consumer_key is None
        assert importer.config.wc_consumer_secret is None
