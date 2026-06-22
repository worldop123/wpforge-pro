"""
WPForge 示例数据加载模块
提供可重复加载的示例数据，用于演示和开发测试

包含：
- 3个示例站点（博客、电商、企业站）
- 10个示例产品
- 5个示例采集任务
- 示例用户（admin、editor、viewer）
- 示例AI模型配置
- 示例代理配置
- 示例SEO配置
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.site import Site
from app.models.product import Product, ProductCategory
from app.models.task import Task, TaskLog
from app.models.seo import SEOAudit, SEOSetting
from app.core.logging import get_logger

logger = get_logger(__name__)

# 示例用户密码（统一使用，方便演示）
DEMO_PASSWORD = "Demo@123456"


def get_demo_users() -> List[Dict[str, Any]]:
    """获取示例用户数据"""
    return [
        {
            "username": "admin",
            "email": "admin@wpforge.demo",
            "full_name": "系统管理员",
            "hashed_password": get_password_hash(DEMO_PASSWORD),
            "is_active": True,
            "is_admin": True,
            "is_superuser": True,
        },
        {
            "username": "editor",
            "email": "editor@wpforge.demo",
            "full_name": "内容编辑",
            "hashed_password": get_password_hash(DEMO_PASSWORD),
            "is_active": True,
            "is_admin": False,
            "is_superuser": False,
        },
        {
            "username": "viewer",
            "email": "viewer@wpforge.demo",
            "full_name": "只读用户",
            "hashed_password": get_password_hash(DEMO_PASSWORD),
            "is_active": True,
            "is_admin": False,
            "is_superuser": False,
        },
    ]


def get_demo_sites(admin_user_id: int) -> List[Dict[str, Any]]:
    """获取示例站点数据"""
    return [
        {
            "name": "技术博客 - TechBlog",
            "url": "https://blog.wpforge.demo",
            "description": "一个专注于Web开发技术的博客站点，分享前端、后端、DevOps等技术文章。",
            "wp_url": "https://blog.wpforge.demo",
            "wp_username": "admin",
            "wp_password": "blog-app-password-123",
            "language": "zh-CN",
            "currency": "CNY",
            "price_markup": 0,
            "page_builder": "gutenberg",
            "status": "active",
            "user_id": admin_user_id,
            "config": {"blog_type": "tech", "posts_per_page": 10},
        },
        {
            "name": "跨境电商 - ShopExpress",
            "url": "https://shop.wpforge.demo",
            "description": "面向欧美市场的跨境电商独立站，主营3C数码和家居用品。",
            "wp_url": "https://shop.wpforge.demo",
            "wp_username": "admin",
            "wp_password": "shop-app-password-456",
            "wc_consumer_key": "ck_demo_consumer_key_1234567890",
            "wc_consumer_secret": "cs_demo_consumer_secret_0987654321",
            "language": "en-US",
            "currency": "USD",
            "price_markup": 35,
            "page_builder": "elementor",
            "status": "active",
            "user_id": admin_user_id,
            "config": {"shop_type": "cross_border", "shipping_zones": 3},
        },
        {
            "name": "企业官网 - CorpSite",
            "url": "https://corp.wpforge.demo",
            "description": "某科技公司企业官网，展示公司介绍、产品服务、新闻动态和联系方式。",
            "wp_url": "https://corp.wpforge.demo",
            "wp_username": "admin",
            "wp_password": "corp-app-password-789",
            "language": "zh-CN",
            "currency": "CNY",
            "price_markup": 0,
            "page_builder": "bricks",
            "status": "active",
            "user_id": admin_user_id,
            "config": {"site_type": "corporate", "contact_form": True},
        },
    ]


def get_demo_products(site_id: int, task_id: int = None) -> List[Dict[str, Any]]:
    """获取示例产品数据"""
    base_time = datetime.utcnow()
    products = []
    categories_map = {
        "electronics": ["电子产品", "3C数码"],
        "home": ["家居生活", "日用品"],
        "fashion": ["时尚服饰", "配饰"],
    }

    product_templates = [
        {
            "name": "无线蓝牙耳机 Pro Max",
            "sku": "WBH-PM-001",
            "description": "主动降噪无线蓝牙耳机，支持LDAC高清音质，续航36小时，IPX5防水等级。配备定制动圈单元，低频浑厚有力，高频清晰透亮。",
            "short_description": "主动降噪 | LDAC高清音质 | 36小时续航",
            "regular_price": 199.99,
            "sale_price": 149.99,
            "currency": "USD",
            "stock_quantity": 500,
            "categories": categories_map["electronics"],
            "tags": ["蓝牙耳机", "降噪", "热销"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/headphone-promax.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/headphone-1.jpg",
                "https://shop.wpforge.demo/wp-content/uploads/headphone-2.jpg",
            ],
            "source_url": "https://source-example.com/products/wbh-pm-001",
            "source_site": "source-example.com",
        },
        {
            "name": "智能手表 Series 7",
            "sku": "SW-S7-002",
            "description": "1.9英寸AMOLED高清大屏，支持血氧监测、心率监测、睡眠追踪。100+运动模式，5ATM防水，14天超长续航。",
            "short_description": "AMOLED大屏 | 血氧监测 | 14天续航",
            "regular_price": 249.99,
            "sale_price": 199.99,
            "currency": "USD",
            "stock_quantity": 300,
            "categories": categories_map["electronics"],
            "tags": ["智能手表", "健康监测"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/watch-s7.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/watch-1.jpg",
                "https://shop.wpforge.demo/wp-content/uploads/watch-2.jpg",
            ],
            "source_url": "https://source-example.com/products/sw-s7-002",
            "source_site": "source-example.com",
        },
        {
            "name": "便携式充电宝 20000mAh",
            "sku": "PB-20K-003",
            "description": "20000mAh大容量，支持PD 65W快充，可为笔记本充电。双向快充，Type-C接口，LED数显电量。",
            "short_description": "20000mAh | 65W快充 | 可充笔记本",
            "regular_price": 59.99,
            "sale_price": 39.99,
            "currency": "USD",
            "stock_quantity": 1000,
            "categories": categories_map["electronics"],
            "tags": ["充电宝", "快充"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/powerbank-20k.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/powerbank-1.jpg",
            ],
            "source_url": "https://source-example.com/products/pb-20k-003",
            "source_site": "source-example.com",
        },
        {
            "name": "机械键盘 RGB背光 87键",
            "sku": "KB-RGB-004",
            "description": "87键紧凑布局，红轴机械键盘，RGB全彩背光，Type-C可换线设计，PBT键帽耐磨持久。",
            "short_description": "红轴 | RGB背光 | PBT键帽",
            "regular_price": 79.99,
            "sale_price": 64.99,
            "currency": "USD",
            "stock_quantity": 200,
            "categories": categories_map["electronics"],
            "tags": ["机械键盘", "RGB"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/keyboard-rgb.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/keyboard-1.jpg",
            ],
            "source_url": "https://source-example.com/products/kb-rgb-004",
            "source_site": "source-example.com",
        },
        {
            "name": "北欧风格台灯",
            "sku": "HL-ND-005",
            "description": "北欧极简设计风格台灯，三档色温调节，无极调光，USB供电，护眼LED光源。",
            "short_description": "北欧风格 | 三档色温 | 护眼LED",
            "regular_price": 45.99,
            "sale_price": 32.99,
            "currency": "USD",
            "stock_quantity": 150,
            "categories": categories_map["home"],
            "tags": ["台灯", "北欧", "护眼"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/lamp-nd.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/lamp-1.jpg",
            ],
            "source_url": "https://source-example.com/products/hl-nd-005",
            "source_site": "source-example.com",
        },
        {
            "name": "记忆棉颈椎枕",
            "sku": "PW-MF-006",
            "description": "慢回弹记忆棉材质，人体工学曲线设计，有效支撑颈椎，透气亲肤枕套，可拆洗。",
            "short_description": "记忆棉 | 人体工学 | 可拆洗",
            "regular_price": 35.99,
            "sale_price": 25.99,
            "currency": "USD",
            "stock_quantity": 800,
            "categories": categories_map["home"],
            "tags": ["枕头", "记忆棉"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/pillow-mf.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/pillow-1.jpg",
            ],
            "source_url": "https://source-example.com/products/pw-mf-006",
            "source_site": "source-example.com",
        },
        {
            "name": "不锈钢保温杯 500ml",
            "sku": "CUP-SS-007",
            "description": "316不锈钢内胆，12小时保温保冷，防漏密封杯盖，磨砂质感外观，便携提手。",
            "short_description": "316不锈钢 | 12小时保温 | 防漏",
            "regular_price": 29.99,
            "sale_price": 19.99,
            "currency": "USD",
            "stock_quantity": 2000,
            "categories": categories_map["home"],
            "tags": ["保温杯", "不锈钢"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/cup-ss.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/cup-1.jpg",
            ],
            "source_url": "https://source-example.com/products/cup-ss-007",
            "source_site": "source-example.com",
        },
        {
            "name": "真皮商务皮带",
            "sku": "BLT-LT-008",
            "description": "头层牛皮材质，自动扣设计，商务休闲两用，多色可选，精美礼盒包装。",
            "short_description": "头层牛皮 | 自动扣 | 礼盒装",
            "regular_price": 49.99,
            "sale_price": 34.99,
            "currency": "USD",
            "stock_quantity": 300,
            "categories": categories_map["fashion"],
            "tags": ["皮带", "真皮", "商务"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/belt-lt.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/belt-1.jpg",
            ],
            "source_url": "https://source-example.com/products/blt-lt-008",
            "source_site": "source-example.com",
        },
        {
            "name": "防蓝光近视眼镜框",
            "sku": "GLS-AB-009",
            "description": "TR90超轻记忆镜框，防蓝光镜片，适合长时间使用电脑人群，附带度数定制服务。",
            "short_description": "TR90镜框 | 防蓝光 | 度数定制",
            "regular_price": 39.99,
            "sale_price": 27.99,
            "currency": "USD",
            "stock_quantity": 400,
            "categories": categories_map["fashion"],
            "tags": ["眼镜", "防蓝光"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/glasses-ab.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/glasses-1.jpg",
            ],
            "source_url": "https://source-example.com/products/gls-ab-009",
            "source_site": "source-example.com",
        },
        {
            "name": "运动健身手套",
            "sku": "GLV-SP-010",
            "description": "透气网眼面料，硅胶防滑掌垫，腕部魔术贴固定，适合举重、骑行等运动。",
            "short_description": "透气 | 防滑 | 运动健身",
            "regular_price": 19.99,
            "sale_price": 14.99,
            "currency": "USD",
            "stock_quantity": 600,
            "categories": categories_map["fashion"],
            "tags": ["手套", "运动"],
            "featured_image": "https://shop.wpforge.demo/wp-content/uploads/glove-sp.jpg",
            "gallery_images": [
                "https://shop.wpforge.demo/wp-content/uploads/glove-1.jpg",
            ],
            "source_url": "https://source-example.com/products/glv-sp-010",
            "source_site": "source-example.com",
        },
    ]

    for i, tmpl in enumerate(product_templates):
        products.append({
            **tmpl,
            "slug": tmpl["sku"].lower().replace("-", "-"),
            "price": tmpl["sale_price"] or tmpl["regular_price"],
            "in_stock": True,
            "manage_stock": True,
            "images": [{"src": tmpl["featured_image"], "alt": tmpl["name"]}],
            "attributes": [],
            "variations": [],
            "is_variable": False,
            "translated": i % 2 == 0,  # 一半已翻译
            "translation_language": "zh-CN" if i % 2 == 0 else None,
            "seo_title": tmpl["name"][:60],
            "seo_description": tmpl["short_description"][:160],
            "seo_keywords": ",".join(tmpl["tags"]),
            "wp_status": "publish" if i < 5 else "draft",
            "status": "published" if i < 5 else "draft",
            "site_id": site_id,
            "task_id": task_id,
        })

    return products


def get_demo_tasks(user_id: int, site_id: int) -> List[Dict[str, Any]]:
    """获取示例任务数据（不同状态）"""
    now = datetime.utcnow()
    return [
        {
            "name": "采集 - ShopExpress 全站产品",
            "task_type": "scraping",
            "status": "pending",
            "progress": 0,
            "params": {"url": "https://source-example.com", "max_products": 100, "auto_translate": True},
            "result": {},
            "total_items": 100,
            "processed_items": 0,
            "failed_items": 0,
            "priority": 5,
            "site_id": site_id,
            "user_id": user_id,
        },
        {
            "name": "翻译 - 批量产品描述翻译",
            "task_type": "translation",
            "status": "running",
            "progress": 45.0,
            "params": {"target_language": "zh-CN", "engine": "ai"},
            "result": {},
            "total_items": 50,
            "processed_items": 22,
            "failed_items": 1,
            "started_at": now - timedelta(minutes=15),
            "priority": 7,
            "site_id": site_id,
            "user_id": user_id,
        },
        {
            "name": "导入 - WordPress产品发布",
            "task_type": "import",
            "status": "completed",
            "progress": 100,
            "params": {"site_id": site_id, "publish": True},
            "result": {"imported": 30, "success": True},
            "total_items": 30,
            "processed_items": 30,
            "failed_items": 0,
            "started_at": now - timedelta(hours=2),
            "completed_at": now - timedelta(hours=1, minutes=50),
            "duration": 600.0,
            "priority": 5,
            "site_id": site_id,
            "user_id": user_id,
        },
        {
            "name": "SEO - 全站SEO审计",
            "task_type": "seo",
            "status": "failed",
            "progress": 30,
            "params": {"deep_audit": True},
            "result": {},
            "error_message": "连接超时：目标站点无法访问",
            "total_items": 20,
            "processed_items": 6,
            "failed_items": 14,
            "started_at": now - timedelta(hours=5),
            "completed_at": now - timedelta(hours=4, minutes=55),
            "duration": 300.0,
            "priority": 3,
            "site_id": site_id,
            "user_id": user_id,
        },
        {
            "name": "采集 - 竞品价格监控",
            "task_type": "scraping",
            "status": "pending",
            "progress": 0,
            "params": {"url": "https://competitor-example.com", "scrape_reviews": True},
            "result": {},
            "total_items": 50,
            "processed_items": 0,
            "failed_items": 0,
            "priority": 8,
            "site_id": site_id,
            "user_id": user_id,
        },
    ]


def get_demo_ai_models() -> List[Dict[str, Any]]:
    """获取示例AI模型配置"""
    return [
        {
            "id": "openai",
            "name": "OpenAI",
            "provider": "openai",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-demo-openai-key-placeholder",
            "max_tokens": 4096,
            "temperature": 0.7,
            "is_active": True,
            "is_default": True,
        },
        {
            "id": "anthropic",
            "name": "Anthropic Claude",
            "provider": "anthropic",
            "model": "claude-3-5-sonnet",
            "base_url": "https://api.anthropic.com",
            "api_key": "sk-ant-demo-key-placeholder",
            "max_tokens": 4096,
            "temperature": 0.7,
            "is_active": True,
            "is_default": False,
        },
        {
            "id": "gemini",
            "name": "Google Gemini",
            "provider": "google",
            "model": "gemini-1.5-pro",
            "base_url": "https://generativelanguage.googleapis.com",
            "api_key": "AIza-demo-gemini-key-placeholder",
            "max_tokens": 8192,
            "temperature": 0.7,
            "is_active": True,
            "is_default": False,
        },
        {
            "id": "ollama",
            "name": "Ollama (本地)",
            "provider": "ollama",
            "model": "llama3.1",
            "base_url": "http://localhost:11434",
            "api_key": "",
            "max_tokens": 4096,
            "temperature": 0.7,
            "is_active": False,
            "is_default": False,
        },
    ]


def get_demo_proxy_configs() -> List[Dict[str, Any]]:
    """获取示例代理配置"""
    return [
        {
            "id": "http-proxy",
            "name": "HTTP代理 - 美国",
            "protocol": "http",
            "host": "192.168.1.100",
            "port": 8080,
            "username": "demo_user",
            "password": "demo_pass_http",
            "country": "US",
            "provider": "custom",
            "is_active": True,
        },
        {
            "id": "https-proxy",
            "name": "HTTPS代理 - 日本",
            "protocol": "https",
            "host": "203.0.113.50",
            "port": 443,
            "username": "demo_user",
            "password": "demo_pass_https",
            "country": "JP",
            "provider": "custom",
            "is_active": True,
        },
        {
            "id": "socks5-proxy",
            "name": "SOCKS5代理 - 德国",
            "protocol": "socks5",
            "host": "198.51.100.25",
            "port": 1080,
            "username": "demo_user",
            "password": "demo_pass_socks5",
            "country": "DE",
            "provider": "custom",
            "is_active": True,
        },
    ]


def get_demo_seo_config(site_id: int) -> Dict[str, Any]:
    """获取示例SEO配置"""
    return {
        "site_id": site_id,
        "site_title": "ShopExpress - 全球精选好物",
        "site_description": "ShopExpress致力于为全球消费者提供高品质的3C数码和家居用品，享受便捷的跨境购物体验。",
        "site_keywords": "跨境电商,3C数码,家居用品,蓝牙耳机,智能手表",
        "title_template": "{title} | ShopExpress",
        "description_template": "{description} - 立即在ShopExpress选购，享受全球配送。",
        "og_image": "https://shop.wpforge.demo/wp-content/uploads/og-image.jpg",
        "twitter_card": "summary_large_image",
        "noindex": False,
        "nofollow": False,
        "advanced_settings": {
            "breadcrumb_enabled": True,
            "schema_markup": True,
            "sitemap_auto_submit": True,
            "robots_txt": "User-agent: *\nAllow: /",
        },
    }


def get_demo_seo_audits(site_id: int) -> List[Dict[str, Any]]:
    """获取示例SEO审计数据"""
    return [
        {
            "url": "https://shop.wpforge.demo/",
            "site_id": site_id,
            "overall_score": 85,
            "content_score": 90,
            "technical_score": 80,
            "performance_score": 78,
            "mobile_score": 88,
            "meta_data": {"title": "ShopExpress - 全球精选好物", "description": "跨境电商独立站"},
            "headings": [{"tag": "h1", "text": "全球精选好物", "count": 1}],
            "images": [{"src": "/logo.png", "alt": "ShopExpress", "has_alt": True}],
            "links": [{"href": "/products", "internal": True, "count": 15}],
            "performance": {"lcp": 2.1, "fid": 50, "cls": 0.05},
            "issues": [{"type": "warning", "message": "部分图片缺少ALT属性"}],
            "recommendations": [
                {"priority": "high", "message": "优化首屏加载速度"},
                {"priority": "medium", "message": "添加更多内链"},
            ],
            "status": "completed",
        },
    ]


def clean_demo_data(db: Session) -> Dict[str, int]:
    """清理示例数据（先清理再导入，保证可重复加载）

    返回各表清理的记录数
    """
    deleted_counts = {}

    # 按依赖顺序清理（先清理子表再清理父表）
    # 清理SEO设置（通过关联的站点ID清理）
    demo_site_ids_subquery = db.query(Site.id).filter(
        Site.url.like("%.wpforge.demo%")
    ).subquery()
    deleted_counts["seo_settings"] = db.query(SEOSetting).filter(
        SEOSetting.site_id.in_(demo_site_ids_subquery)
    ).delete(synchronize_session=False)

    # 清理SEO审计
    deleted_counts["seo_audits"] = db.query(SEOAudit).filter(
        SEOAudit.url.like("%.wpforge.demo%")
    ).delete(synchronize_session=False)

    # 清理任务日志
    deleted_counts["task_logs"] = db.query(TaskLog).filter(
        TaskLog.task_id.in_(
            db.query(Task.id).filter(Task.name.like("%Demo%")).union(
                db.query(Task.id).filter(Task.name.like("采集 - %")),
                db.query(Task.id).filter(Task.name.like("翻译 - %")),
                db.query(Task.id).filter(Task.name.like("导入 - %")),
                db.query(Task.id).filter(Task.name.like("SEO - %")),
            )
        )
    ).delete(synchronize_session=False)

    # 清理产品
    deleted_counts["products"] = db.query(Product).filter(
        Product.source_site == "source-example.com"
    ).delete(synchronize_session=False)

    # 清理任务
    deleted_counts["tasks"] = db.query(Task).filter(
        Task.name.like("采集 - %") |
        Task.name.like("翻译 - %") |
        Task.name.like("导入 - %") |
        Task.name.like("SEO - %")
    ).delete(synchronize_session=False)

    # 清理站点
    deleted_counts["sites"] = db.query(Site).filter(
        Site.url.like("%.wpforge.demo%")
    ).delete(synchronize_session=False)

    # 清理用户
    deleted_counts["users"] = db.query(User).filter(
        User.email.like("%@wpforge.demo%")
    ).delete(synchronize_session=False)

    db.commit()
    return deleted_counts


def load_demo_data(db: Session) -> Dict[str, Any]:
    """加载示例数据（可重复执行，会先清理旧数据）

    返回加载统计信息
    """
    logger.info("开始加载示例数据...")

    # 1. 清理旧数据
    cleaned = clean_demo_data(db)
    logger.info(f"已清理旧数据: {cleaned}")

    # 2. 加载用户
    users_data = get_demo_users()
    created_users = {}
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        db.flush()
        created_users[user.username] = user
    db.commit()
    logger.info(f"已加载 {len(created_users)} 个示例用户")

    admin_user = created_users["admin"]

    # 3. 加载站点
    sites_data = get_demo_sites(admin_user.id)
    created_sites = []
    for site_data in sites_data:
        site = Site(**site_data)
        db.add(site)
        db.flush()
        created_sites.append(site)
    db.commit()
    logger.info(f"已加载 {len(created_sites)} 个示例站点")

    # 使用电商站点作为产品关联站点
    shop_site = next((s for s in created_sites if "ShopExpress" in s.name), created_sites[0])

    # 4. 加载任务（先创建任务，因为产品可能关联任务）
    tasks_data = get_demo_tasks(admin_user.id, shop_site.id)
    created_tasks = []
    for task_data in tasks_data:
        task = Task(**task_data)
        db.add(task)
        db.flush()
        created_tasks.append(task)
    db.commit()
    logger.info(f"已加载 {len(created_tasks)} 个示例任务")

    # 使用第一个任务关联产品
    demo_task = created_tasks[0] if created_tasks else None

    # 5. 加载产品
    products_data = get_demo_products(shop_site.id, demo_task.id if demo_task else None)
    for product_data in products_data:
        product = Product(**product_data)
        db.add(product)
    db.commit()
    logger.info(f"已加载 {len(products_data)} 个示例产品")

    # 6. 加载SEO设置
    seo_config = get_demo_seo_config(shop_site.id)
    seo_setting = SEOSetting(**seo_config)
    db.add(seo_setting)
    db.commit()
    logger.info("已加载示例SEO配置")

    # 7. 加载SEO审计
    seo_audits_data = get_demo_seo_audits(shop_site.id)
    for audit_data in seo_audits_data:
        audit = SEOAudit(**audit_data)
        db.add(audit)
    db.commit()
    logger.info(f"已加载 {len(seo_audits_data)} 个示例SEO审计")

    # 8. AI模型和代理配置作为返回数据（这些是静态配置，不持久化到数据库）
    ai_models = get_demo_ai_models()
    proxy_configs = get_demo_proxy_configs()

    stats = {
        "users": len(created_users),
        "sites": len(created_sites),
        "products": len(products_data),
        "tasks": len(created_tasks),
        "seo_settings": 1,
        "seo_audits": len(seo_audits_data),
        "ai_models": len(ai_models),
        "proxy_configs": len(proxy_configs),
        "cleaned": cleaned,
    }

    logger.info(f"示例数据加载完成: {stats}")
    return stats
