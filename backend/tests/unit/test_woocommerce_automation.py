"""
WooCommerce自动化服务测试

覆盖:
- ProductReview, Coupon, ShippingZone, PaymentGateway, ProductQA 数据类
- ReviewGenerator
- CouponGenerator
- QAGenerator
- WooCommerceAutomationService
- wc_automation_service 全局实例
"""
import pytest
from datetime import datetime

from app.services.woocommerce_automation import (
    ProductReview,
    Coupon,
    ShippingZone,
    PaymentGateway,
    ProductQA,
    ReviewGenerator,
    CouponGenerator,
    QAGenerator,
    WooCommerceAutomationService,
    wc_automation_service,
)


# ---------------------------------------------------------------------------
# ProductReview 数据类
# ---------------------------------------------------------------------------
class TestProductReview:
    def test_defaults(self):
        review = ProductReview()
        assert review.id is None
        assert review.product_id == 0
        assert review.author == ""
        assert review.email == ""
        assert review.avatar == ""
        assert review.rating == 5
        assert review.content == ""
        assert review.date == ""
        assert review.verified is True
        assert review.helpful == 0
        assert review.not_helpful == 0
        assert review.images == []
        assert review.metadata == {}

    def test_custom_values(self):
        review = ProductReview(
            id=1,
            product_id=100,
            author="John",
            email="john@test.com",
            rating=4,
            content="Great product",
            verified=False,
            helpful=10,
        )
        assert review.id == 1
        assert review.product_id == 100
        assert review.author == "John"
        assert review.rating == 4
        assert review.verified is False
        assert review.helpful == 10

    def test_independent_lists(self):
        a = ProductReview()
        b = ProductReview()
        a.images.append("img.jpg")
        assert b.images == []


# ---------------------------------------------------------------------------
# Coupon 数据类
# ---------------------------------------------------------------------------
class TestCoupon:
    def test_defaults(self):
        c = Coupon()
        assert c.code == ""
        assert c.discount_type == "percent"
        assert c.amount == 0.0
        assert c.description == ""
        assert c.date_expires is None
        assert c.usage_count == 0
        assert c.usage_limit is None
        assert c.usage_limit_per_user is None
        assert c.minimum_amount is None
        assert c.maximum_amount is None
        assert c.individual_use is False
        assert c.exclude_sale_items is False
        assert c.product_ids == []
        assert c.exclude_product_ids == []
        assert c.categories == []
        assert c.exclude_categories == []
        assert c.email_restrictions == []
        assert c.free_shipping is False

    def test_custom_values(self):
        c = Coupon(
            code="SAVE10",
            discount_type="fixed_cart",
            amount=10.0,
            usage_limit=100,
            free_shipping=True,
        )
        assert c.code == "SAVE10"
        assert c.discount_type == "fixed_cart"
        assert c.amount == 10.0
        assert c.usage_limit == 100
        assert c.free_shipping is True


# ---------------------------------------------------------------------------
# ShippingZone 数据类
# ---------------------------------------------------------------------------
class TestShippingZone:
    def test_defaults(self):
        z = ShippingZone()
        assert z.id is None
        assert z.name == ""
        assert z.order == 0
        assert z.enabled is True
        assert z.locations == []
        assert z.methods == []

    def test_custom_values(self):
        z = ShippingZone(
            id=1,
            name="Domestic",
            order=0,
            locations=[{"code": "US", "type": "country"}],
        )
        assert z.id == 1
        assert z.name == "Domestic"
        assert len(z.locations) == 1


# ---------------------------------------------------------------------------
# PaymentGateway 数据类
# ---------------------------------------------------------------------------
class TestPaymentGateway:
    def test_defaults(self):
        g = PaymentGateway()
        assert g.id == ""
        assert g.title == ""
        assert g.description == ""
        assert g.enabled is True
        assert g.order == 0
        assert g.settings == {}

    def test_custom_values(self):
        g = PaymentGateway(
            id="paypal",
            title="PayPal",
            enabled=False,
            order=2,
            settings={"key": "value"},
        )
        assert g.id == "paypal"
        assert g.title == "PayPal"
        assert g.enabled is False
        assert g.order == 2
        assert g.settings == {"key": "value"}


# ---------------------------------------------------------------------------
# ReviewGenerator
# ---------------------------------------------------------------------------
class TestReviewGenerator:
    def test_generate_review_default(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product")
        assert isinstance(review, ProductReview)
        assert review.author != ""
        assert review.email != ""
        assert review.avatar != ""
        assert 1 <= review.rating <= 5
        assert review.content != ""
        assert review.date != ""
        assert "Test Product" in review.content or len(review.content) > 0

    def test_generate_review_with_rating(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product", rating=4)
        assert review.rating == 4

    def test_generate_review_positive(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product", rating=4, review_type="positive")
        assert review.rating == 4
        assert "Test Product" in review.content

    def test_generate_review_neutral(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product", rating=3, review_type="neutral")
        assert review.rating == 3
        assert "Test Product" in review.content

    def test_generate_review_detailed(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product", rating=5, detailed=True)
        assert review.rating == 5
        assert "Test Product" in review.content
        # 详细评论应当较长
        assert len(review.content) > 50

    def test_generate_review_rating_5_uses_detailed(self):
        """5星评论自动使用详细模板"""
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product", rating=5)
        assert review.rating == 5
        assert len(review.content) > 50

    def test_generate_review_email_format(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product")
        assert "@" in review.email
        assert review.email.split("@")[0] == review.author.lower().replace(" ", ".")

    def test_generate_review_avatar_url(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product")
        assert review.avatar.startswith("http")

    def test_generate_review_verified_flag(self):
        gen = ReviewGenerator()
        # 多次生成验证 verified 是 bool 类型
        for _ in range(20):
            review = gen.generate_review("Test Product")
            assert isinstance(review.verified, bool)

    def test_generate_review_helpful_non_negative(self):
        gen = ReviewGenerator()
        review = gen.generate_review("Test Product")
        assert review.helpful >= 0

    def test_generate_reviews_count(self):
        gen = ReviewGenerator()
        reviews = gen.generate_reviews("Test Product", count=5)
        assert len(reviews) == 5
        assert all(isinstance(r, ProductReview) for r in reviews)

    def test_generate_reviews_rating_range(self):
        gen = ReviewGenerator()
        reviews = gen.generate_reviews("Test Product", count=10, min_rating=3, max_rating=5)
        assert all(3 <= r.rating <= 5 for r in reviews)

    def test_generate_reviews_sorted_by_date(self):
        gen = ReviewGenerator()
        reviews = gen.generate_reviews("Test Product", count=10)
        dates = [r.date for r in reviews]
        assert dates == sorted(dates, reverse=True)

    def test_generate_reviews_empty(self):
        gen = ReviewGenerator()
        reviews = gen.generate_reviews("Test Product", count=0)
        assert reviews == []

    def test_generate_review_response_5_star(self):
        gen = ReviewGenerator()
        review = ProductReview(rating=5)
        response = gen.generate_review_response(review, brand_name="TestBrand")
        assert "author" in response
        assert "content" in response
        assert "date" in response
        assert "TestBrand" in response["content"] or "客服" in response["author"]

    def test_generate_review_response_1_star(self):
        gen = ReviewGenerator()
        review = ProductReview(rating=1)
        response = gen.generate_review_response(review, brand_name="TestBrand")
        assert "抱歉" in response["content"] or "歉意" in response["content"]

    def test_generate_review_response_3_star(self):
        gen = ReviewGenerator()
        review = ProductReview(rating=3)
        response = gen.generate_review_response(review, brand_name="TestBrand")
        assert "反馈" in response["content"] or "意见" in response["content"]

    def test_generate_review_response_unknown_rating(self):
        gen = ReviewGenerator()
        review = ProductReview(rating=10)  # 超出范围，应当使用默认5星回复
        response = gen.generate_review_response(review, brand_name="TestBrand")
        assert "content" in response

    def test_generate_review_response_no_brand(self):
        gen = ReviewGenerator()
        review = ProductReview(rating=5)
        response = gen.generate_review_response(review)
        assert "content" in response
        assert "author" in response


# ---------------------------------------------------------------------------
# CouponGenerator
# ---------------------------------------------------------------------------
class TestCouponGenerator:
    def test_generate_coupon_code_default_prefix(self):
        gen = CouponGenerator()
        code = gen.generate_coupon_code()
        assert code.startswith("SAVE_")
        assert len(code) == len("SAVE_") + 8

    def test_generate_coupon_code_custom_prefix(self):
        gen = CouponGenerator()
        code = gen.generate_coupon_code("PROMO")
        assert code.startswith("PROMO_")

    def test_generate_coupon_code_unique(self):
        gen = CouponGenerator()
        codes = {gen.generate_coupon_code() for _ in range(20)}
        # 随机性应当产生多个不同的 code（极大概率）
        assert len(codes) > 1

    def test_generate_coupon_percentage(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="percentage")
        assert coupon.discount_type == "percent"
        assert coupon.amount > 0
        assert "%" in coupon.description

    def test_generate_coupon_fixed_cart(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="fixed_cart")
        assert coupon.discount_type == "fixed_cart"
        assert coupon.amount > 0
        assert "$" in coupon.description

    def test_generate_coupon_fixed_product(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="fixed_product")
        assert coupon.discount_type == "fixed_product"
        assert coupon.amount > 0

    def test_generate_coupon_unknown_type_defaults_percentage(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="unknown")
        assert coupon.discount_type == "percent"

    def test_generate_coupon_with_expires(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="percentage", expires_days=30)
        assert coupon.date_expires is not None
        # 应当是未来的日期
        assert coupon.date_expires > datetime.now().strftime("%Y-%m-%d")

    def test_generate_coupon_no_expires(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="percentage", expires_days=None)
        assert coupon.date_expires is None

    def test_generate_coupon_with_min_amount(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="percentage", min_amount=50.0)
        assert coupon.minimum_amount == 50.0

    def test_generate_coupon_with_usage_limit(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="percentage", usage_limit=200)
        assert coupon.usage_limit == 200

    def test_generate_coupon_individual_use(self):
        gen = CouponGenerator()
        coupon = gen.generate_coupon(coupon_type="percentage")
        assert coupon.individual_use is True

    def test_generate_coupons_count(self):
        gen = CouponGenerator()
        coupons = gen.generate_coupons(count=5)
        assert len(coupons) == 5
        assert all(isinstance(c, Coupon) for c in coupons)

    def test_generate_coupons_empty(self):
        gen = CouponGenerator()
        coupons = gen.generate_coupons(count=0)
        assert coupons == []

    def test_generate_coupons_code_unique(self):
        gen = CouponGenerator()
        coupons = gen.generate_coupons(count=10)
        codes = {c.code for c in coupons}
        assert len(codes) == 10


# ---------------------------------------------------------------------------
# WooCommerceAutomationService
# ---------------------------------------------------------------------------
class TestWooCommerceAutomationService:
    def test_init(self):
        svc = WooCommerceAutomationService()
        assert isinstance(svc.review_generator, ReviewGenerator)
        assert isinstance(svc.coupon_generator, CouponGenerator)

    def test_auto_generate_product_reviews(self):
        svc = WooCommerceAutomationService()
        reviews = svc.auto_generate_product_reviews(
            product_id=1,
            product_name="Test Product",
            review_count=5,
            avg_rating=4.5,
        )
        assert len(reviews) == 5
        assert all(r.product_id == 1 for r in reviews)
        assert all(isinstance(r, ProductReview) for r in reviews)

    def test_auto_generate_product_reviews_rating_range(self):
        svc = WooCommerceAutomationService()
        reviews = svc.auto_generate_product_reviews(
            product_id=1,
            product_name="Test Product",
            review_count=10,
            avg_rating=4.0,
        )
        # avg_rating=4.0 -> min_rating=max(1,int(2.5))=2, max_rating=min(5,int(4.5))=4
        assert all(2 <= r.rating <= 4 for r in reviews)

    def test_auto_generate_product_reviews_zero_count(self):
        svc = WooCommerceAutomationService()
        reviews = svc.auto_generate_product_reviews(
            product_id=1,
            product_name="Test Product",
            review_count=0,
        )
        assert reviews == []

    def test_auto_setup_payment_gateways(self):
        svc = WooCommerceAutomationService()
        gateways = svc.auto_setup_payment_gateways()
        assert len(gateways) == 4
        assert all(isinstance(g, PaymentGateway) for g in gateways)
        ids = {g.id for g in gateways}
        assert "paypal" in ids
        assert "stripe" in ids
        assert "cod" in ids
        assert "bacs" in ids

    def test_auto_setup_payment_gateways_order(self):
        svc = WooCommerceAutomationService()
        gateways = svc.auto_setup_payment_gateways()
        orders = [g.order for g in gateways]
        assert orders == sorted(orders)

    def test_auto_setup_payment_gateways_paypal_enabled(self):
        svc = WooCommerceAutomationService()
        gateways = svc.auto_setup_payment_gateways()
        paypal = next(g for g in gateways if g.id == "paypal")
        assert paypal.enabled is True
        assert "email" in paypal.settings

    def test_auto_setup_payment_gateways_cod_disabled(self):
        svc = WooCommerceAutomationService()
        gateways = svc.auto_setup_payment_gateways()
        cod = next(g for g in gateways if g.id == "cod")
        assert cod.enabled is False

    def test_auto_setup_shipping_zones(self):
        svc = WooCommerceAutomationService()
        zones = svc.auto_setup_shipping_zones()
        assert len(zones) == 3
        assert all(isinstance(z, ShippingZone) for z in zones)

    def test_auto_setup_shipping_zones_names(self):
        svc = WooCommerceAutomationService()
        zones = svc.auto_setup_shipping_zones(base_country="US", base_state="CA")
        names = [z.name for z in zones]
        assert any("Domestic" in n for n in names)
        assert any("International" in n for n in names)
        assert any("Local Pickup" in n for n in names)

    def test_auto_setup_shipping_zones_domestic_methods(self):
        svc = WooCommerceAutomationService()
        zones = svc.auto_setup_shipping_zones()
        domestic = zones[0]
        assert len(domestic.methods) == 3
        method_ids = [m["id"] for m in domestic.methods]
        assert "flat_rate" in method_ids
        assert "free_shipping" in method_ids

    def test_auto_setup_shipping_zones_international_locations(self):
        svc = WooCommerceAutomationService()
        zones = svc.auto_setup_shipping_zones()
        international = zones[1]
        assert len(international.locations) == 6
        assert all(l["type"] == "continent" for l in international.locations)

    def test_auto_generate_coupons(self):
        svc = WooCommerceAutomationService()
        coupons = svc.auto_generate_coupons(count=5)
        assert len(coupons) == 5
        assert all(isinstance(c, Coupon) for c in coupons)

    def test_auto_generate_coupons_with_types(self):
        svc = WooCommerceAutomationService()
        coupons = svc.auto_generate_coupons(count=5, types=["percentage"])
        assert all(c.discount_type == "percent" for c in coupons)

    def test_auto_generate_coupons_zero(self):
        svc = WooCommerceAutomationService()
        coupons = svc.auto_generate_coupons(count=0)
        assert coupons == []

    def test_auto_link_related_products(self):
        svc = WooCommerceAutomationService()
        products = [{"id": i, "name": f"P{i}"} for i in range(1, 11)]
        result = svc.auto_link_related_products(
            product_id=1,
            all_products=products,
            related_count=4,
            cross_sell_count=2,
            upsell_count=2,
        )
        assert "related" in result
        assert "cross_sells" in result
        assert "upsells" in result
        assert len(result["related"]) == 4
        assert len(result["cross_sells"]) == 2
        assert len(result["upsells"]) == 2
        # 当前产品不应当在结果中
        assert 1 not in result["related"]
        assert 1 not in result["cross_sells"]
        assert 1 not in result["upsells"]

    def test_auto_link_related_products_no_others(self):
        svc = WooCommerceAutomationService()
        products = [{"id": 1, "name": "P1"}]
        result = svc.auto_link_related_products(
            product_id=1,
            all_products=products,
        )
        assert result == {"related": [], "cross_sells": [], "upsells": []}

    def test_auto_link_related_products_few_products(self):
        svc = WooCommerceAutomationService()
        products = [{"id": 1}, {"id": 2}]
        result = svc.auto_link_related_products(
            product_id=1,
            all_products=products,
            related_count=5,
            cross_sell_count=5,
            upsell_count=5,
        )
        # 只有1个其他产品
        assert len(result["related"]) == 1
        assert len(result["cross_sells"]) == 0
        assert len(result["upsells"]) == 0

    def test_auto_link_related_products_no_overlap(self):
        svc = WooCommerceAutomationService()
        products = [{"id": i} for i in range(1, 21)]
        result = svc.auto_link_related_products(
            product_id=1,
            all_products=products,
            related_count=4,
            cross_sell_count=3,
            upsell_count=2,
        )
        all_ids = set(result["related"]) | set(result["cross_sells"]) | set(result["upsells"])
        # 没有重复
        assert len(all_ids) == len(result["related"]) + len(result["cross_sells"]) + len(result["upsells"])

    def test_auto_setup_store_pages(self):
        svc = WooCommerceAutomationService()
        pages = svc.auto_setup_store_pages(store_name="MyStore")
        assert len(pages) == 8
        slugs = {p["slug"] for p in pages}
        assert "shop" in slugs
        assert "cart" in slugs
        assert "checkout" in slugs
        assert "my-account" in slugs
        assert "terms-and-conditions" in slugs
        assert "privacy-policy" in slugs
        assert "refund-policy" in slugs
        assert "shipping-policy" in slugs

    def test_auto_setup_store_pages_woocommerce_pages(self):
        svc = WooCommerceAutomationService()
        pages = svc.auto_setup_store_pages(store_name="MyStore")
        wc_pages = [p for p in pages if p.get("is_woocommerce")]
        assert len(wc_pages) == 4

    def test_auto_setup_store_pages_store_name_in_content(self):
        svc = WooCommerceAutomationService()
        pages = svc.auto_setup_store_pages(store_name="MyStore")
        terms = next(p for p in pages if p["slug"] == "terms-and-conditions")
        assert "MyStore" in terms["content"]

    def test_get_woocommerce_settings(self):
        svc = WooCommerceAutomationService()
        settings = svc.get_woocommerce_settings(store_name="MyStore", currency="USD", country="US")
        assert "general" in settings
        assert "products" in settings
        assert "shipping" in settings
        assert "payments" in settings
        assert "accounts" in settings
        assert "email" in settings

    def test_get_woocommerce_settings_currency(self):
        svc = WooCommerceAutomationService()
        settings = svc.get_woocommerce_settings(currency="EUR", country="FR")
        assert settings["general"]["woocommerce_currency"] == "EUR"
        assert "FR" in settings["general"]["woocommerce_default_country"]

    def test_get_woocommerce_settings_store_name(self):
        svc = WooCommerceAutomationService()
        settings = svc.get_woocommerce_settings(store_name="MyStore")
        assert settings["email"]["woocommerce_email_from_name"] == "MyStore"
        assert "MyStore" in settings["email"]["woocommerce_email_footer_text"]

    def test_get_cro_optimization_tips(self):
        svc = WooCommerceAutomationService()
        tips = svc.get_cro_optimization_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0
        assert all(isinstance(t, str) for t in tips)

    def test_global_instance(self):
        assert isinstance(wc_automation_service, WooCommerceAutomationService)


# ---------------------------------------------------------------------------
# ProductQA 数据类
# ---------------------------------------------------------------------------
class TestProductQA:
    def test_defaults(self):
        qa = ProductQA()
        assert qa.id is None
        assert qa.product_id == 0
        assert qa.question == ""
        assert qa.answer == ""
        assert qa.author_name == ""
        assert qa.author_email == ""
        assert qa.date_created == ""
        assert qa.helpful == 0
        assert qa.not_helpful == 0
        assert qa.votes == {}

    def test_custom_values(self):
        qa = ProductQA(
            id=1,
            product_id=100,
            question="Is this good?",
            answer="Yes, it is.",
            author_name="John",
            author_email="john@test.com",
            date_created="2024-01-01 10:00:00",
            helpful=5,
            not_helpful=1,
        )
        assert qa.id == 1
        assert qa.product_id == 100
        assert qa.question == "Is this good?"
        assert qa.answer == "Yes, it is."
        assert qa.author_name == "John"
        assert qa.helpful == 5

    def test_to_dict(self):
        qa = ProductQA(
            product_id=1,
            question="Q?",
            answer="A.",
            author_name="John",
            author_email="john@test.com",
            date_created="2024-01-01",
            helpful=3,
        )
        d = qa.to_dict()
        assert d["product_id"] == 1
        assert d["question"] == "Q?"
        assert d["answer"] == "A."
        assert d["author_name"] == "John"
        assert d["helpful"] == 3

    def test_independent_votes(self):
        a = ProductQA()
        b = ProductQA()
        a.votes["up"] = 1
        assert b.votes == {}


# ---------------------------------------------------------------------------
# QAGenerator
# ---------------------------------------------------------------------------
class TestQAGenerator:
    def test_generate_qa_basic(self):
        gen = QAGenerator()
        qa = gen.generate_qa(product_id=1, product_name="Test Product")
        assert isinstance(qa, ProductQA)
        assert qa.product_id == 1
        assert qa.question != ""
        assert qa.answer != ""
        assert qa.author_name != ""
        assert qa.author_email != ""
        assert qa.date_created != ""
        assert "@" in qa.author_email

    def test_generate_qa_default_product_name(self):
        gen = QAGenerator()
        qa = gen.generate_qa(product_id=42)
        assert qa.product_id == 42
        # 默认产品名应包含产品ID
        assert "42" in qa.question or "42" in qa.answer

    def test_generate_qa_question_contains_product(self):
        gen = QAGenerator()
        qa = gen.generate_qa(product_id=1, product_name="Magic Widget")
        assert "Magic Widget" in qa.question

    def test_generate_qa_answer_non_empty(self):
        gen = QAGenerator()
        qa = gen.generate_qa(product_id=1, product_name="Widget")
        assert len(qa.answer) > 10

    def test_generate_qa_email_format(self):
        gen = QAGenerator()
        qa = gen.generate_qa(product_id=1, product_name="Widget")
        assert "@" in qa.author_email
        # 邮箱用户名应为 author_name 的小写形式
        assert qa.author_email.split("@")[0] == qa.author_name.lower().replace(" ", ".")

    def test_generate_qas_count(self):
        gen = QAGenerator()
        qas = gen.generate_qas(product_id=1, count=5, product_name="Widget")
        assert len(qas) == 5
        assert all(isinstance(q, ProductQA) for q in qas)

    def test_generate_qas_sorted_by_date(self):
        gen = QAGenerator()
        qas = gen.generate_qas(product_id=1, count=8, product_name="Widget")
        dates = [q.date_created for q in qas]
        assert dates == sorted(dates, reverse=True)

    def test_generate_qas_zero(self):
        gen = QAGenerator()
        qas = gen.generate_qas(product_id=1, count=0)
        assert qas == []

    def test_generate_qas_all_have_product_id(self):
        gen = QAGenerator()
        qas = gen.generate_qas(product_id=99, count=3, product_name="Widget")
        assert all(q.product_id == 99 for q in qas)


# ---------------------------------------------------------------------------
# WooCommerceAutomationService - 新增 AI 生成方法
# ---------------------------------------------------------------------------
class TestWooCommerceAIContent:
    def test_init_has_qa_generator(self):
        svc = WooCommerceAutomationService()
        assert isinstance(svc.qa_generator, QAGenerator)

    def test_generate_product_reviews_count(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=5)
        assert len(reviews) == 5
        assert all(isinstance(r, dict) for r in reviews)

    def test_generate_product_reviews_fields(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=3)
        for r in reviews:
            assert "author_name" in r
            assert "author_email" in r
            assert "review_content" in r
            assert "rating" in r
            assert "date_created" in r
            assert "verified" in r
            assert "avatar_url" in r

    def test_generate_product_reviews_rating_range(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=10)
        assert all(1 <= r["rating"] <= 5 for r in reviews)

    def test_generate_product_reviews_verified_is_bool(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=5)
        assert all(isinstance(r["verified"], bool) for r in reviews)

    def test_generate_product_reviews_avatar_url(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=3)
        assert all(r["avatar_url"].startswith("http") for r in reviews)

    def test_generate_product_reviews_email_format(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=3)
        assert all("@" in r["author_email"] for r in reviews)

    def test_generate_product_reviews_content_non_empty(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=3)
        assert all(r["review_content"] for r in reviews)

    def test_generate_product_reviews_zero(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=0)
        assert reviews == []

    def test_generate_product_reviews_with_name(self):
        svc = WooCommerceAutomationService()
        reviews = svc.generate_product_reviews(product_id=1, count=2, product_name="MyWidget")
        # 评论内容应包含产品名（本地生成器会包含）
        assert any("MyWidget" in r["review_content"] for r in reviews)

    def test_generate_product_qa_count(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=5)
        assert len(qas) == 5
        assert all(isinstance(q, dict) for q in qas)

    def test_generate_product_qa_fields(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=3)
        for q in qas:
            assert "question" in q
            assert "answer" in q
            assert "author_name" in q
            assert "author_email" in q
            assert "date_created" in q

    def test_generate_product_qa_question_non_empty(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=3)
        assert all(q["question"] for q in qas)

    def test_generate_product_qa_answer_non_empty(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=3)
        assert all(len(q["answer"]) > 5 for q in qas)

    def test_generate_product_qa_zero(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=0)
        assert qas == []

    def test_generate_product_qa_with_name(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=2, product_name="MagicWidget")
        assert any("MagicWidget" in q["question"] for q in qas)

    def test_generate_product_qa_email_format(self):
        svc = WooCommerceAutomationService()
        qas = svc.generate_product_qa(product_id=1, count=3)
        assert all("@" in q["author_email"] for q in qas)


# ---------------------------------------------------------------------------
# WooCommerceAutomationService - 支付网关配置
# ---------------------------------------------------------------------------
class TestConfigurePaymentGateways:
    def test_configure_basic(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[
                {"id": "paypal", "enabled": True},
                {"id": "stripe", "enabled": True},
            ],
        )
        assert result["site_id"] == 1
        assert result["success_count"] == 2
        assert result["success"] is True
        assert len(result["configured"]) == 2

    def test_configure_returns_api_request(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "paypal", "enabled": True}],
        )
        gw = result["configured"][0]
        assert "api_request" in gw
        assert gw["api_request"]["method"] == "PUT"
        assert "/wc/v3/payment_gateways/paypal" in gw["api_request"]["endpoint"]

    def test_configure_paypal_defaults(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "paypal", "enabled": True}],
        )
        gw = result["configured"][0]
        assert gw["gateway_id"] == "paypal"
        assert gw["enabled"] is True
        assert gw["title"] == "PayPal"
        assert "email" in gw["settings"]

    def test_configure_stripe_defaults(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "stripe", "enabled": True}],
        )
        gw = result["configured"][0]
        assert gw["gateway_id"] == "stripe"
        assert "publishable_key" in gw["settings"]
        assert "secret_key" in gw["settings"]

    def test_configure_cod_defaults(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "cod", "enabled": False}],
        )
        gw = result["configured"][0]
        assert gw["enabled"] is False
        assert gw["settings"]["enabled"] == "no"

    def test_configure_custom_title(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "paypal", "title": "My PayPal", "enabled": True}],
        )
        gw = result["configured"][0]
        assert gw["title"] == "My PayPal"
        assert gw["settings"]["title"] == "My PayPal"

    def test_configure_custom_settings_merged(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{
                "id": "paypal",
                "enabled": True,
                "settings": {"email": "custom@pay.com", "testmode": "yes"},
            }],
        )
        gw = result["configured"][0]
        assert gw["settings"]["email"] == "custom@pay.com"
        assert gw["settings"]["testmode"] == "yes"

    def test_configure_unknown_gateway(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "unknown_gateway", "enabled": True}],
        )
        # 未知网关也应被配置（使用默认值）
        assert result["success_count"] == 1
        gw = result["configured"][0]
        assert gw["gateway_id"] == "unknown_gateway"

    def test_configure_missing_id_fails(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"enabled": True}],  # 缺少 id
        )
        assert result["success"] is False
        assert len(result["failed"]) == 1
        assert result["success_count"] == 0

    def test_configure_gateway_id_alias(self):
        """支持 gateway_id 作为 id 的别名"""
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"gateway_id": "paypal", "enabled": True}],
        )
        assert result["success_count"] == 1

    def test_configure_empty_list(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(site_id=1, gateways=[])
        assert result["success_count"] == 0
        assert result["total"] == 0
        assert result["success"] is True

    def test_configure_multiple_gateways(self):
        svc = WooCommerceAutomationService()
        gateways = [
            {"id": "paypal", "enabled": True},
            {"id": "stripe", "enabled": True},
            {"id": "cod", "enabled": False},
            {"id": "bacs", "enabled": False},
        ]
        result = svc.configure_payment_gateways(site_id=5, gateways=gateways)
        assert result["success_count"] == 4
        assert result["site_id"] == 5

    def test_configure_alipay(self):
        svc = WooCommerceAutomationService()
        result = svc.configure_payment_gateways(
            site_id=1,
            gateways=[{"id": "alipay", "enabled": True}],
        )
        assert result["success_count"] == 1
        assert result["configured"][0]["gateway_id"] == "alipay"


# ---------------------------------------------------------------------------
# WooCommerceAutomationService - 营销自动化
# ---------------------------------------------------------------------------
class TestSetupMarketingAutomation:
    def test_basic(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_marketing_automation(site_id=1)
        assert result["site_id"] == 1
        assert result["status"] == "configured"

    def test_has_coupons(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_marketing_automation(site_id=1)
        assert "coupons" in result
        assert result["coupon_count"] == 5
        assert len(result["coupons"]) == 5

    def test_has_abandoned_cart(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_marketing_automation(site_id=1)
        ac = result["abandoned_cart"]
        assert ac["enabled"] is True
        assert "email_sequence" in ac
        assert len(ac["email_sequence"]) == 3
        assert "discount_incentive" in ac
        assert ac["discount_incentive"]["enabled"] is True

    def test_has_trust_badges(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_marketing_automation(site_id=1)
        badges = result["trust_badges"]
        assert isinstance(badges, list)
        assert len(badges) >= 3
        for b in badges:
            assert "name" in b
            assert "position" in b

    def test_has_urgency_elements(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_marketing_automation(site_id=1)
        urgency = result["urgency_elements"]
        assert "low_stock_alert" in urgency
        assert "high_demand_alert" in urgency
        assert "recent_sales" in urgency
        assert urgency["low_stock_alert"]["enabled"] is True

    def test_has_social_proof(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_marketing_automation(site_id=1)
        sp = result["social_proof"]
        assert "sales_notifications" in sp
        assert "review_highlights" in sp
        assert "customer_count" in sp
        assert sp["sales_notifications"]["enabled"] is True

    def test_different_site_ids(self):
        svc = WooCommerceAutomationService()
        r1 = svc.setup_marketing_automation(site_id=1)
        r2 = svc.setup_marketing_automation(site_id=2)
        assert r1["site_id"] == 1
        assert r2["site_id"] == 2


# ---------------------------------------------------------------------------
# WooCommerceAutomationService - CRO 转化率优化
# ---------------------------------------------------------------------------
class TestSetupCROOptimization:
    def test_basic(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_cro_optimization(site_id=1)
        assert result["site_id"] == 1
        assert result["status"] == "configured"

    def test_has_trust_elements(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_cro_optimization(site_id=1)
        te = result["trust_elements"]
        assert "security_badges" in te
        assert "guarantees" in te
        assert "certifications" in te
        assert "customer_testimonials" in te
        assert len(te["security_badges"]) >= 3

    def test_has_urgency_elements(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_cro_optimization(site_id=1)
        ue = result["urgency_elements"]
        assert "stock_urgency" in ue
        assert "time_urgency" in ue
        assert "social_urgency" in ue
        assert "limited_offer" in ue
        assert ue["stock_urgency"]["enabled"] is True

    def test_has_conversion_optimization(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_cro_optimization(site_id=1)
        co = result["conversion_optimization"]
        assert "checkout_optimization" in co
        assert "product_page_optimization" in co
        assert "cta_optimization" in co
        assert "mobile_optimization" in co
        assert "exit_intent" in co
        assert co["checkout_optimization"]["guest_checkout"] is True

    def test_has_ab_test_suggestions(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_cro_optimization(site_id=1)
        suggestions = result["ab_test_suggestions"]
        assert isinstance(suggestions, list)
        assert len(suggestions) >= 3
        for s in suggestions:
            assert "element" in s
            assert "variants" in s

    def test_has_tips(self):
        svc = WooCommerceAutomationService()
        result = svc.setup_cro_optimization(site_id=1)
        assert isinstance(result["tips"], list)
        assert len(result["tips"]) > 0

    def test_different_site_ids(self):
        svc = WooCommerceAutomationService()
        r1 = svc.setup_cro_optimization(site_id=10)
        r2 = svc.setup_cro_optimization(site_id=20)
        assert r1["site_id"] == 10
        assert r2["site_id"] == 20
