"""
WooCommerce深度自动化模块
包含产品增强、支付物流配置、营销自动化等功能
"""

from app.services.woocommerce.woocommerce_automation import (
    WooCommerceAutomationService,
    ProductReview,
    ProductFAQ,
    CouponConfig,
    PaymentGatewayConfig,
    ShippingZoneConfig,
    TrustBadge,
    UrgencyElement,
    ReviewType,
    CouponType,
    get_woocommerce_automation_service,
)

__all__ = [
    "WooCommerceAutomationService",
    "ProductReview",
    "ProductFAQ",
    "CouponConfig",
    "PaymentGatewayConfig",
    "ShippingZoneConfig",
    "TrustBadge",
    "UrgencyElement",
    "ReviewType",
    "CouponType",
    "get_woocommerce_automation_service",
]
