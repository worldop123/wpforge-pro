// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  avatar?: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// 站点相关类型
export interface Site {
  id: number
  name: string
  wp_url: string
  wp_username: string
  language: string
  currency: string
  page_builder: string
  status: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SiteCreate {
  name: string
  wp_url: string
  wp_username: string
  wp_password: string
  wc_consumer_key?: string
  wc_consumer_secret?: string
  language?: string
  currency?: string
  page_builder?: string
}

export interface SiteUpdate {
  name?: string
  wp_url?: string
  wp_username?: string
  wp_password?: string
  wc_consumer_key?: string
  wc_consumer_secret?: string
  language?: string
  currency?: string
  page_builder?: string
  is_active?: boolean
}

// 产品相关类型
export interface Product {
  id: number
  site_id: number
  name: string
  sku?: string
  description?: string
  short_description?: string
  price?: number
  regular_price?: number
  sale_price?: number
  stock_quantity?: number
  status: string
  wp_product_id?: number
  images?: ProductImage[]
  categories?: ProductCategory[]
  tags?: string[]
  attributes?: ProductAttribute[]
  variations?: ProductVariation[]
  seo_title?: string
  seo_description?: string
  created_at: string
  updated_at: string
}

export interface ProductImage {
  id: number
  src: string
  name: string
  alt?: string
  position?: number
}

export interface ProductCategory {
  id: number
  name: string
  slug: string
  parent?: number
}

export interface ProductAttribute {
  id: number
  name: string
  options: string[]
  visible?: boolean
  variation?: boolean
}

export interface ProductVariation {
  id: number
  sku?: string
  price?: number
  regular_price?: number
  sale_price?: number
  stock_quantity?: number
  attributes: { name: string; option: string }[]
}

// 任务相关类型
export interface Task {
  id: number
  name: string
  task_type: string
  status: TaskStatus
  progress: number
  status_message?: string
  total_items?: number
  processed_items?: number
  failed_items?: number
  site_id?: number
  user_id: number
  params?: Record<string, any>
  result?: Record<string, any>
  error_message?: string
  celery_task_id?: string
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface TaskLog {
  id: number
  task_id: number
  level: string
  message: string
  details?: Record<string, any>
  created_at: string
}

// 采集相关类型
export interface ScrapeRequest {
  url: string
  site_id?: number
  max_products?: number
  auto_translate?: boolean
  auto_import?: boolean
  target_language?: string
  proxy_enabled?: boolean
  scrape_images?: boolean
  scrape_variations?: boolean
  scrape_reviews?: boolean
}

export interface ScrapeResponse {
  task_id: string
  status: string
  message: string
}

export interface SiteAnalysis {
  site_type: string
  confidence: number
  pagination_type: string
  pagination_selector?: string
  product_list_selector?: string
  product_detail_url_pattern?: string
  currency?: string
  language?: string
  has_anti_detection: boolean
  detected_fields: DetectedField[]
  recommendations: string[]
}

export interface DetectedField {
  name: string
  selector: string
  confidence: number
  needs_translation: boolean
}

// 翻译相关类型
export interface TranslateRequest {
  text: string
  source_language?: string
  target_language: string
  engine?: string
  polish?: boolean
}

export interface TranslateResponse {
  original_text: string
  translated_text: string
  source_language: string
  target_language: string
  engine: string
  quality_score?: number
}

// SEO相关类型
export interface SEOAuditResult {
  url: string
  overall_score: number
  content_score: number
  technical_score: number
  performance_score: number
  title?: string
  description?: string
  keywords?: string[]
  word_count?: number
  keyword_density?: number
  issues: SEOIssue[]
  recommendations: string[]
  headings: string[]
  images: SEOImage[]
  links: SEOLink[]
}

export interface SEOIssue {
  type: string
  severity: 'error' | 'warning' | 'info'
  message: string
  suggestion?: string
}

export interface SEOImage {
  src: string
  alt?: string
  has_alt: boolean
}

export interface SEOLink {
  href: string
  text?: string
  is_internal: boolean
  is_external: boolean
}

// 价格相关类型
export interface PriceCalculateRequest {
  base_price: number
  base_currency: string
  target_currency: string
  strategy?: string
  markup_percentage?: number
  markup_fixed?: number
  psychological_pricing?: boolean
}

export interface PriceCalculateResponse {
  base_price: number
  base_currency: string
  target_currency: string
  exchange_rate: number
  final_price: number
  strategy: string
  markup_percentage?: number
  psychological_pricing: boolean
}

// WordPress相关类型
export interface WPImportRequest {
  site_id: number
  product_ids?: number[]
  import_method?: string
  update_if_exists?: boolean
  skip_images?: boolean
  publish?: boolean
}

export interface WPImportResponse {
  task_id: string
  status: string
  message: string
  import_method: string
}

// AI相关类型
export interface AIChatRequest {
  message: string
  model?: string
  temperature?: number
  max_tokens?: number
  history?: Array<{ role: string; content: string }>
}

export interface AIChatResponse {
  response: string
  model: string
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

// 代理相关类型
export interface Proxy {
  id?: number
  host: string
  port: number
  protocol: string
  username?: string
  password?: string
  country?: string
  quality?: string
  provider?: string
  is_alive?: boolean
  response_time?: number
  last_checked?: string
}

// 监控相关类型
export interface MonitoringOverview {
  sites: number
  products: number
  tasks: {
    total: number
    pending: number
    running: number
    completed: number
    failed: number
    cancelled: number
  }
  system_status: string
  uptime: string
}

export interface SiteStatus {
  site_id: number
  site_name: string
  url: string
  is_up: boolean
  response_time_ms: number
  status_code: number
  last_checked: string
  uptime_24h: number
  uptime_7d: number
  uptime_30d: number
}

export interface Alert {
  id: number
  site_id: number
  site_name: string
  type: string
  severity: 'critical' | 'warning' | 'info'
  message: string
  created_at: string
  resolved: boolean
}

// 通用响应类型
export interface SuccessResponse<T = any> {
  success: boolean
  message: string
  data?: T
}

export interface PaginatedResponse<T = any> {
  success: boolean
  message: string
  data: {
    items: T[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

export interface ErrorResponse {
  success: boolean
  message: string
  detail?: string
  errors?: Record<string, string[]>
}
