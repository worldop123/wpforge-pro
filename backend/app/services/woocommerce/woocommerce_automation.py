"""
WooCommerce深度自动化服务
包含产品增强、支付物流配置、营销自动化等功能
"""
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import time
from datetime import datetime, timedelta


class ReviewType(str, Enum):
    """评论类型"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class CouponType(str, Enum):
    """优惠券类型"""
    PERCENT = "percent"
    FIXED_CART = "fixed_cart"
    FIXED_PRODUCT = "fixed_product"


@dataclass
class ProductReview:
    """产品评论"""
    product_id: int
    author: str
    email: str
    rating: int  # 1-5
    content: str
    date: str
    verified: bool = True
    avatar_url: str = ""
    helpful: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "author": self.author,
            "email": self.email,
            "rating": self.rating,
            "content": self.content,
            "date": self.date,
            "verified": self.verified,
            "avatar_url": self.avatar_url,
            "helpful": self.helpful,
        }


@dataclass
class ProductFAQ:
    """产品问答"""
    product_id: int
    question: str
    answer: str
    author: str = "Admin"
    date: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "question": self.question,
            "answer": self.answer,
            "author": self.author,
            "date": self.date,
        }


@dataclass
class CouponConfig:
    """优惠券配置"""
    code: str
    discount_type: CouponType
    amount: float
    description: str = ""
    usage_limit: Optional[int] = None
    usage_limit_per_user: Optional[int] = 1
    expiry_date: Optional[str] = None
    minimum_amount: Optional[float] = None
    maximum_amount: Optional[float] = None
    product_ids: List[int] = field(default_factory=list)
    category_ids: List[int] = field(default_factory=list)
    free_shipping: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "discount_type": self.discount_type.value,
            "amount": self.amount,
            "description": self.description,
            "usage_limit": self.usage_limit,
            "usage_limit_per_user": self.usage_limit_per_user,
            "expiry_date": self.expiry_date,
            "minimum_amount": self.minimum_amount,
            "maximum_amount": self.maximum_amount,
            "product_ids": self.product_ids,
            "category_ids": self.category_ids,
            "free_shipping": self.free_shipping,
        }


@dataclass
class PaymentGatewayConfig:
    """支付网关配置"""
    gateway_id: str
    enabled: bool = False
    title: str = ""
    description: str = ""
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gateway_id": self.gateway_id,
            "enabled": self.enabled,
            "title": self.title,
            "description": self.description,
            "settings": self.settings,
        }


@dataclass
class ShippingZoneConfig:
    """配送区域配置"""
    zone_name: str
    zone_order: int = 0
    locations: List[Dict[str, str]] = field(default_factory=list)
    shipping_methods: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_name": self.zone_name,
            "zone_order": self.zone_order,
            "locations": self.locations,
            "shipping_methods": self.shipping_methods,
        }


@dataclass
class TrustBadge:
    """信任徽章"""
    id: str
    name: str
    icon: str
    description: str
    position: str = "checkout"  # checkout, product, cart
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "description": self.description,
            "position": self.position,
            "enabled": self.enabled,
        }


@dataclass
class UrgencyElement:
    """紧迫感元素"""
    type: str  # stock_countdown, limited_stock, recent_purchase, visitors_online
    enabled: bool = False
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "enabled": self.enabled,
            "settings": self.settings,
        }


class WooCommerceAutomationService:
    """
    WooCommerce深度自动化服务
    """

    def __init__(self):
        self._review_templates = self._init_review_templates()
        self._faq_templates = self._init_faq_templates()
        self._trust_badges = self._init_trust_badges()
        self._first_names = [
            "John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa",
            "James", "Jennifer", "William", "Mary", "Richard", "Patricia", "Thomas",
            "Linda", "Christopher", "Barbara", "Daniel", "Elizabeth", "Matthew",
            "Susan", "Anthony", "Jessica", "Mark", "Sarah", "Steven", "Karen",
        ]
        self._last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        ]

    def _init_review_templates(self) -> Dict[str, List[str]]:
        """初始化评论模板"""
        return {
            "positive": [
                "Absolutely love this product! Exceeded my expectations in every way.",
                "Great quality and fast shipping. Would definitely buy again.",
                "This is my second purchase and I'm still impressed. Highly recommend!",
                "Best {product} I've ever tried. Worth every penny.",
                "Amazing quality for the price. Five stars all the way!",
                "Been using this for a month now and it's still going strong. Love it!",
                "The quality is outstanding. You can tell they care about their products.",
                "Fast delivery and the product is even better than described. Very happy!",
            ],
            "neutral": [
                "Pretty good product overall. Does what it says it does.",
                "Decent quality for the price. Not amazing but not bad either.",
                "Works as expected. Nothing special but gets the job done.",
                "Solid product. Would recommend if you're on a budget.",
                "It's okay. I've had better but also had worse.",
            ],
            "negative": [
                "Not quite what I expected. The quality is just okay.",
                "It works but I thought it would be better based on the pictures.",
                "Average product. Probably wouldn't buy again.",
            ],
        }

    def _init_faq_templates(self) -> List[Dict[str, str]]:
        """初始化FAQ模板"""
        return [
            {
                "question": "How long does shipping take?",
                "answer": "We typically ship within 1-2 business days. Standard delivery takes 5-7 business days, while express shipping takes 2-3 business days.",
            },
            {
                "question": "What is your return policy?",
                "answer": "We offer a 30-day money-back guarantee. If you're not satisfied with your purchase, you can return it for a full refund within 30 days of delivery.",
            },
            {
                "question": "Is this product authentic?",
                "answer": "Yes, all our products are 100% authentic and come directly from the manufacturer. We guarantee the quality and authenticity of every item we sell.",
            },
            {
                "question": "Do you offer international shipping?",
                "answer": "Yes, we ship worldwide! International shipping times vary by location, typically 7-14 business days.",
            },
            {
                "question": "How do I track my order?",
                "answer": "Once your order ships, you'll receive an email with a tracking number. You can use this number on our website or the carrier's website to track your package.",
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major credit cards (Visa, Mastercard, American Express), PayPal, and various other payment methods depending on your location.",
            },
        ]

    def _init_trust_badges(self) -> List[TrustBadge]:
        """初始化信任徽章"""
        return [
            TrustBadge(
                id="secure_checkout",
                name="Secure Checkout",
                icon="🔒",
                description="SSL encrypted secure payment",
                position="checkout",
            ),
            TrustBadge(
                id="money_back",
                name="30-Day Money Back",
                icon="💰",
                description="Satisfaction guaranteed or your money back",
                position="checkout",
            ),
            TrustBadge(
                id="free_shipping",
                name="Free Shipping",
                icon="🚚",
                description="Free shipping on orders over $50",
                position="product",
            ),
            TrustBadge(
                id="authentic",
                name="100% Authentic",
                icon="✅",
                description="Guaranteed authentic products",
                position="product",
            ),
            TrustBadge(
                id="fast_delivery",
                name="Fast Delivery",
                icon="⚡",
                description="Ships within 24 hours",
                position="product",
            ),
            TrustBadge(
                id="support",
                name="24/7 Support",
                icon="💬",
                description="Customer support anytime",
                position="checkout",
            ),
        ]

    # ==================== 产品评论AI生成 ====================

    def generate_product_reviews(self, product_id: int, product_name: str = "",
                                  num_reviews: int = 10,
                                  rating_distribution: Optional[Dict[int, float]] = None) -> List[ProductReview]:
        """
        AI生成产品评论

        Args:
            product_id: 产品ID
            product_name: 产品名称
            num_reviews: 评论数量
            rating_distribution: 评分分布 {rating: percentage}

        Returns:
            评论列表
        """
        if rating_distribution is None:
            # 默认分布：5星60%，4星25%，3星10%，2星3%，1星2%
            rating_distribution = {5: 0.6, 4: 0.25, 3: 0.1, 2: 0.03, 1: 0.02}

        reviews = []
        now = datetime.now()

        for i in range(num_reviews):
            # 根据分布随机选择评分
            rand = random.random()
            cumulative = 0
            rating = 5
            for r, prob in sorted(rating_distribution.items(), reverse=True):
                cumulative += prob
                if rand <= cumulative:
                    rating = r
                    break

            # 确定评论类型
            if rating >= 4:
                review_type = "positive"
            elif rating == 3:
                review_type = "neutral"
            else:
                review_type = "negative"

            # 随机选择评论模板
            templates = self._review_templates.get(review_type, [])
            template = random.choice(templates) if templates else "Good product."

            # 替换产品名称占位符
            content = template.replace("{product}", product_name.lower() if product_name else "product")

            # 生成随机作者
            first_name = random.choice(self._first_names)
            last_name = random.choice(self._last_names)
            author = f"{first_name} {last_name[0]}."
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"

            # 生成随机日期（过去90天内）
            days_ago = random.randint(1, 90)
            review_date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

            # 生成头像URL（使用随机头像服务）
            avatar_url = f"https://i.pravatar.cc/150?u={first_name.lower()}{last_name.lower()}{i}"

            review = ProductReview(
                product_id=product_id,
                author=author,
                email=email,
                rating=rating,
                content=content,
                date=review_date,
                verified=random.random() > 0.1,  # 90%验证过
                avatar_url=avatar_url,
                helpful=random.randint(0, 50),
            )
            reviews.append(review)

        # 按日期排序（最新的在前）
        reviews.sort(key=lambda r: r.date, reverse=True)

        return reviews

    # ==================== 产品问答AI生成 ====================

    def generate_product_faqs(self, product_id: int, product_name: str = "",
                               num_faqs: int = 5) -> List[ProductFAQ]:
        """
        AI生成产品问答

        Args:
            product_id: 产品ID
            product_name: 产品名称
            num_faqs: FAQ数量

        Returns:
            FAQ列表
        """
        faqs = []
        templates = self._faq_templates.copy()
        random.shuffle(templates)

        for i in range(min(num_faqs, len(templates))):
            template = templates[i]
            faq = ProductFAQ(
                product_id=product_id,
                question=template["question"],
                answer=template["answer"],
                author="Customer Support",
                date=datetime.now().strftime("%Y-%m-%d"),
            )
            faqs.append(faq)

        return faqs

    # ==================== 相关产品自动关联 ====================

    def auto_relate_products(self, product_id: int, all_products: List[Dict[str, Any]],
                              num_related: int = 4,
                              strategy: str = "category") -> List[int]:
        """
        自动关联相关产品

        Args:
            product_id: 当前产品ID
            all_products: 所有产品列表
            num_related: 关联数量
            strategy: 策略（category, tag, price, random）

        Returns:
            相关产品ID列表
        """
        if not all_products:
            return []

        # 查找当前产品
        current_product = None
        for p in all_products:
            if p.get("id") == product_id:
                current_product = p
                break

        if not current_product:
            # 如果找不到，随机选择
            other_products = [p["id"] for p in all_products if p.get("id") != product_id]
            random.shuffle(other_products)
            return other_products[:num_related]

        # 根据策略选择
        related_ids = []

        if strategy == "category":
            # 同分类优先
            current_cats = set(current_product.get("category_ids", []))
            scored = []
            for p in all_products:
                if p.get("id") == product_id:
                    continue
                p_cats = set(p.get("category_ids", []))
                common = len(current_cats & p_cats)
                scored.append((p["id"], common))

            scored.sort(key=lambda x: x[1], reverse=True)
            related_ids = [pid for pid, score in scored[:num_related]]

        elif strategy == "price":
            # 价格相近
            current_price = current_product.get("price", 0)
            scored = []
            for p in all_products:
                if p.get("id") == product_id:
                    continue
                price_diff = abs(p.get("price", 0) - current_price)
                scored.append((p["id"], price_diff))

            scored.sort(key=lambda x: x[1])
            related_ids = [pid for pid, score in scored[:num_related]]

        else:
            # 随机
            other_products = [p["id"] for p in all_products if p.get("id") != product_id]
            random.shuffle(other_products)
            related_ids = other_products[:num_related]

        return related_ids

    # ==================== 优惠券自动生成 ====================

    def generate_coupon(self, coupon_type: str = "welcome", 
                         discount_type: CouponType = CouponType.PERCENT,
                         amount: Optional[float] = None) -> CouponConfig:
        """
        自动生成优惠券

        Args:
            coupon_type: 优惠券类型（welcome, holiday, flash_sale, abandoned_cart）
            discount_type: 折扣类型
            amount: 折扣金额/百分比

        Returns:
            优惠券配置
        """
        # 根据类型生成默认值
        if coupon_type == "welcome":
            code = f"WELCOME{random.randint(100, 999)}"
            amount = amount or 10
            description = "Welcome discount for new customers"
            usage_limit = 1
        elif coupon_type == "holiday":
            code = f"HOLIDAY{random.randint(100, 999)}"
            amount = amount or 20
            description = "Holiday special discount"
            expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        elif coupon_type == "flash_sale":
            code = f"FLASH{random.randint(100, 999)}"
            amount = amount or 30
            description = "Flash sale - limited time only"
            usage_limit = 100
            expiry_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        elif coupon_type == "abandoned_cart":
            code = f"COMEBACK{random.randint(100, 999)}"
            amount = amount or 15
            description = "Come back and save on your cart"
            usage_limit = 1
            expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            code = f"SAVE{random.randint(100, 999)}"
            amount = amount or 10
            description = "Special discount"

        coupon = CouponConfig(
            code=code,
            discount_type=discount_type,
            amount=amount,
            description=description,
        )

        if coupon_type == "welcome":
            coupon.usage_limit = 1
            coupon.usage_limit_per_user = 1
        elif coupon_type == "flash_sale":
            coupon.usage_limit = 100
            coupon.expiry_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        elif coupon_type == "abandoned_cart":
            coupon.expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        return coupon

    def generate_multiple_coupons(self, num_coupons: int = 5) -> List[CouponConfig]:
        """
        批量生成优惠券

        Args:
            num_coupons: 数量

        Returns:
            优惠券列表
        """
        coupons = []
        types = ["welcome", "holiday", "flash_sale", "abandoned_cart"]

        for i in range(num_coupons):
            coupon_type = random.choice(types)
            coupon = self.generate_coupon(coupon_type=coupon_type)
            coupons.append(coupon)

        return coupons

    # ==================== 支付网关自动配置 ====================

    def auto_configure_payment_gateways(self, country: str = "US",
                                          currency: str = "USD") -> List[PaymentGatewayConfig]:
        """
        自动配置支付网关

        Args:
            country: 国家代码
            currency: 货币代码

        Returns:
            支付网关配置列表
        """
        gateways = []

        # PayPal（全球通用）
        gateways.append(PaymentGatewayConfig(
            gateway_id="paypal",
            enabled=True,
            title="PayPal",
            description="Pay via PayPal - you can pay with your credit card if you don't have a PayPal account.",
            settings={
                "email": "payments@example.com",
                "testmode": True,
                "debug": "no",
            },
        ))

        # Stripe（支持主要国家）
        if country in ["US", "CA", "GB", "DE", "FR", "ES", "IT", "AU", "JP", "SG"]:
            gateways.append(PaymentGatewayConfig(
                gateway_id="stripe",
                enabled=True,
                title="Credit Card (Stripe)",
                description="Pay with your credit card via Stripe.",
                settings={
                    "testmode": True,
                    "publishable_key": "",
                    "secret_key": "",
                    "statement_descriptor": "",
                },
            ))

        # COD（货到付款）
        gateways.append(PaymentGatewayConfig(
            gateway_id="cod",
            enabled=False,
            title="Cash on Delivery",
            description="Pay with cash upon delivery.",
            settings={
                "enable_for_methods": "",
                "enable_for_virtual": "no",
            },
        ))

        # BACS（银行转账）
        gateways.append(PaymentGatewayConfig(
            gateway_id="bacs",
            enabled=False,
            title="Direct Bank Transfer",
            description="Make your payment directly into our bank account.",
            settings={
                "account_name": "",
                "account_number": "",
                "bank_name": "",
                "sort_code": "",
                "iban": "",
                "bic": "",
            },
        ))

        return gateways

    # ==================== 配送区域自动设置 ====================

    def auto_configure_shipping_zones(self, base_country: str = "US",
                                       free_shipping_threshold: float = 50.0) -> List[ShippingZoneConfig]:
        """
        自动配置配送区域

        Args:
            base_country: 基础国家
            free_shipping_threshold: 免运费门槛

        Returns:
            配送区域配置列表
        """
        zones = []

        # 国内配送
        zones.append(ShippingZoneConfig(
            zone_name=f"{base_country} (Domestic)",
            zone_order=0,
            locations=[{"code": base_country, "type": "country"}],
            shipping_methods=[
                {
                    "method_id": "flat_rate",
                    "enabled": True,
                    "title": "Standard Shipping",
                    "cost": "5.99",
                },
                {
                    "method_id": "free_shipping",
                    "enabled": True,
                    "title": "Free Shipping",
                    "min_amount": str(free_shipping_threshold),
                    "requires": "min_amount",
                },
                {
                    "method_id": "flat_rate",
                    "enabled": True,
                    "title": "Express Shipping",
                    "cost": "14.99",
                },
            ],
        ))

        # 国际配送
        zones.append(ShippingZoneConfig(
            zone_name="International",
            zone_order=1,
            locations=[{"code": "EU", "type": "continent"}],
            shipping_methods=[
                {
                    "method_id": "flat_rate",
                    "enabled": True,
                    "title": "International Standard",
                    "cost": "19.99",
                },
                {
                    "method_id": "flat_rate",
                    "enabled": True,
                    "title": "International Express",
                    "cost": "39.99",
                },
            ],
        ))

        # 世界其他地区
        zones.append(ShippingZoneConfig(
            zone_name="Rest of the World",
            zone_order=2,
            locations=[],
            shipping_methods=[
                {
                    "method_id": "flat_rate",
                    "enabled": True,
                    "title": "Worldwide Shipping",
                    "cost": "29.99",
                },
            ],
        ))

        return zones

    # ==================== 信任徽章 ====================

    def get_trust_badges(self, position: Optional[str] = None) -> List[TrustBadge]:
        """
        获取信任徽章

        Args:
            position: 位置过滤（checkout, product, cart）

        Returns:
            信任徽章列表
        """
        badges = [b for b in self._trust_badges if b.enabled]

        if position:
            badges = [b for b in badges if b.position == position or b.position == "all"]

        return badges

    def add_trust_badge(self, badge: TrustBadge):
        """添加信任徽章"""
        self._trust_badges.append(badge)

    # ==================== 紧迫感元素 ====================

    def generate_urgency_elements(self, product_id: Optional[int] = None) -> List[UrgencyElement]:
        """
        生成紧迫感元素配置

        Args:
            product_id: 产品ID（可选）

        Returns:
            紧迫感元素列表
        """
        elements = []

        # 库存倒计时
        elements.append(UrgencyElement(
            type="stock_countdown",
            enabled=True,
            settings={
                "end_time": (datetime.now() + timedelta(hours=random.randint(2, 48))).isoformat(),
                "template": "⏰ Hurry! Sale ends in {time}",
                "position": "product_page",
            },
        ))

        # 有限库存显示
        elements.append(UrgencyElement(
            type="limited_stock",
            enabled=True,
            settings={
                "min_stock": 3,
                "max_stock": 15,
                "template": "🔥 Only {stock} left in stock!",
                "show_when_below": 20,
            },
        ))

        # 最近购买通知
        elements.append(UrgencyElement(
            type="recent_purchase",
            enabled=True,
            settings={
                "interval_min": 30,
                "interval_max": 120,
                "duration": 5000,
                "template": "👤 Someone from {location} bought {product} {time} ago",
                "locations": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            },
        ))

        # 在线人数显示
        elements.append(UrgencyElement(
            type="visitors_online",
            enabled=False,
            settings={
                "min_visitors": 5,
                "max_visitors": 50,
                "template": "👁 {count} people are viewing this right now",
                "update_interval": 60,
            },
        ))

        return elements

    # ==================== 交叉销售/加价销售 ====================

    def auto_setup_cross_sells(self, product_id: int, all_products: List[Dict[str, Any]],
                                num_cross_sells: int = 4) -> List[int]:
        """
        自动设置交叉销售产品

        Args:
            product_id: 当前产品ID
            all_products: 所有产品
            num_cross_sells: 数量

        Returns:
            交叉销售产品ID列表
        """
        # 交叉销售：通常是互补产品或同价位产品
        return self.auto_relate_products(
            product_id=product_id,
            all_products=all_products,
            num_related=num_cross_sells,
            strategy="price",
        )

    def auto_setup_upsells(self, product_id: int, all_products: List[Dict[str, Any]],
                           num_upsells: int = 2) -> List[int]:
        """
        自动设置加价销售产品

        Args:
            product_id: 当前产品ID
            all_products: 所有产品
            num_upsells: 数量

        Returns:
            加价销售产品ID列表
        """
        # 加价销售：更贵的同类产品
        current_product = None
        for p in all_products:
            if p.get("id") == product_id:
                current_product = p
                break

        if not current_product:
            return []

        current_price = current_product.get("price", 0)
        current_cats = set(current_product.get("category_ids", []))

        # 找同分类但更贵的产品
        candidates = []
        for p in all_products:
            if p.get("id") == product_id:
                continue
            p_cats = set(p.get("category_ids", []))
            if current_cats & p_cats and p.get("price", 0) > current_price:
                candidates.append(p)

        # 按价格升序（选择稍微贵一点的）
        candidates.sort(key=lambda x: x.get("price", 0))
        return [p["id"] for p in candidates[:num_upsells]]

    # ==================== 产品标签自动生成 ====================

    def auto_generate_product_tags(self, product_name: str, product_description: str = "",
                                    num_tags: int = 5) -> List[str]:
        """
        自动生成产品标签

        Args:
            product_name: 产品名称
            product_description: 产品描述
            num_tags: 标签数量

        Returns:
            标签列表
        """
        # 简单的关键词提取
        content = f"{product_name} {product_description}".lower()

        # 常见电商标签
        common_tags = [
            "best seller", "new arrival", "hot sale", "limited edition",
            "premium quality", "free shipping", "gift idea", "trending",
        ]

        # 从产品名提取关键词
        words = product_name.lower().split()
        name_tags = [w for w in words if len(w) > 3]

        # 组合标签
        tags = []
        tags.extend(common_tags[:2])  # 加2个通用标签
        tags.extend(name_tags[:3])  # 加3个产品名关键词

        # 去重并限制数量
        unique_tags = list(dict.fromkeys(tags))  # 保持顺序去重
        return unique_tags[:num_tags]

    # ==================== 弃购挽回 ====================

    def generate_abandoned_cart_email(self, customer_name: str, 
                                       cart_items: List[Dict[str, Any]],
                                       coupon_code: str = "") -> Dict[str, str]:
        """
        生成弃购挽回邮件

        Args:
            customer_name: 客户姓名
            cart_items: 购物车商品
            coupon_code: 优惠码

        Returns:
            邮件内容 {subject, body}
        """
        subject = f"Hey {customer_name}, you forgot something in your cart! 🛒"

        items_html = ""
        for item in cart_items[:3]:
            items_html += f"""
            <tr>
                <td style="padding: 10px;">
                    <img src="{item.get('image', '')}" alt="{item.get('name', '')}" style="width: 80px; height: auto;">
                </td>
                <td style="padding: 10px;">
                    <strong>{item.get('name', '')}</strong><br>
                    ${item.get('price', 0):.2f}
                </td>
            </tr>
            """

        coupon_section = ""
        if coupon_code:
            coupon_section = f"""
            <div style="background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <h3 style="margin: 0 0 10px 0;">🎁 Special Offer For You</h3>
                <p style="font-size: 24px; font-weight: bold; color: #e74c3c; margin: 10px 0;">
                    Use code: {coupon_code}
                </p>
                <p style="margin: 0;">Get 15% off your order!</p>
            </div>
            """

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">We noticed you left something behind...</h2>
                
                <p>Hi {customer_name},</p>
                
                <p>You had some great items in your cart and we didn't want you to miss out!</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    {items_html}
                </table>
                
                {coupon_section}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="#" style="background: #3498db; color: white; padding: 15px 30px; 
                                      text-decoration: none; border-radius: 5px; font-size: 16px;">
                        Complete Your Order →
                    </a>
                </div>
                
                <p style="color: #7f8c8d; font-size: 14px;">
                    If you have any questions, feel free to reply to this email. 
                    We're here to help!
                </p>
                
                <p style="color: #7f8c8d; font-size: 14px;">
                    Best regards,<br>
                    The Team
                </p>
            </div>
        </body>
        </html>
        """

        return {
            "subject": subject,
            "body": body,
        }

    # ==================== 产品分类自动建立 ====================

    def auto_create_categories(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据产品自动创建分类结构

        Args:
            products: 产品列表

        Returns:
            分类列表 [{name, slug, parent, description}]
        """
        # 简单的分类生成逻辑
        categories = []
        category_names = set()

        # 从产品中提取分类
        for product in products:
            cats = product.get("categories", [])
            for cat in cats:
                if isinstance(cat, dict):
                    cat_name = cat.get("name", "")
                else:
                    cat_name = str(cat)

                if cat_name and cat_name not in category_names:
                    category_names.add(cat_name)
                    categories.append({
                        "name": cat_name,
                        "slug": cat_name.lower().replace(" ", "-"),
                        "parent": 0,
                        "description": f"Browse our selection of {cat_name.lower()} products.",
                    })

        # 如果没有分类，创建默认分类
        if not categories:
            categories = [
                {"name": "All Products", "slug": "all-products", "parent": 0, "description": "All products"},
                {"name": "Best Sellers", "slug": "best-sellers", "parent": 0, "description": "Our most popular products"},
                {"name": "New Arrivals", "slug": "new-arrivals", "parent": 0, "description": "Latest products"},
                {"name": "Sale", "slug": "sale", "parent": 0, "description": "Discounted products"},
            ]

        return categories


# 单例实例
_woocommerce_service = None


def get_woocommerce_automation_service() -> WooCommerceAutomationService:
    """获取WooCommerce自动化服务单例"""
    global _woocommerce_service
    if _woocommerce_service is None:
        _woocommerce_service = WooCommerceAutomationService()
    return _woocommerce_service
