"""
Celery 任务测试 - 使用 mock 隔离 Celery 执行和数据库
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


class FakeRequest:
    """模拟 Celery self.request"""
    id = "fake-celery-id-123"


class FakeQuery:
    """模拟 SQLAlchemy query 链式调用"""

    def __init__(self, first_result=None, all_result=None):
        self._first_result = first_result
        self._all_result = all_result or []

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def first(self):
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


def _make_db_mock(task=None):
    """构造一个 mock db session"""
    db = MagicMock()
    query = FakeQuery(first_result=task)
    db.query.return_value = query
    db.commit = MagicMock()
    db.close = MagicMock()
    db.add = MagicMock()
    db.refresh = MagicMock()
    return db


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
        # pricing_tasks 依赖 PriceEngine，由 test_pricing_tasks 注入后可正常导入
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

    @patch("app.tasks.scraping_tasks.time.sleep", return_value=None)
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_success(self, mock_session_local, mock_sleep):
        """任务正常执行"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        # 调用任务（使用 .run 而非 .delay 避免实际入队）
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

    @patch("app.tasks.scraping_tasks.time.sleep", return_value=None)
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_with_auto_translate(self, mock_session_local, mock_sleep):
        """启用自动翻译"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.scraping_tasks.time.sleep", return_value=None)
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_with_auto_import(self, mock_session_local, mock_sleep):
        """启用自动导入"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.scraping_tasks.time.sleep", return_value=None)
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_cancelled(self, mock_session_local, mock_sleep):
        """任务被取消"""
        task = _make_task_mock(status="cancelled")
        # 第一次查询返回 pending，循环中查询返回 cancelled
        mock_db = MagicMock()
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")

        call_count = {"n": 0}

        def fake_first():
            call_count["n"] += 1
            if call_count["n"] <= 1:
                return pending_task
            return cancelled_task

        mock_db.query.return_value.filter.return_value.first = fake_first
        mock_db.commit = MagicMock()
        mock_session_local.return_value = mock_db

        result = scrape_products_task.run(
            task_id=1,
            params={"url": "https://example.com", "max_products": 100},
        )

        assert result["status"] == "cancelled"
        assert "collected" in result

    @patch("app.tasks.scraping_tasks.time.sleep", return_value=None)
    @patch("app.tasks.scraping_tasks.SessionLocal")
    def test_scrape_task_exception(self, mock_session_local, mock_sleep):
        """任务执行异常"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        # commit 调用顺序：
        # 1. task.status="running" 后 commit（非 try/except）
        # 2. _add_log 内 commit（try/except 包裹，异常被吞）
        # 3. _update_progress 内 commit（非 try/except，此处抛异常）
        # 后续异常处理中的 commit 需要成功
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

    @patch("app.tasks.translation_tasks.time.sleep", return_value=None)
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_success(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.translation_tasks.time.sleep", return_value=None)
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_no_polish(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        result = translate_products_task.run(
            task_id=1,
            params={
                "product_ids": [1, 2],
                "polish": False,
            },
        )

        assert result["status"] == "completed"
        assert task.result["polished"] is False

    @patch("app.tasks.translation_tasks.time.sleep", return_value=None)
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_cancelled(self, mock_session_local, mock_sleep):
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        mock_db = MagicMock()
        call_count = {"n": 0}

        def fake_first():
            call_count["n"] += 1
            if call_count["n"] <= 1:
                return pending_task
            return cancelled_task

        mock_db.query.return_value.filter.return_value.first = fake_first
        mock_db.commit = MagicMock()
        mock_session_local.return_value = mock_db

        result = translate_products_task.run(
            task_id=1,
            params={"product_ids": list(range(100))},
        )

        assert result["status"] == "cancelled"

    @patch("app.tasks.translation_tasks.time.sleep", return_value=None)
    @patch("app.tasks.translation_tasks.SessionLocal")
    def test_translate_task_default_total(self, mock_session_local, mock_sleep):
        """没有 product_ids 时使用默认总数 50"""
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        result = translate_products_task.run(
            task_id=1,
            params={},
        )

        assert result["status"] == "completed"
        assert result["translated_products"] == 50


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

    @patch("app.tasks.import_tasks.time.sleep", return_value=None)
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_success(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.import_tasks.time.sleep", return_value=None)
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_skip_images(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        result = import_to_wordpress_task.run(
            task_id=1,
            params={
                "product_ids": [1, 2],
                "skip_images": True,
            },
        )

        assert result["status"] == "completed"

    @patch("app.tasks.import_tasks.time.sleep", return_value=None)
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_no_publish(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        result = import_to_wordpress_task.run(
            task_id=1,
            params={
                "product_ids": [1, 2],
                "publish": False,
            },
        )

        assert result["status"] == "completed"
        assert task.result["publish"] is False

    @patch("app.tasks.import_tasks.time.sleep", return_value=None)
    @patch("app.tasks.import_tasks.SessionLocal")
    def test_import_task_cancelled(self, mock_session_local, mock_sleep):
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        mock_db = MagicMock()
        call_count = {"n": 0}

        def fake_first():
            call_count["n"] += 1
            if call_count["n"] <= 1:
                return pending_task
            return cancelled_task

        mock_db.query.return_value.filter.return_value.first = fake_first
        mock_db.commit = MagicMock()
        mock_session_local.return_value = mock_db

        result = import_to_wordpress_task.run(
            task_id=1,
            params={"product_ids": list(range(100))},
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

    @patch("app.tasks.seo_tasks.time.sleep", return_value=None)
    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_success(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.seo_tasks.time.sleep", return_value=None)
    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_default_pages(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

        result = optimize_seo_task.run(
            task_id=1,
            params={},
        )

        assert result["status"] == "completed"
        assert result["optimized_pages"] == 20

    @patch("app.tasks.seo_tasks.time.sleep", return_value=None)
    @patch("app.tasks.seo_tasks.SessionLocal")
    def test_seo_task_cancelled(self, mock_session_local, mock_sleep):
        pending_task = _make_task_mock(status="pending")
        cancelled_task = _make_task_mock(status="cancelled")
        mock_db = MagicMock()
        call_count = {"n": 0}

        def fake_first():
            call_count["n"] += 1
            if call_count["n"] <= 1:
                return pending_task
            return cancelled_task

        mock_db.query.return_value.filter.return_value.first = fake_first
        mock_db.commit = MagicMock()
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.cloning_tasks.time.sleep", return_value=None)
    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_success(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.cloning_tasks.time.sleep", return_value=None)
    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_no_originalize(self, mock_session_local, mock_sleep):
        task = _make_task_mock()
        mock_db = _make_db_mock(task=task)
        mock_session_local.return_value = mock_db

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

    @patch("app.tasks.cloning_tasks.time.sleep", return_value=None)
    @patch("app.tasks.cloning_tasks.SessionLocal")
    def test_clone_task_exception(self, mock_session_local, mock_sleep):
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
