"""
Pydantic Schemas - 数据验证模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl


# ==================== 用户相关 Schema ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    is_admin: bool
    is_superuser: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None


# ==================== 站点相关 Schema ====================

class SiteBase(BaseModel):
    """站点基础模型"""
    name: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl
    description: Optional[str] = None
    wp_url: HttpUrl
    wp_username: str
    wp_password: str
    language: str = "zh-CN"
    currency: str = "CNY"
    price_markup: int = 30
    page_builder: str = "elementor"


class SiteCreate(SiteBase):
    """站点创建模型"""
    pass


class SiteUpdate(BaseModel):
    """站点更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    wp_username: Optional[str] = None
    wp_password: Optional[str] = None
    language: Optional[str] = None
    currency: Optional[str] = None
    price_markup: Optional[int] = None
    page_builder: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class SiteResponse(SiteBase):
    """站点响应模型"""
    id: int
    status: str
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SiteListResponse(BaseModel):
    """站点列表响应"""
    items: List[SiteResponse]
    total: int
    page: int
    page_size: int


# ==================== 产品相关 Schema ====================

class ProductBase(BaseModel):
    """产品基础模型"""
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    regular_price: Optional[float] = None
    sale_price: Optional[float] = None
    currency: str = "USD"
    stock_quantity: int = 0
    in_stock: bool = True
    categories: List[str] = []
    tags: List[str] = []
    images: List[Dict[str, Any]] = []
    attributes: List[Dict[str, Any]] = []
    variations: List[Dict[str, Any]] = []
    is_variable: bool = False
    source_url: Optional[str] = None
    source_site: Optional[str] = None


class ProductCreate(ProductBase):
    """产品创建模型"""
    pass


class ProductUpdate(BaseModel):
    """产品更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    regular_price: Optional[float] = None
    sale_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    in_stock: Optional[bool] = None
    status: Optional[str] = None
    wp_status: Optional[str] = None


class ProductResponse(ProductBase):
    """产品响应模型"""
    id: int
    slug: Optional[str] = None
    price: Optional[float] = None
    translated: bool = False
    translation_language: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    wp_post_id: Optional[int] = None
    wp_status: str = "draft"
    status: str = "draft"
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """产品列表响应"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int


# ==================== 任务相关 Schema ====================

class TaskBase(BaseModel):
    """任务基础模型"""
    name: str
    task_type: str
    params: Dict[str, Any] = {}
    priority: int = 5


class TaskCreate(TaskBase):
    """任务创建模型"""
    site_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """任务更新模型"""
    status: Optional[str] = None
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int
    task_id: Optional[str] = None
    status: str
    progress: float
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: float = 0
    site_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int


# ==================== 采集相关 Schema ====================

class ScrapeRequest(BaseModel):
    """采集请求模型"""
    url: HttpUrl
    site_id: Optional[int] = None
    max_products: Optional[int] = None
    auto_translate: bool = True
    auto_import: bool = False
    target_language: Optional[str] = None
    proxy_enabled: Optional[bool] = None
    scrape_images: bool = True
    scrape_variations: bool = True
    scrape_reviews: bool = False


class ScrapeResponse(BaseModel):
    """采集响应模型"""
    task_id: str
    status: str
    message: str
    estimated_count: Optional[int] = None


class ScrapeResult(BaseModel):
    """采集结果模型"""
    success: bool
    total_scraped: int
    products: List[Dict[str, Any]] = []
    errors: List[str] = []
    duration: float


# ==================== 翻译相关 Schema ====================

class TranslateRequest(BaseModel):
    """翻译请求模型"""
    text: str
    source_language: str = "auto"
    target_language: str = "en"
    engine: str = "ai"
    polish: bool = True
    seo_optimize: bool = False


class TranslateResponse(BaseModel):
    """翻译响应模型"""
    translated_text: str
    source_language: str
    target_language: str
    engine: str
    quality_score: Optional[int] = None
    is_polished: bool = False


class BatchTranslateRequest(BaseModel):
    """批量翻译请求"""
    texts: List[str]
    source_language: str = "auto"
    target_language: str = "en"
    engine: str = "ai"


class BatchTranslateResponse(BaseModel):
    """批量翻译响应"""
    translations: List[Dict[str, Any]]
    total: int
    success_count: int


# ==================== SEO相关 Schema ====================

class SEOAuditRequest(BaseModel):
    """SEO审计请求"""
    url: HttpUrl
    site_id: Optional[int] = None
    deep_audit: bool = False


class SEOAuditResponse(BaseModel):
    """SEO审计响应"""
    task_id: Optional[str] = None
    url: str
    overall_score: int
    content_score: int
    technical_score: int
    performance_score: int
    issues: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []


class SEOOptimizeRequest(BaseModel):
    """SEO优化请求"""
    product_id: int
    site_id: Optional[int] = None
    optimize_title: bool = True
    optimize_description: bool = True
    optimize_slug: bool = True
    optimize_images: bool = True
    optimize_schema: bool = True


# ==================== 价格相关 Schema ====================

class PriceCalculateRequest(BaseModel):
    """价格计算请求"""
    base_price: float
    source_currency: str = "USD"
    target_currency: str = "CNY"
    markup_percentage: Optional[float] = None
    optimize_ending: bool = True


class PriceCalculateResponse(BaseModel):
    """价格计算响应"""
    original_price: float
    original_currency: str
    target_price: float
    target_currency: str
    exchange_rate: float
    markup_amount: float
    final_price: float
    is_optimized: bool


# ==================== WordPress相关 Schema ====================

class WPImportRequest(BaseModel):
    """WordPress导入请求"""
    site_id: int
    product_ids: Optional[List[int]] = None
    import_images: bool = True
    create_categories: bool = True
    create_variations: bool = True
    publish: bool = False


class WPImportResponse(BaseModel):
    """WordPress导入响应"""
    task_id: str
    status: str
    message: str
    total_products: int


# ==================== AI相关 Schema ====================

class AIChatRequest(BaseModel):
    """AI聊天请求"""
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class AIChatResponse(BaseModel):
    """AI聊天响应"""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = {}


class AISiteAnalyzeRequest(BaseModel):
    """AI站点分析请求"""
    url: HttpUrl
    analyze_type: str = "full"  # full, structure, content, seo


class AISiteAnalyzeResponse(BaseModel):
    """AI站点分析响应"""
    platform: str
    cms: Optional[str] = None
    page_builder: Optional[str] = None
    language: str
    currency: Optional[str] = None
    structure: Dict[str, Any] = {}
    recommendations: List[str] = []


# ==================== 通用响应 Schema ====================

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """分页响应基类"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
