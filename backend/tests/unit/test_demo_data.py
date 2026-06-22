"""
示例数据加载模块测试
覆盖 demo_data.py 的所有功能：用户、站点、产品、任务、SEO、AI模型、代理配置
"""
import pytest
from datetime import datetime

from app.demo.demo_data import (
    get_demo_users,
    get_demo_sites,
    get_demo_products,
    get_demo_tasks,
    get_demo_ai_models,
    get_demo_proxy_configs,
    get_demo_seo_config,
    get_demo_seo_audits,
    clean_demo_data,
    load_demo_data,
    DEMO_PASSWORD,
)
from app.models.user import User
from app.models.site import Site
from app.models.product import Product
from app.models.task import Task
from app.models.seo import SEOAudit, SEOSetting


# ==================== 用户数据测试 ====================

class TestDemoUsers:
    """示例用户数据测试"""

    def test_get_demo_users_count(self):
        """测试示例用户数量为3"""
        users = get_demo_users()
        assert len(users) == 3

    def test_demo_users_roles(self):
        """测试示例用户包含 admin、editor、viewer 三个角色"""
        users = get_demo_users()
        usernames = [u["username"] for u in users]
        assert "admin" in usernames
        assert "editor" in usernames
        assert "viewer" in usernames

    def test_admin_user_is_admin(self):
        """测试 admin 用户具有管理员权限"""
        users = get_demo_users()
        admin = next(u for u in users if u["username"] == "admin")
        assert admin["is_admin"] is True
        assert admin["is_superuser"] is True

    def test_editor_user_not_admin(self):
        """测试 editor 用户不是管理员"""
        users = get_demo_users()
        editor = next(u for u in users if u["username"] == "editor")
        assert editor["is_admin"] is False
        assert editor["is_superuser"] is False

    def test_demo_users_have_hashed_password(self):
        """测试示例用户密码已哈希"""
        users = get_demo_users()
        for user in users:
            assert user["hashed_password"] != DEMO_PASSWORD
            assert user["hashed_password"].startswith("$2b$")

    def test_demo_users_email_domain(self):
        """测试示例用户邮箱使用 demo 域名"""
        users = get_demo_users()
        for user in users:
            assert user["email"].endswith("@wpforge.demo")

    def test_demo_users_are_active(self):
        """测试示例用户都是活跃的"""
        users = get_demo_users()
        for user in users:
            assert user["is_active"] is True


# ==================== 站点数据测试 ====================

class TestDemoSites:
    """示例站点数据测试"""

    def test_get_demo_sites_count(self):
        """测试示例站点数量为3"""
        sites = get_demo_sites(admin_user_id=1)
        assert len(sites) == 3

    def test_demo_sites_different_types(self):
        """测试示例站点包含博客、电商、企业站三种类型"""
        sites = get_demo_sites(admin_user_id=1)
        names = [s["name"] for s in sites]
        # 博客
        assert any("博客" in n or "TechBlog" in n for n in names)
        # 电商
        assert any("电商" in n or "ShopExpress" in n for n in names)
        # 企业站
        assert any("企业" in n or "CorpSite" in n for n in names)

    def test_demo_sites_have_complete_config(self):
        """测试示例站点有完整配置"""
        sites = get_demo_sites(admin_user_id=1)
        for site in sites:
            assert site["name"]
            assert site["url"]
            assert site["wp_url"]
            assert site["wp_username"]
            assert site["wp_password"]
            assert site["language"]
            assert site["currency"]
            assert site["page_builder"]
            assert site["status"] == "active"

    def test_demo_sites_user_id(self):
        """测试示例站点关联到指定用户"""
        sites = get_demo_sites(admin_user_id=42)
        for site in sites:
            assert site["user_id"] == 42

    def test_ecommerce_site_has_woocommerce_config(self):
        """测试电商站点有WooCommerce配置"""
        sites = get_demo_sites(admin_user_id=1)
        shop = next(s for s in sites if "ShopExpress" in s["name"])
        assert shop["wc_consumer_key"]
        assert shop["wc_consumer_secret"]


# ==================== 产品数据测试 ====================

class TestDemoProducts:
    """示例产品数据测试"""

    def test_get_demo_products_count(self):
        """测试示例产品数量为10"""
        products = get_demo_products(site_id=1)
        assert len(products) == 10

    def test_demo_products_have_images(self):
        """测试示例产品包含图片URL"""
        products = get_demo_products(site_id=1)
        for p in products:
            assert p["featured_image"]
            assert p["featured_image"].startswith("http")

    def test_demo_products_have_prices(self):
        """测试示例产品包含价格信息"""
        products = get_demo_products(site_id=1)
        for p in products:
            assert p["regular_price"] is not None
            assert p["regular_price"] > 0

    def test_demo_products_have_categories(self):
        """测试示例产品包含分类"""
        products = get_demo_products(site_id=1)
        for p in products:
            assert isinstance(p["categories"], list)
            assert len(p["categories"]) > 0

    def test_demo_products_have_descriptions(self):
        """测试示例产品包含描述"""
        products = get_demo_products(site_id=1)
        for p in products:
            assert p["description"]
            assert p["short_description"]

    def test_demo_products_have_sku(self):
        """测试示例产品包含SKU"""
        products = get_demo_products(site_id=1)
        for p in products:
            assert p["sku"]
            assert p["sku"].strip()

    def test_demo_products_site_id(self):
        """测试示例产品关联到指定站点"""
        products = get_demo_products(site_id=99)
        for p in products:
            assert p["site_id"] == 99

    def test_demo_products_have_source_info(self):
        """测试示例产品包含来源信息"""
        products = get_demo_products(site_id=1)
        for p in products:
            assert p["source_url"]
            assert p["source_site"]


# ==================== 任务数据测试 ====================

class TestDemoTasks:
    """示例任务数据测试"""

    def test_get_demo_tasks_count(self):
        """测试示例任务数量为5"""
        tasks = get_demo_tasks(user_id=1, site_id=1)
        assert len(tasks) == 5

    def test_demo_tasks_different_statuses(self):
        """测试示例任务包含不同状态"""
        tasks = get_demo_tasks(user_id=1, site_id=1)
        statuses = set(t["status"] for t in tasks)
        assert "pending" in statuses
        assert "running" in statuses
        assert "completed" in statuses
        assert "failed" in statuses

    def test_demo_tasks_have_user_and_site(self):
        """测试示例任务关联到用户和站点"""
        tasks = get_demo_tasks(user_id=10, site_id=20)
        for t in tasks:
            assert t["user_id"] == 10
            assert t["site_id"] == 20

    def test_failed_task_has_error_message(self):
        """测试失败任务有错误信息"""
        tasks = get_demo_tasks(user_id=1, site_id=1)
        failed = next(t for t in tasks if t["status"] == "failed")
        assert failed["error_message"]

    def test_completed_task_has_result(self):
        """测试完成任务有结果"""
        tasks = get_demo_tasks(user_id=1, site_id=1)
        completed = next(t for t in tasks if t["status"] == "completed")
        assert completed["result"]


# ==================== AI模型和代理配置测试 ====================

class TestDemoConfigs:
    """示例配置数据测试"""

    def test_ai_models_count(self):
        """测试AI模型配置数量为4"""
        models = get_demo_ai_models()
        assert len(models) == 4

    def test_ai_models_providers(self):
        """测试AI模型包含 OpenAI、Anthropic、Gemini、Ollama"""
        models = get_demo_ai_models()
        providers = set(m["provider"] for m in models)
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers
        assert "ollama" in providers

    def test_proxy_configs_count(self):
        """测试代理配置数量为3"""
        proxies = get_demo_proxy_configs()
        assert len(proxies) == 3

    def test_proxy_configs_protocols(self):
        """测试代理配置包含 HTTP、HTTPS、SOCKS5"""
        proxies = get_demo_proxy_configs()
        protocols = set(p["protocol"] for p in proxies)
        assert "http" in protocols
        assert "https" in protocols
        assert "socks5" in protocols

    def test_seo_config_has_required_fields(self):
        """测试SEO配置包含必要字段"""
        config = get_demo_seo_config(site_id=1)
        assert config["site_title"]
        assert config["site_description"]
        assert config["site_keywords"]
        assert config["title_template"]
        assert config["og_image"]

    def test_seo_audits_count(self):
        """测试SEO审计数据存在"""
        audits = get_demo_seo_audits(site_id=1)
        assert len(audits) >= 1
        assert audits[0]["overall_score"] > 0


# ==================== 数据加载和清理测试 ====================

class TestDemoDataLoading:
    """示例数据加载和清理测试"""

    def test_load_demo_data_returns_stats(self, db):
        """测试加载示例数据返回统计信息"""
        stats = load_demo_data(db)
        assert "users" in stats
        assert "sites" in stats
        assert "products" in stats
        assert "tasks" in stats
        assert stats["users"] == 3
        assert stats["sites"] == 3
        assert stats["products"] == 10
        assert stats["tasks"] == 5

    def test_load_demo_data_creates_users(self, db):
        """测试加载后数据库中有示例用户"""
        load_demo_data(db)
        users = db.query(User).filter(User.email.like("%@wpforge.demo%")).all()
        assert len(users) == 3

    def test_load_demo_data_creates_sites(self, db):
        """测试加载后数据库中有示例站点"""
        load_demo_data(db)
        sites = db.query(Site).filter(Site.url.like("%.wpforge.demo%")).all()
        assert len(sites) == 3

    def test_load_demo_data_creates_products(self, db):
        """测试加载后数据库中有示例产品"""
        load_demo_data(db)
        products = db.query(Product).filter(Product.source_site == "source-example.com").all()
        assert len(products) == 10

    def test_load_demo_data_creates_tasks(self, db):
        """测试加载后数据库中有示例任务"""
        load_demo_data(db)
        tasks = db.query(Task).filter(Task.name.like("采集 - %")).all()
        assert len(tasks) >= 1

    def test_load_demo_data_creates_seo_settings(self, db):
        """测试加载后数据库中有SEO设置"""
        load_demo_data(db)
        settings = db.query(SEOSetting).filter(SEOSetting.site_title.like("%ShopExpress%")).all()
        assert len(settings) == 1

    def test_load_demo_data_is_idempotent(self, db):
        """测试重复加载不会产生重复数据"""
        load_demo_data(db)
        load_demo_data(db)
        users = db.query(User).filter(User.email.like("%@wpforge.demo%")).all()
        sites = db.query(Site).filter(Site.url.like("%.wpforge.demo%")).all()
        products = db.query(Product).filter(Product.source_site == "source-example.com").all()
        assert len(users) == 3
        assert len(sites) == 3
        assert len(products) == 10

    def test_clean_demo_data_removes_all(self, db):
        """测试清理函数能移除所有示例数据"""
        load_demo_data(db)
        cleaned = clean_demo_data(db)
        assert cleaned["users"] == 3
        assert cleaned["sites"] == 3
        assert cleaned["products"] == 10
        # 验证数据库中已无示例数据
        users = db.query(User).filter(User.email.like("%@wpforge.demo%")).all()
        assert len(users) == 0

    def test_clean_demo_data_on_empty_db(self, db):
        """测试在空数据库上清理不报错"""
        cleaned = clean_demo_data(db)
        assert cleaned["users"] == 0
        assert cleaned["sites"] == 0
