"""
Celery 任务测试 - 使用 mock 隔离 Celery 执行和数据库

任务实现已切换为真实 service 调用，因此测试通过 mock.patch 模拟
service 工厂/类，验证任务逻辑正确调用 service 并更新 Task 状态。
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from app.tasks import celery_app, get_task_function, setup_scheduled_tasks
from app.tasks.scraping_tasks import scrape_products_task, _update_progress, _add_log
from app.tasks.translation_tasks import translate_products_task
from app.tasks.import_tasks import import_to_wordpress_task
from app.tasks.seo_tasks import optimize_seo_task
from app.tasks.cloning_tasks import clone_site_task

# 导入服务层的数据类，用于构造 mock 返回值
from app.services.scraper_service import ScrapedProduct
from app.services.ai_clone_service import CloneResult, ClonedPage, PageType
from app.services.wordpress_service import ImportResult, ImportStatus


class FakeRequest:
    """模拟 Celery self.request"""
    id = "fake-celery-id-123"


class FakeQuery:
    """模拟 SQLAlchemy query 链式调用"""

    def __init__(self, first_result=None, all_result=None, first_func=None):
        self._first_result = first_result
        self._all_result = all_result or []
        self._first_func = first_func

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def first(self):
        if self._first_func:
            return self._first_func()
        return self._first_result

    def all(self):
        return self._all_result

    def count(self):
        return len(self._all_result)


def _make_task_mock(status="pending"):
    """构造一个 mock task 对象"""
    task = MagicMock()
    task.id = 1
    task.status = status
    task.progress = 0
    task.status_message = ""
    task.total_items = 0
    task.processed_items = 0
    task.failed_items = 0
    task.result = {}
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    task.params = {}
    return task


def _make_product_mock(pid=1, name="Product", description="Desc",
                       short_description="Short", regular_price="100.00",
                       currency="USD", price="100.00", is_deleted=False,
                       site_id=1, source_url="https://example.com",
                       seo_title=None, seo_description=None, seo_keywords=None,
                       sku="SKU-001", stock_quantity=10, in_stock=True,
                       categories=None, tags=None, images=None,
                       attributes=None, variations=None, is_variable=False,
                       meta_data=None, wp_post_id=None, wp_status="draft",
                       last_synced_at=None, translated=False,
                       translation_language=None):
    """构造一个 mock product 对象"""
    product = MagicMock()
    product.id = pid
    product.name = name
    product.description = description
    product.short_description = short_description
    product.regular_price = regular_price
    product.price = price
    product.currency = currency
    product.sale_price = None
    product.is_deleted = is_deleted
    product.site_id = site_id
    product.source_url = source_url
    product.seo_title = seo_title
    product.seo_description = seo_description
    product.seo_keywords = seo_keywords
    product.sku = sku
    product.stock_quantity = stock_quantity
    product.in_stock = in_stock
    product.categories = categories or []
    product.tags = tags or []
    product.images = images or []
    product.attributes = attributes or []
    product.variations = variations or []
    product.is_variable = is_variable
    product.meta_data = meta_data or {}
    product.wp_post_id = wp_post_id
    product.wp_status = wp_status
    product.last_synced_at = last_synced_at
    product.translated = translated
    product.translation_language = translation_language
    return product


def _make_site_mock(wp_url="https://wp.example.com", wp_username="admin",
                    wp_password="pass", wc_consumer_key="key",
                    wc_consumer_secret="secret", currency="USD",
                    price_markup=30):
    """构造一个 mock site 对象"""
    site = MagicMock()
    site.wp_url = wp_url
    site.wp_username = wp_username
    site.wp_password = wp_password
    site.wc_consumer_key = wc_consumer_key
    site.wc_consumer_secret = wc_consumer_secret
    site.currency = currency
    site.price_markup = price_markup
    return site


def _make_db_mock(task=None, site=None, products=None, task_first_func=None):
    """构造一个 mock db session，支持按模型返回不同结果"""
    db = MagicMock()

    def query_side_effect(model):
        if model.__name__ == "Task":
            if task_first_func:
                return FakeQuery(first_func=task_first_func)
            return FakeQuery(first_result=task)
        if model.__name__ == "Site":
            return FakeQuery(first_result=site)
        if model.__name__ == "Product":
            return FakeQuery(all_result=products or [])
        return FakeQuery()

    db.query.side_effect = query_side_effect
    db.commit = MagicMock()
    db.close = MagicMock()
    db.add = MagicMock()
    db.refresh = MagicMock()
    return db


def _make_cancelled_task_first_func(pending_task, cancelled_task):
    """构造一个 first() 函数：第一次返回 pending，之后返回 cancelled"""
    call_count = {"n": 0}

    def fake_first():
        call_count["n"] += 1
        if call_count["n"] <= 1:
            return pending_task
        return cancelled_task

    return fake_first


# ==================== Celery 应用测试 ====================

class TestCeleryApp:
    """Celery 应用配置测试"""

    def test_celery_app_name(self):
        assert celery_app.main == "wpforge"

    def test_celery_app_config(self):
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.accept_content == ["json"]
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.timezone == "Asia/Shanghai"
        assert celery_app.conf.enable_utc is True
        assert celery_app.conf.task_track_started is True
        assert celery_app.conf.task_time_limit == 3600
        assert celery_app.conf.task_soft_time_limit == 3300
        assert celery_app.conf.worker_prefetch_multiplier == 1
        assert celery_app.conf.worker_max_tasks_per_child == 1000
        assert celery_app.conf.result_expires == 86400

    def test_get_task_function_known(self):
        func = get_task_function("scraping")
        assert func is not None
        assert func.name == "scrape_products"

    def test_get_task_function_translation(self):
        func = get_task_function("translation")
        assert func is not None
        assert func.name == "translate_products"

    def test_get_task_function_import(self):
        func = get_task_function("import")
        assert func is not None
        assert func.name == "import_to_wordpress"

    def test_get_task_function_seo(self):
        func = get_task_function("seo")
        assert func is not None
        assert func.name == "optimize_seo"

    def test_get_task_function_cloning(self):
        func = get_task_function("cloning")
        assert func is not None
        assert func.name == "clone_site"

    def test_get_task_function_pricing(self):
        # pricing_tasks 已修复导入，使用真实 PriceCalculator/PriceOptimizer
        func = get_task_function("pricing")
        assert func is not None
        assert func.name == "calculate_prices_task"

    def test_get_task_function_unknown(self):
        assert get_task_function("unknown_type") is None

    def test_get_task_function_empty(self):
        assert get_task_function("") is None


class TestSetupScheduledTasks:
    """定时任务配置测试"""

    def test_setup_scheduled_tasks_default(self):
        result = setup_scheduled_tasks()
        assert isinstance(result, dict)
        # 应该至少有一个定时任务
        assert len(result) >= 1

    def test_setup_scheduled_tasks_custom(self):
        custom = [
            {
                "name": "test-scrape",
                "task": "app.tasks.scraping_tasks.scrape_products_task",
                "cron": "0 4 * * *",
                "args": [1, {"url": "https://x.com"}],
            }
        ]
        result = setup_scheduled_tasks(custom)
        assert "test-scrape" in result
        assert celery_app.conf.beat_schedule.get("test-scrape") is not None

    def test_setup_scheduled_tasks_empty_list(self):
        result = setup_scheduled_tasks([])
        # 空列表时使用默认配置
        assert isinstance(result, dict)


# ==================== 采集任务测试 ====================

class TestScrapingTask:
    """scrape_products_task 测试"""

    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_not_found(self, mock_session_local):
        """任务不存在时返回错误"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = scrape_products_task.run(
            task_id=999,
            params={"url": "https://example.com", "max_products": 5},
        )

        assert result == {"error": "任务不存在"}
        mock_db.close.assert_called_once()

    @patch("app.tasks.scraping_tasks.create_woocommerce_scraper")
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_success(self, mock_session_local, mock_create_scraper):
        """任务正常执行：验证真实采集服务被调用"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        # 模拟采集器返回5个产品
        mock_products = [
            ScrapedProduct(url=f"https://example.com/product-{i}", title=f"Product {i}")
            for i in range(5)
        ]
        mock_scraper = MagicMock()
        mock_scraper.scrape = AsyncMock(return_value=mock_products)
        mock_create_scraper.return_value = mock_scraper

        result = scrape_products_task.run(
            task_id=1,
            params={
                "url": "https://example.com",
                "max_products": 5,
                "auto_translate": False,
                "auto_import": False,
            },
        )

        assert result["status"] == "completed"
        assert result["products_collected"] == 5
        assert result["task_id"] == 1
        assert task.status == "completed"
        assert task.progress == 100
        mock_db.close.assert_called_once()
        # 验证真实采集服务被调用
        mock_create_scraper.assert_called_once()
        mock_scraper.scrape.assert_called_once()

    @patch("app.tasks.scraping_tasks.create_woocommerce_scraper")
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_with_auto_translate(self, mock_session_local, mock_create_scraper):
        """启用自动翻译"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        mock_products = [
            ScrapedProduct(url=f"https://example.com/p{i}", title=f"P{i}") for i in range(5)
        ]
        mock_scraper = MagicMock()
        mock_scraper.scrape = AsyncMock(return_value=mock_products)
        mock_create_scraper.return_value = mock_scraper

        result = scrape_products_task.run(
            task_id=1,
            params={
                "url": "https://example.com",
                "max_products": 5,
                "auto_translate": True,
                "target_language": "zh-CN",
            },
        )

        assert result["status"] == "completed"
        assert task.result["auto_translate"] is True
        assert task.result["target_language"] == "zh-CN"

    @patch("app.tasks.scraping_tasks.create_woocommerce_scraper")
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_with_auto_import(self, mock_session_local, mock_create_scraper):
        """启用自动导入"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        mock_products = [
            ScrapedProduct(url=f"https://example.com/p{i}", title=f"P{i}") for i in range(5)
        ]
        mock_scraper = MagicMock()
        mock_scraper.scrape = AsyncMock(return_value=mock_products)
        mock_create_scraper.return_value = mock_scraper

        result = scrape_products_task.run(
            task_id=1,
            params={
                "url": "https://example.com",
                "max_products": 5,
                "auto_import": True,
                "site_id": 1,
            },
        )

        assert result["status"] == "completed"
        assert task.result["auto_import"] is True

    @patch("app.tasks.scraping_tasks.create_woocommerce_scraper")
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_cancelled(self, mock_session_local, mock_create_scraper):
        """任务被取消：采集器调用 progress_callback 时检测到取消"""
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        fake_first = _make_cancelled_task_first_func(pending_task, cancelled_task)
        mock_db = _make_db_mock(task_first_func=fake_first)
        mock_session_local.return_value = mock_db

        # 模拟采集器调用 progress_callback，触发取消检查
        async def fake_scrape(progress_callback=None):
            if progress_callback:
                progress_callback(1, 10)
            return []

        mock_scraper = MagicMock()
        mock_scraper.scrape = fake_scrape
        mock_create_scraper.return_value = mock_scraper

        result = scrape_products_task.run(
            task_id=1,
            params={"url": "https://example.com", "max_products": 100},
        )

        assert result["status"] == "cancelled"
        assert "collected" in result

    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_exception(self, mock_session_local):
        """任务执行异常：commit 失败时标记任务为 failed"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        # commit 调用顺序：
        # 1. task.status="running" 后 commit
        # 2. _add_log 内 commit（异常被吞）
        # 3. _update_progress 内 commit（此处抛异常，传播到外层）
        call_count = {"n": 0}

        def commit_side_effect():
            call_count["n"] += 1
            if call_count["n"] == 3:
                raise Exception("DB error")

        mock_db.commit.side_effect = commit_side_effect
        mock_session_local.return_value = mock_db

        result = scrape_products_task.run(
            task_id=1,
            params={"url": "https://example.com", "max_products": 5},
        )

        assert result["status"] == "failed"
        assert "error" in result


# ==================== 翻译任务测试 ====================

class TestTranslationTask:
    """translate_products_task 测试"""

    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_not_found(self, mock_session_local):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = translate_products_task.run(task_id=999, params={})

        assert result == {"error": "任务不存在"}
        mock_db.close.assert_called_once()

    @patch("app.tasks.translation_tasks.TranslationService")
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_success(self, mock_session_local, mock_translation_cls):
        """任务正常执行：验证真实翻译服务被调用"""
        task = _make_task_mock()
        products = [_make_product_mock(pid=i) for i in range(1, 6)]
        mock_db = _make_db_mock(task=task, products=products)
        mock_session_local.return_value = mock_db

        # 模拟翻译服务
        mock_service = MagicMock()
        mock_service.translate_product = AsyncMock(return_value={
            "name": "翻译后的名称",
            "description": "翻译后的描述",
            "short_description": "翻译后的简短描述",
        })
        mock_translation_cls.return_value = mock_service

        result = translate_products_task.run(
            task_id=1,
            params={
                "product_ids": [1, 2, 3, 4, 5],
                "target_language": "zh-CN",
                "engine": "ai",
                "polish": True,
            },
        )

        assert result["status"] == "completed"
        assert result["translated_products"] == 5
        assert task.status == "completed"
        assert task.result["target_language"] == "zh-CN"
        assert task.result["engine"] == "ai"
        # 验证翻译服务被调用5次
        assert mock_service.translate_product.call_count == 5

    @patch("app.tasks.translation_tasks.TranslationService")
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_no_polish(self, mock_session_local, mock_translation_cls):
        task = _make_task_mock()
        products = [_make_product_mock(pid=1), _make_product_mock(pid=2)]
        mock_db = _make_db_mock(task=task, products=products)
        mock_session_local.return_value = mock_db

        mock_service = MagicMock()
        mock_service.translate_product = AsyncMock(return_value={"name": "翻译"})
        mock_translation_cls.return_value = mock_service

        result = translate_products_task.run(
            task_id=1,
            params={
                "product_ids": [1, 2],
                "polish": False,
            },
        )

        assert result["status"] == "completed"
        assert task.result["polished"] is False

    @patch("app.tasks.translation_tasks.TranslationService")
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_cancelled(self, mock_session_local, mock_translation_cls):
        """任务被取消：循环中检测到 cancelled 状态"""
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        fake_first = _make_cancelled_task_first_func(pending_task, cancelled_task)
        products = [_make_product_mock(pid=1)]
        mock_db = _make_db_mock(task_first_func=fake_first, products=products)
        mock_session_local.return_value = mock_db

        mock_service = MagicMock()
        mock_service.translate_product = AsyncMock(return_value={"name": "翻译"})
        mock_translation_cls.return_value = mock_service

        result = translate_products_task.run(
            task_id=1,
            params={"product_ids": list(range(100))},
        )

        assert result["status"] == "cancelled"

    @patch("app.tasks.translation_tasks.TranslationService")
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_default_total(self, mock_session_local, mock_translation_cls):
        """没有 product_ids 时查询数据库获取产品"""
        task = _make_task_mock()
        products = [_make_product_mock(pid=i) for i in range(1, 4)]
        mock_db = _make_db_mock(task=task, products=products)
        mock_session_local.return_value = mock_db

        mock_service = MagicMock()
        mock_service.translate_product = AsyncMock(return_value={"name": "翻译"})
        mock_translation_cls.return_value = mock_service

        result = translate_products_task.run(
            task_id=1,
            params={},
        )

        assert result["status"] == "completed"
        assert result["translated_products"] == 3


# ==================== 导入任务测试 ====================

class TestImportTask:
    """import_to_wordpress_task 测试"""

    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_not_found(self, mock_session_local):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = import_to_wordpress_task.run(task_id=999, params={})

        assert result == {"error": "任务不存在"}
        mock_db.close.assert_called_once()

    @patch("app.tasks.import_tasks.create_woocommerce_importer")
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_success(self, mock_session_local, mock_create_importer):
        """任务正常执行：验证真实导入服务被调用"""
        task = _make_task_mock()
        site = _make_site_mock()
        products = [_make_product_mock(pid=i) for i in range(1, 6)]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        # 模拟导入器
        mock_importer = MagicMock()
        mock_importer.check_connection = AsyncMock(return_value=True)
        mock_import_result = ImportResult(
            status=ImportStatus.COMPLETED,
            total=5,
            imported=5,
            failed=0,
            skipped=0,
            imported_ids=[101, 102, 103, 104, 105],
        )
        mock_importer.import_products_batch = AsyncMock(return_value=mock_import_result)
        mock_create_importer.return_value = mock_importer

        result = import_to_wordpress_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "product_ids": [1, 2, 3, 4, 5],
                "import_method": "rest_api",
                "publish": True,
            },
        )

        assert result["status"] == "completed"
        assert "imported_products" in result
        assert "failed_products" in result
        assert task.status == "completed"
        assert task.result["import_method"] == "rest_api"
        assert task.result["publish"] is True
        # 验证真实导入服务被调用
        mock_importer.check_connection.assert_called_once()
        mock_importer.import_products_batch.assert_called_once()

    @patch("app.tasks.import_tasks.create_woocommerce_importer")
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_skip_images(self, mock_session_local, mock_create_importer):
        task = _make_task_mock()
        site = _make_site_mock()
        products = [_make_product_mock(pid=1), _make_product_mock(pid=2)]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        mock_importer = MagicMock()
        mock_importer.check_connection = AsyncMock(return_value=True)
        mock_import_result = ImportResult(
            status=ImportStatus.COMPLETED,
            total=2,
            imported=2,
            failed=0,
            skipped=0,
            imported_ids=[101, 102],
        )
        mock_importer.import_products_batch = AsyncMock(return_value=mock_import_result)
        mock_create_importer.return_value = mock_importer

        result = import_to_wordpress_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "product_ids": [1, 2],
                "skip_images": True,
            },
        )

        assert result["status"] == "completed"

    @patch("app.tasks.import_tasks.create_woocommerce_importer")
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_no_publish(self, mock_session_local, mock_create_importer):
        task = _make_task_mock()
        site = _make_site_mock()
        products = [_make_product_mock(pid=1), _make_product_mock(pid=2)]
        mock_db = _make_db_mock(task=task, site=site, products=products)
        mock_session_local.return_value = mock_db

        mock_importer = MagicMock()
        mock_importer.check_connection = AsyncMock(return_value=True)
        mock_import_result = ImportResult(
            status=ImportStatus.COMPLETED,
            total=2,
            imported=2,
            failed=0,
            skipped=0,
            imported_ids=[101, 102],
        )
        mock_importer.import_products_batch = AsyncMock(return_value=mock_import_result)
        mock_create_importer.return_value = mock_importer

        result = import_to_wordpress_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "product_ids": [1, 2],
                "publish": False,
            },
        )

        assert result["status"] == "completed"
        assert task.result["publish"] is False

    @patch("app.tasks.import_tasks.create_woocommerce_importer")
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_cancelled(self, mock_session_local, mock_create_importer):
        """任务被取消：导入器调用 progress_callback 时检测到取消"""
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        fake_first = _make_cancelled_task_first_func(pending_task, cancelled_task)
        site = _make_site_mock()
        products = [_make_product_mock(pid=i) for i in range(1, 101)]
        mock_db = _make_db_mock(task_first_func=fake_first, site=site, products=products)
        mock_session_local.return_value = mock_db

        # 模拟导入器调用 progress_callback 触发取消
        mock_importer = MagicMock()
        mock_importer.check_connection = AsyncMock(return_value=True)

        async def fake_import(**kwargs):
            progress_callback = kwargs.get("progress_callback")
            if progress_callback:
                progress_callback(1, len(kwargs.get("products", [])))
            return ImportResult(status=ImportStatus.CANCELLED, total=0)

        mock_importer.import_products_batch = fake_import
        mock_create_importer.return_value = mock_importer

        result = import_to_wordpress_task.run(
            task_id=1,
            params={"product_ids": list(range(1, 101)), "site_id": 1},
        )

        assert result["status"] == "cancelled"


# ==================== SEO 任务测试 ====================

class TestSEOTask:
    """optimize_seo_task 测试"""

    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_not_found(self, mock_session_local):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = optimize_seo_task.run(task_id=999, params={})

        assert result == {"error": "任务不存在"}
        mock_db.close.assert_called_once()

    @patch("app.tasks.seo_tasks.SiteSpeedOptimizer")
    @patch("app.tasks.seo_tasks.SEOGenerator")
    @patch("app.tasks.seo_tasks.SEOAnalyzer")
    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_success(self, mock_session_local, mock_analyzer_cls,
                              mock_generator_cls, mock_speed_cls):
        """任务正常执行：验证真实 SEO 服务被调用"""
        task = _make_task_mock()
        products = [_make_product_mock(pid=i) for i in range(1, 6)]
        mock_db = _make_db_mock(task=task, products=products)
        mock_session_local.return_value = mock_db

        # 模拟 SEO 分析器
        mock_analyzer = mock_analyzer_cls.return_value
        mock_analysis = MagicMock()
        mock_analysis.overall_score = 50
        mock_analyzer.analyze_html.return_value = mock_analysis

        # 模拟 SEO 生成器
        mock_generator = mock_generator_cls.return_value
        mock_generator.generate_seo_title = AsyncMock(return_value="SEO Title")
        mock_generator.generate_meta_description = AsyncMock(return_value="SEO Description")

        # 模拟速度优化器
        mock_speed = mock_speed_cls.return_value
        mock_speed.get_optimization_suggestions.return_value = [{"category": "images"}]
        mock_speed.generate_htaccess_rules.return_value = "# rules"

        result = optimize_seo_task.run(
            task_id=1,
            params={
                "site_id": 1,
                "page_ids": [1, 2, 3, 4, 5],
                "optimize_type": "full",
                "target_keywords": ["shoes", "sneakers"],
            },
        )

        assert result["status"] == "completed"
        assert result["optimized_pages"] == 5
        assert task.status == "completed"
        assert task.result["optimize_type"] == "full"
        assert task.result["keywords_optimized"] == 2
        assert task.result["schema_generated"] is True
        assert task.result["sitemap_updated"] is True
        # 验证真实 SEO 服务被调用
        assert mock_analyzer.analyze_html.call_count == 5
        assert mock_generator.generate_seo_title.call_count == 5

    @patch("app.tasks.seo_tasks.SiteSpeedOptimizer")
    @patch("app.tasks.seo_tasks.SEOGenerator")
    @patch("app.tasks.seo_tasks.SEOAnalyzer")
    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_default_pages(self, mock_session_local, mock_analyzer_cls,
                                    mock_generator_cls, mock_speed_cls):
        """没有 page_ids 时查询数据库获取产品"""
        task = _make_task_mock()
        products = [_make_product_mock(pid=i) for i in range(1, 4)]
        mock_db = _make_db_mock(task=task, products=products)
        mock_session_local.return_value = mock_db

        mock_analyzer = mock_analyzer_cls.return_value
        mock_analysis = MagicMock()
        mock_analysis.overall_score = 50
        mock_analyzer.analyze_html.return_value = mock_analysis

        mock_generator = mock_generator_cls.return_value
        mock_generator.generate_seo_title = AsyncMock(return_value="SEO Title")
        mock_generator.generate_meta_description = AsyncMock(return_value="SEO Desc")

        mock_speed = mock_speed_cls.return_value
        mock_speed.get_optimization_suggestions.return_value = []
        mock_speed.generate_htaccess_rules.return_value = "# rules"

        result = optimize_seo_task.run(
            task_id=1,
            params={},
        )

        assert result["status"] == "completed"
        assert result["optimized_pages"] == 3

    @patch("app.tasks.seo_tasks.SiteSpeedOptimizer")
    @patch("app.tasks.seo_tasks.SEOGenerator")
    @patch("app.tasks.seo_tasks.SEOAnalyzer")
    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_cancelled(self, mock_session_local, mock_analyzer_cls,
                                mock_generator_cls, mock_speed_cls):
        """任务被取消：循环中检测到 cancelled 状态"""
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        fake_first = _make_cancelled_task_first_func(pending_task, cancelled_task)
        products = [_make_product_mock(pid=1)]
        mock_db = _make_db_mock(task_first_func=fake_first, products=products)
        mock_session_local.return_value = mock_db

        mock_analyzer = mock_analyzer_cls.return_value
        mock_analysis = MagicMock()
        mock_analysis.overall_score = 50
        mock_analyzer.analyze_html.return_value = mock_analysis

        mock_generator = mock_generator_cls.return_value
        mock_generator.generate_seo_title = AsyncMock(return_value="SEO Title")
        mock_generator.generate_meta_description = AsyncMock(return_value="SEO Desc")

        mock_speed = mock_speed_cls.return_value
        mock_speed.get_optimization_suggestions.return_value = []
        mock_speed.generate_htaccess_rules.return_value = "# rules"

        result = optimize_seo_task.run(
            task_id=1,
            params={"page_ids": list(range(100))},
        )

        assert result["status"] == "cancelled"


# ==================== 仿站任务测试 ====================

class TestCloningTask:
    """clone_site_task 测试"""

    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_not_found(self, mock_session_local):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        result = clone_site_task.run(task_id=999, params={})

        assert result == {"error": "任务不存在"}
        mock_db.close.assert_called_once()

    @patch("app.tasks.cloning_tasks.AICloneService")
    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_success(self, mock_session_local, mock_clone_cls):
        """任务正常执行：验证真实仿站服务被调用"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        # 模拟 AICloneService.full_clone 返回 CloneResult
        mock_service = mock_clone_cls.return_value
        mock_clone_result = CloneResult(
            reference_url="https://example.com",
            total_pages=25,
            pages=[
                ClonedPage(
                    url="https://example.com",
                    page_type=PageType.HOME,
                    title="Home",
                    original_images=["img1.jpg", "img2.jpg"],
                )
            ],
            originality_score=0.85,
        )
        mock_service.full_clone.return_value = mock_clone_result

        result = clone_site_task.run(
            task_id=1,
            params={
                "source_url": "https://example.com",
                "target_site_id": 1,
                "clone_mode": "full",
                "content_originalize": True,
                "image_redesign": True,
                "restructure": True,
            },
        )

        assert result["status"] == "completed"
        assert result["pages_cloned"] == 25
        assert task.status == "completed"
        assert task.result["source_url"] == "https://example.com"
        assert task.result["clone_mode"] == "full"
        assert task.result["content_originalized"] is True
        assert task.result["images_redesigned"] is True
        assert task.result["structure_restructured"] is True
        # 验证真实仿站服务被调用
        mock_service.full_clone.assert_called_once()

    @patch("app.tasks.cloning_tasks.AICloneService")
    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_no_originalize(self, mock_session_local, mock_clone_cls):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        mock_service = mock_clone_cls.return_value
        mock_clone_result = CloneResult(
            reference_url="https://example.com",
            total_pages=10,
            pages=[],
            originality_score=0.8,
        )
        mock_service.full_clone.return_value = mock_clone_result

        result = clone_site_task.run(
            task_id=1,
            params={
                "source_url": "https://example.com",
                "content_originalize": False,
                "image_redesign": False,
                "restructure": False,
            },
        )

        assert result["status"] == "completed"
        assert task.result["content_originalized"] is False
        assert task.result["images_redesigned"] is False
        assert task.result["structure_restructured"] is False

    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_exception(self, mock_session_local):
        """任务执行异常：commit 失败时标记任务为 failed"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        # commit 调用顺序：
        # 1. task.status="running" 后 commit
        # 2. _add_log 内 commit（异常被吞）
        # 3. _update_progress 内 commit（此处抛异常，传播到外层）
        call_count = {"n": 0}

        def commit_side_effect():
            call_count["n"] += 1
            if call_count["n"] == 3:
                raise Exception("DB error")

        mock_db.commit.side_effect = commit_side_effect
        mock_session_local.return_value = mock_db

        result = clone_site_task.run(
            task_id=1,
            params={"source_url": "https://example.com"},
        )

        assert result["status"] == "failed"


# ==================== 辅助函数测试 ====================

class TestTaskHelpers:
    """任务辅助函数测试"""

    def test_update_progress_with_task(self):
        db = MagicMock()
        task = MagicMock()
        _update_progress(db, task, 50, "half done")
        assert task.progress == 50
        assert task.status_message == "half done"
        db.commit.assert_called_once()

    def test_update_progress_without_task(self):
        db = MagicMock()
        _update_progress(db, None, 50, "msg")
        db.commit.assert_not_called()

    def test_add_log_success(self):
        db = MagicMock()
        _add_log(db, task_id=1, level="info", message="hello", details={"k": "v"})
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_add_log_exception(self):
        db = MagicMock()
        db.commit.side_effect = Exception("DB error")
        # 不应该抛异常
        _add_log(db, task_id=1, level="info", message="hello")
        db.add.assert_called_once()

    def test_add_log_default_details(self):
        db = MagicMock()
        _add_log(db, task_id=1, level="info", message="hello")
        db.add.assert_called_once()
        log_obj = db.add.call_args[0][0]
        assert log_obj.details == {}
