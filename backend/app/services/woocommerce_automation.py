"""
WooCommerce深度自动化服务
产品评论AI生成、支付配置、配送设置、优惠券、交叉销售
"""
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProductReview:
    """产品评论数据类"""
    id: Optional[int] = None
    product_id: int = 0
    author: str = ""
    email: str = ""
    avatar: str = ""
    rating: int = 5
    content: str = ""
    date: str = ""
    verified: bool = True
    helpful: int = 0
    not_helpful: int = 0
    images: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Coupon:
    """优惠券数据类"""
    code: str = ""
    discount_type: str = "percent"  # percent, fixed_cart, fixed_product
    amount: float = 0.0
    description: str = ""
    date_expires: Optional[str] = None
    usage_count: int = 0
    usage_limit: Optional[int] = None
    usage_limit_per_user: Optional[int] = None
    minimum_amount: Optional[float] = None
    maximum_amount: Optional[float] = None
    individual_use: bool = False
    exclude_sale_items: bool = False
    product_ids: List[int] = field(default_factory=list)
    exclude_product_ids: List[int] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    exclude_categories: List[str] = field(default_factory=list)
    email_restrictions: List[str] = field(default_factory=list)
    free_shipping: bool = False


@dataclass
class ShippingZone:
    """配送区域数据类"""
    id: Optional[int] = None
    name: str = ""
    order: int = 0
    enabled: bool = True
    locations: List[Dict[str, str]] = field(default_factory=list)
    methods: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PaymentGateway:
    """支付网关数据类"""
    id: str = ""
    title: str = ""
    description: str = ""
    enabled: bool = True
    order: int = 0
    settings: Dict[str, Any] = field(default_factory=dict)


class ReviewGenerator:
    """AI评论生成器"""
    
    # 评论模板
    REVIEW_TEMPLATES = {
        "positive": [
            "非常满意！{product}的质量超出预期，强烈推荐！",
            "买了{product}，用了一段时间，感觉很不错，值得购买。",
            "{product}收到了，包装很好，质量也不错，下次还会再来。",
            "性价比很高的{product}，做工精细，使用效果很好。",
            "朋友推荐的{product}，果然没让我失望，非常满意！",
            "已经是第二次购买{product}了，一如既往的好，值得信赖。",
            "{product}比想象中还要好，物流也很快，好评！",
            "用了{product}之后效果明显，会继续回购的。",
            "物超所值的{product}，推荐给大家！",
            "{product}的设计很贴心，使用起来很方便，赞一个！",
        ],
        "neutral": [
            "{product}整体还可以，就是价格稍微有点贵。",
            "买的{product}，质量一般般，凑合能用。",
            "{product}收到了，和描述的差不多，没有惊喜也没有失望。",
            "说实话，{product}还行吧，没有特别惊艳的感觉。",
            "{product}用着还可以，就是发货有点慢。",
        ],
        "detailed": [
            "我买{product}主要是为了{purpose}，用了大概{duration}了，说说我的感受。首先，{advantage1}，这点我很满意。其次，{advantage2}，也很不错。当然也有一些小缺点，比如{disadvantage}，但总体来说还是很值得购买的。如果满分10分的话，我给{score}分。",
            "作为一个{user_type}，我对{product}还是比较挑剔的。这次购买的{product}，{pros}，这些都是优点。但是{cons}，还有改进空间。综合来看，{conclusion}。",
            "对比了好几家的{product}，最后选了这家。{reason_for_choice}。收到货后，{first_impression}。使用了一段时间后，{long_term_experience}。总的来说，{final_thoughts}。",
        ],
    }
    
    # 常见用户名
    USER_NAMES = [
        "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis",
        "David Wilson", "Jessica Taylor", "Christopher Anderson", "Amanda Thomas",
        "Daniel Jackson", "Jennifer White", "Matthew Harris", "Ashley Martin",
        "Andrew Thompson", "Brittany Garcia", "James Martinez", "Samantha Robinson",
        "Ryan Clark", "Nicole Rodriguez", "Joshua Lewis", "Elizabeth Lee",
    ]
    
    # 头像URL模板（使用随机头像服务）
    AVATAR_TEMPLATES = [
        "https://i.pravatar.cc/150?img={num}",
        "https://randomuser.me/api/portraits/men/{num}.jpg",
        "https://randomuser.me/api/portraits/women/{num}.jpg",
    ]
    
    def __init__(self):
        pass
    
    def generate_review(self, 
                        product_name: str,
                        rating: Optional[int] = None,
                        review_type: str = "positive",
                        detailed: bool = False) -> ProductReview:
        """
        生成产品评论
        
        Args:
            product_name: 产品名称
            rating: 评分（1-5），None则随机
            review_type: 评论类型 (positive, neutral, detailed)
            detailed: 是否详细评论
            
        Returns:
            产品评论
        """
        # 随机评分（偏向高分）
        if rating is None:
            rating_weights = [0.05, 0.05, 0.1, 0.25, 0.55]  # 1-5星的权重
            rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]
        
        # 选择评论模板
        if detailed or rating == 5:
            templates = self.REVIEW_TEMPLATES["detailed"]
            template = random.choice(templates)
            
            # 填充模板变量
            content = template.format(
                product=product_name,
                purpose=random.choice(["日常使用", "工作需要", "送礼", "自己用"]),
                duration=random.choice(["一周", "半个月", "一个月", "两个月"]),
                advantage1=random.choice(["质量很好", "做工精细", "效果明显", "使用方便"]),
                advantage2=random.choice(["性价比高", "包装精美", "物流很快", "客服态度好"]),
                disadvantage=random.choice(["价格稍贵", "颜色选择少", "说明书不够详细", "尺寸有点大"]),
                score=random.choice(["8.5", "9", "9.5", "8"]),
                user_type=random.choice(["老用户", "新手", "专业人士", "普通消费者"]),
                pros=random.choice(["外观设计漂亮", "功能齐全", "性能稳定", "操作简单"]),
                cons=random.choice(["价格偏高", "体积稍大", "配件少", "颜色单一"]),
                conclusion=random.choice(["还是很推荐的", "总体满意", "值得购买", "可以考虑入手"]),
                reason_for_choice=random.choice(["看评价不错", "朋友推荐", "品牌信赖", "价格合适"]),
                first_impression=random.choice(["包装很精美", "外观很漂亮", "手感不错", "比想象中好"]),
                long_term_experience=random.choice(["越用越喜欢", "性能稳定", "没有出现问题", "效果越来越好"]),
                final_thoughts=random.choice(["很满意的一次购物", "会推荐给朋友", "下次还会回购", "物有所值"]),
            )
        else:
            templates = self.REVIEW_TEMPLATES.get(review_type, self.REVIEW_TEMPLATES["positive"])
            template = random.choice(templates)
            content = template.format(product=product_name)
        
        # 随机用户名
        author = random.choice(self.USER_NAMES)
        
        # 生成头像
        avatar_num = random.randint(1, 70)
        avatar_template = random.choice(self.AVATAR_TEMPLATES)
        avatar = avatar_template.format(num=avatar_num)
        
        # 随机日期（最近90天内）
        days_ago = random.randint(1, 90)
        review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
        
        # 生成邮箱
        email_username = author.lower().replace(" ", ".")
        email_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
        email = f"{email_username}@{random.choice(email_domains)}"
        
        review = ProductReview(
            product_id=0,  # 后续设置
            author=author,
            email=email,
            avatar=avatar,
            rating=rating,
            content=content,
            date=review_date,
            verified=random.random() > 0.2,  # 80%是已验证购买
            helpful=random.randint(0, 50),
        )
        
        return review
    
    def generate_reviews(self, 
                         product_name: str,
                         count: int = 10,
                         min_rating: int = 3,
                         max_rating: int = 5) -> List[ProductReview]:
        """
        批量生成产品评论
        
        Args:
            product_name: 产品名称
            count: 评论数量
            min_rating: 最低评分
            max_rating: 最高评分
            
        Returns:
            评论列表
        """
        reviews = []
        
        for i in range(count):
            rating = random.randint(min_rating, max_rating)
            
            # 部分评论使用详细模板
            detailed = random.random() < 0.3
            
            review = self.generate_review(
                product_name=product_name,
                rating=rating,
                detailed=detailed,
            )
            
            reviews.append(review)
        
        # 按日期排序（新的在前）
        reviews.sort(key=lambda r: r.date, reverse=True)
        
        return reviews
    
    def generate_review_response(self, review: ProductReview, brand_name: str = "") -> Dict[str, str]:
        """
        生成商家回复
        
        Args:
            review: 评论
            brand_name: 品牌名称
            
        Returns:
            回复内容
        """
        responses = {
            5: [
                f"感谢您的好评！{brand_name}致力于为客户提供最优质的产品和服务，您的满意是我们最大的动力。期待您的再次光临！",
                f"非常感谢您的认可！{brand_name}会继续努力，为您带来更好的购物体验。欢迎下次再来！",
                f"谢谢您的五星好评！看到您满意我们非常开心。{brand_name}会继续保持，不辜负您的信任。",
            ],
            4: [
                f"感谢您的评价！很高兴您对我们的产品感到满意。{brand_name}会继续改进，争取做到更好。",
                f"谢谢您的支持！我们会继续努力提升产品和服务质量。欢迎您下次再来{brand_name}！",
            ],
            3: [
                f"感谢您的反馈！我们很遗憾没有完全达到您的期望。{brand_name}会认真对待您的意见，不断改进。如果有任何问题，欢迎随时联系我们的客服。",
                f"谢谢您的中肯评价！您的意见对我们很重要。{brand_name}会继续努力提升产品质量。",
            ],
            2: [
                f"非常抱歉给您带来了不好的体验！{brand_name}非常重视您的反馈，我们会尽快核实并改进。请您联系我们的客服，我们会尽力为您解决问题。",
                f"很遗憾没有让您满意。{brand_name}真诚地向您道歉。请您联系我们，我们一定会给您一个满意的解决方案。",
            ],
            1: [
                f"非常抱歉！我们对给您带来的不愉快体验深感歉意。{brand_name}非常重视每一位客户的反馈，请您务必联系我们的客服团队，我们会第一时间为您解决问题。",
                f"真的很抱歉！您的不满意是我们最不愿意看到的。{brand_name}一定会认真处理您的问题，请联系我们的客服，我们会给您一个满意的答复。",
            ],
        }
        
        response_list = responses.get(review.rating, responses[5])
        response = random.choice(response_list)
        
        return {
            "author": f"{brand_name} 客服",
            "content": response,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


class CouponGenerator:
    """优惠券生成器"""
    
    COUPON_TYPES = {
        "percentage": {
            "discount_type": "percent",
            "amounts": [5, 10, 15, 20, 25, 30],
        },
        "fixed_cart": {
            "discount_type": "fixed_cart",
            "amounts": [5, 10, 15, 20, 25, 50],
        },
        "fixed_product": {
            "discount_type": "fixed_product",
            "amounts": [3, 5, 8, 10, 15, 20],
        },
    }
    
    def __init__(self):
        pass
    
    def generate_coupon_code(self, prefix: str = "SAVE") -> str:
        """生成优惠券代码"""
        import string
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(8))
        return f"{prefix}_{random_part}"
    
    def generate_coupon(self, 
                        coupon_type: str = "percentage",
                        prefix: str = "SAVE",
                        min_amount: Optional[float] = None,
                        expires_days: Optional[int] = 30,
                        usage_limit: Optional[int] = 100) -> Coupon:
        """
        生成优惠券
        
        Args:
            coupon_type: 优惠券类型 (percentage, fixed_cart, fixed_product)
            prefix: 代码前缀
            min_amount: 最低消费金额
            expires_days: 有效期天数
            usage_limit: 使用次数限制
            
        Returns:
            优惠券
        """
        type_config = self.COUPON_TYPES.get(coupon_type, self.COUPON_TYPES["percentage"])
        amount = random.choice(type_config["amounts"])
        
        code = self.generate_coupon_code(prefix)
        
        # 过期日期
        date_expires = None
        if expires_days:
            date_expires = (datetime.now() + timedelta(days=expires_days)).strftime("%Y-%m-%d")
        
        coupon = Coupon(
            code=code,
            discount_type=type_config["discount_type"],
            amount=float(amount),
            description=f"享受{amount}{'%' if coupon_type == 'percentage' else '$'}优惠",
            date_expires=date_expires,
            usage_limit=usage_limit,
            minimum_amount=min_amount,
            individual_use=True,
            exclude_sale_items=False,
        )
        
        return coupon
    
    def generate_coupons(self, count: int = 5, **kwargs) -> List[Coupon]:
        """批量生成优惠券"""
        coupons = []
        types = list(self.COUPON_TYPES.keys())
        
        for i in range(count):
            coupon_type = random.choice(types)
            coupon = self.generate_coupon(coupon_type=coupon_type, **kwargs)
            coupons.append(coupon)
        
        return coupons


class WooCommerceAutomationService:
    """WooCommerce深度自动化服务"""
    
    def __init__(self):
        self.review_generator = ReviewGenerator()
        self.coupon_generator = CouponGenerator()
    
    def auto_generate_product_reviews(self, 
                                       product_id: int,
                                       product_name: str,
                                       review_count: int = 10,
                                       avg_rating: float = 4.5) -> List[ProductReview]:
        """
        自动生成产品评论
        
        Args:
            product_id: 产品ID
            product_name: 产品名称
            review_count: 评论数量
            avg_rating: 平均评分目标
            
        Returns:
            评论列表
        """
        # 根据目标平均分计算评分分布
        min_rating = max(1, int(avg_rating - 1.5))
        max_rating = min(5, int(avg_rating + 0.5))
        
        reviews = self.review_generator.generate_reviews(
            product_name=product_name,
            count=review_count,
            min_rating=min_rating,
            max_rating=max_rating,
        )
        
        # 设置产品ID
        for review in reviews:
            review.product_id = product_id
        
        logger.info(f"Generated {len(reviews)} reviews for product {product_id}")
        return reviews
    
    def auto_setup_payment_gateways(self, 
                                     currency: str = "USD",
                                     country: str = "US") -> List[PaymentGateway]:
        """
        自动配置支付网关
        
        Args:
            currency: 货币
            country: 国家
            
        Returns:
            支付网关列表
        """
        gateways = []
        
        # PayPal
        paypal = PaymentGateway(
            id="paypal",
            title="PayPal",
            description="通过PayPal安全支付",
            enabled=True,
            order=1,
            settings={
                "title": "PayPal",
                "description": "通过PayPal安全支付",
                "email": "paypal@example.com",
                "testmode": "no",
                "debug": "no",
                "ipn_notification": "yes",
                "receive_payments": "yes",
                "invoice_prefix": "WPForge-",
            },
        )
        gateways.append(paypal)
        
        # Stripe
        stripe = PaymentGateway(
            id="stripe",
            title="Credit Card (Stripe)",
            description="使用信用卡安全支付",
            enabled=True,
            order=2,
            settings={
                "title": "Credit Card",
                "description": "使用Visa, MasterCard, American Express支付",
                "testmode": "no",
                "debug": "no",
                "publishable_key": "",
                "secret_key": "",
                "webhook_secret": "",
                "statement_descriptor": "WPForge Store",
                "capture": "yes",
                "payment_request": "yes",
            },
        )
        gateways.append(stripe)
        
        # 货到付款
        cod = PaymentGateway(
            id="cod",
            title="Cash on Delivery",
            description="货到付款",
            enabled=False,
            order=3,
            settings={
                "title": "Cash on Delivery",
                "description": "收到货物后付款",
                "instructions": "请准备好现金，快递员会在送货时收取。",
                "enable_for_methods": "",
                "enable_for_virtual": "no",
            },
        )
        gateways.append(cod)
        
        # 银行转账
        bacs = PaymentGateway(
            id="bacs",
            title="Direct Bank Transfer",
            description="银行直接转账",
            enabled=False,
            order=4,
            settings={
                "title": "Direct Bank Transfer",
                "description": "通过银行转账支付，款项到账后发货。",
                "instructions": "请将款项转入以下银行账户：",
                "account_name": "WPForge Ltd.",
                "account_number": "12345678",
                "bank_name": "Example Bank",
                "sort_code": "12-34-56",
                "iban": "",
                "bic": "",
            },
        )
        gateways.append(bacs)
        
        logger.info(f"Setup {len(gateways)} payment gateways")
        return gateways
    
    def auto_setup_shipping_zones(self, 
                                   base_country: str = "US",
                                   base_state: str = "CA") -> List[ShippingZone]:
        """
        自动配置配送区域
        
        Args:
            base_country: 基础国家
            base_state: 基础州/省
            
        Returns:
            配送区域列表
        """
        zones = []
        
        # 国内配送
        domestic_zone = ShippingZone(
            name=f"{base_country} Domestic",
            order=0,
            enabled=True,
            locations=[
                {"code": base_country, "type": "country"},
            ],
            methods=[
                {
                    "id": "flat_rate",
                    "title": "Standard Shipping",
                    "enabled": True,
                    "settings": {
                        "title": "Standard Shipping",
                        "tax_status": "taxable",
                        "cost": "5.99",
                        "class_costs": "",
                        "no_class_cost": "",
                        "calculation_type": "class",
                    },
                },
                {
                    "id": "free_shipping",
                    "title": "Free Shipping",
                    "enabled": True,
                    "settings": {
                        "title": "Free Shipping",
                        "requires": "min_amount",
                        "min_amount": "50.00",
                        "ignore_discounts": "no",
                    },
                },
                {
                    "id": "flat_rate",
                    "title": "Express Shipping",
                    "enabled": True,
                    "settings": {
                        "title": "Express Shipping",
                        "tax_status": "taxable",
                        "cost": "14.99",
                    },
                },
            ],
        )
        zones.append(domestic_zone)
        
        # 国际配送
        international_zone = ShippingZone(
            name="International",
            order=1,
            enabled=True,
            locations=[
                {"code": "EU", "type": "continent"},
                {"code": "AS", "type": "continent"},
                {"code": "OC", "type": "continent"},
                {"code": "NA", "type": "continent"},
                {"code": "SA", "type": "continent"},
                {"code": "AF", "type": "continent"},
            ],
            methods=[
                {
                    "id": "flat_rate",
                    "title": "International Shipping",
                    "enabled": True,
                    "settings": {
                        "title": "International Shipping",
                        "tax_status": "none",
                        "cost": "19.99",
                    },
                },
                {
                    "id": "flat_rate",
                    "title": "Express International",
                    "enabled": True,
                    "settings": {
                        "title": "Express International",
                        "tax_status": "none",
                        "cost": "39.99",
                    },
                },
            ],
        )
        zones.append(international_zone)
        
        # 本地自提
        local_zone = ShippingZone(
            name=f"{base_state} Local Pickup",
            order=2,
            enabled=True,
            locations=[
                {"code": f"{base_country}:{base_state}", "type": "state"},
            ],
            methods=[
                {
                    "id": "local_pickup",
                    "title": "Local Pickup",
                    "enabled": True,
                    settings": {
                        "title": "Local Pickup",
                        "tax_status": "none",
                        "cost": "0.00",
                    },
                },
            ],
        )
        zones.append(local_zone)
        
        logger.info(f"Setup {len(zones)} shipping zones")
        return zones
    
    def auto_generate_coupons(self, 
                               count: int = 5,
                               types: Optional[List[str]] = None) -> List[Coupon]:
        """
        自动生成优惠券
        
        Args:
            count: 优惠券数量
            types: 优惠券类型列表
            
        Returns:
            优惠券列表
        """
        coupons = []
        types = types or ["percentage", "fixed_cart", "fixed_product"]
        
        for i in range(count):
            coupon_type = random.choice(types)
            coupon = self.coupon_generator.generate_coupon(coupon_type=coupon_type)
            coupons.append(coupon)
        
        logger.info(f"Generated {len(coupons)} coupons")
        return coupons
    
    def auto_link_related_products(self, 
                                    product_id: int,
                                    all_products: List[Dict[str, Any]],
                                    related_count: int = 4,
                                    cross_sell_count: int = 2,
                                    upsell_count: int = 2) -> Dict[str, List[int]]:
        """
        自动关联相关产品、交叉销售、追加销售
        
        Args:
            product_id: 当前产品ID
            all_products: 所有产品列表
            related_count: 相关产品数量
            cross_sell_count: 交叉销售数量
            upsell_count: 追加销售数量
            
        Returns:
            关联结果字典
        """
        # 过滤掉当前产品
        other_products = [p for p in all_products if p.get("id") != product_id]
        
        if not other_products:
            return {
                "related": [],
                "cross_sells": [],
                "upsells": [],
            }
        
        # 相关产品（随机选择）
        related = random.sample(
            [p["id"] for p in other_products],
            min(related_count, len(other_products))
        )
        
        # 交叉销售（通常是互补产品，这里简化为随机）
        remaining = [p["id"] for p in other_products if p["id"] not in related]
        cross_sells = random.sample(
            remaining,
            min(cross_sell_count, len(remaining))
        )
        
        # 追加销售（通常是更贵的产品，这里简化为随机）
        remaining2 = [pid for pid in remaining if pid not in cross_sells]
        upsells = random.sample(
            remaining2,
            min(upsell_count, len(remaining2))
        )
        
        result = {
            "related": related,
            "cross_sells": cross_sells,
            "upsells": upsells,
        }
        
        logger.info(f"Linked products for {product_id}: {len(related)} related, {len(cross_sells)} cross-sells, {len(upsells)} upsells")
        return result
    
    def auto_setup_store_pages(self, store_name: str = "WPForge Store") -> List[Dict[str, Any]]:
        """
        自动创建WooCommerce页面
        
        Args:
            store_name: 商店名称
            
        Returns:
            页面列表
        """
        pages = [
            {
                "title": "Shop",
                "slug": "shop",
                "content": "",
                "status": "publish",
                "type": "page",
                "is_woocommerce": True,
                "woocommerce_page": "shop",
            },
            {
                "title": "Cart",
                "slug": "cart",
                "content": "[woocommerce_cart]",
                "status": "publish",
                "type": "page",
                "is_woocommerce": True,
                "woocommerce_page": "cart",
            },
            {
                "title": "Checkout",
                "slug": "checkout",
                "content": "[woocommerce_checkout]",
                "status": "publish",
                "type": "page",
                "is_woocommerce": True,
                "woocommerce_page": "checkout",
            },
            {
                "title": "My Account",
                "slug": "my-account",
                "content": "[woocommerce_my_account]",
                "status": "publish",
                "type": "page",
                "is_woocommerce": True,
                "woocommerce_page": "myaccount",
            },
            {
                "title": "Terms and Conditions",
                "slug": "terms-and-conditions",
                "content": f"<h1>Terms and Conditions</h1>\n<p>Welcome to {store_name}!</p>\n<p>These terms and conditions outline the rules and regulations for the use of our website.</p>",
                "status": "publish",
                "type": "page",
                "is_woocommerce": False,
            },
            {
                "title": "Privacy Policy",
                "slug": "privacy-policy",
                "content": f"<h1>Privacy Policy</h1>\n<p>At {store_name}, we are committed to protecting your privacy...</p>",
                "status": "publish",
                "type": "page",
                "is_woocommerce": False,
            },
            {
                "title": "Refund Policy",
                "slug": "refund-policy",
                "content": "<h1>Refund Policy</h1>\n<p>We offer a 30-day return policy on most items...</p>",
                "status": "publish",
                "type": "page",
                "is_woocommerce": False,
            },
            {
                "title": "Shipping Policy",
                "slug": "shipping-policy",
                "content": "<h1>Shipping Policy</h1>\n<p>We offer worldwide shipping...</p>",
                "status": "publish",
                "type": "page",
                "is_woocommerce": False,
            },
        ]
        
        logger.info(f"Generated {len(pages)} store pages")
        return pages
    
    def get_woocommerce_settings(self, 
                                  store_name: str = "WPForge Store",
                                  currency: str = "USD",
                                  country: str = "US") -> Dict[str, Any]:
        """
        获取推荐的WooCommerce设置
        
        Args:
            store_name: 商店名称
            currency: 货币
            country: 国家
            
        Returns:
            设置字典
        """
        return {
            "general": {
                "woocommerce_store_address": "",
                "woocommerce_store_address_2": "",
                "woocommerce_store_city": "",
                "woocommerce_store_postcode": "",
                "woocommerce_default_country": f"{country}:CA",
                "woocommerce_default_customer_address": "base",
                "woocommerce_currency": currency,
                "woocommerce_currency_pos": "left",
                "woocommerce_price_thousand_sep": ",",
                "woocommerce_price_decimal_sep": ".",
                "woocommerce_price_num_decimals": "2",
                "woocommerce_calc_taxes": "no",
                "woocommerce_enable_coupons": "yes",
                "woocommerce_calc_discounts_sequentially": "no",
            },
            "products": {
                "woocommerce_shop_page_id": "",
                "woocommerce_cart_page_id": "",
                "woocommerce_checkout_page_id": "",
                "woocommerce_myaccount_page_id": "",
                "woocommerce_terms_page_id": "",
                "woocommerce_default_catalog_orderby": "popularity",
                "woocommerce_catalog_columns": "4",
                "woocommerce_catalog_rows": "4",
                "woocommerce_placeholder_image": "",
                "woocommerce_enable_reviews": "yes",
                "woocommerce_review_rating_verification_label": "yes",
                "woocommerce_review_rating_verification_required": "no",
                "woocommerce_enable_review_rating": "yes",
                "woocommerce_review_rating_required": "yes",
            },
            "shipping": {
                "woocommerce_shipping_cost_requires_address": "yes",
                "woocommerce_ship_to_destination": "shipping",
                "woocommerce_shipping_debug_mode": "no",
                "woocommerce_shipping_calculator_enable_cart": "yes",
                "woocommerce_shipping_calculator_enable_shipping": "yes",
            },
            "payments": {
                "woocommerce_gateway_order": ["paypal", "stripe", "cod", "bacs"],
            },
            "accounts": {
                "woocommerce_enable_myaccount_registration": "yes",
                "woocommerce_registration_generate_username": "yes",
                "woocommerce_registration_generate_password": "yes",
                "woocommerce_save_payment_methods": "yes",
                "woocommerce_erasure_request_removes_order_data": "yes",
                "woocommerce_erasure_request_removes_download_data": "yes",
            },
            "email": {
                "woocommerce_email_from_name": store_name,
                "woocommerce_email_from_address": "noreply@example.com",
                "woocommerce_email_header_image": "",
                "woocommerce_email_footer_text": f"{store_name} - All rights reserved.",
                "woocommerce_email_base_color": "#7f54b3",
                "woocommerce_email_background_color": "#f7f7f7",
                "woocommerce_email_body_background_color": "#ffffff",
                "woocommerce_email_text_color": "#3c3c3c",
            },
        }
    
    def get_cro_optimization_tips(self) -> List[str]:
        """获取转化率优化建议"""
        return [
            "添加信任徽章和安全标识",
            "显示库存紧迫感（仅剩X件）",
            "添加社交证明（已售X件、X人正在查看）",
            "添加倒计时促销计时器",
            "优化产品图片质量和数量",
            "添加产品视频展示",
            "显示详细的产品规格和参数",
            "添加真实的用户评价和评分",
            "提供多种支付方式",
            "显示运费和配送时间预估",
            "添加常见问题解答",
            "提供简单的退换货政策",
            "优化结账流程（减少步骤）",
            "添加访客优惠弹窗",
            "添加弃购挽回邮件",
            "优化移动端购物体验",
            "添加一键购买按钮",
            "显示最近购买通知",
            "添加产品对比功能",
            "提供愿望清单功能",
        ]


# 全局WooCommerce自动化服务实例
wc_automation_service = WooCommerceAutomationService()
