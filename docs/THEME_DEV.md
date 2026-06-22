# WPForge Theme 开发指南

本文档详细介绍了WPForge专属主题的架构、定制方法和开发规范。

## 目录

- [主题概述](#主题概述)
- [文件结构](#文件结构)
- [核心功能模块](#核心功能模块)
- [主题定制](#主题定制)
- [钩子系统](#钩子系统)
- [WPForge API集成](#wpforge-api集成)
- [电商漏斗数据面板](#电商漏斗数据面板)
- [性能优化](#性能优化)
- [子主题开发](#子主题开发)
- [常见问题](#常见问题)

## 主题概述

### 主题信息
- **主题名称**：WPForge Theme
- **副标题**：AI-Driven Ultra-Lightweight WordPress Theme
- **版本**：1.0.0
- **许可证**：GPL v3
- **最低WordPress版本**：5.8
- **最低PHP版本**：7.4

### 核心理念
1. **极致轻量化**：纯代码，无冗余，前端加载 < 50KB CSS + < 30KB JS
2. **SEO原生优化**：Schema、语义化HTML、速度优化全部内置
3. **深度集成**：WPForge可以100%控制主题所有设置
4. **页面构建器友好**：原生支持Elementor、Bricks Builder
5. **全页面覆盖**：首页、文章页、页面、产品页、分类页、搜索页、404页等
6. **高度可定制**：大量自定义选项，但默认值已经最优

### 性能指标
| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| CSS总大小 | < 50KB | ~35KB |
| CSS (gzip) | < 15KB | ~10KB |
| JS总大小 | < 30KB | ~20KB |
| JS (gzip) | < 10KB | ~7KB |
| Google PageSpeed (移动端) | > 95分 | 96-98分 |
| Google PageSpeed (桌面端) | > 98分 | 98-100分 |
| LCP | < 1.5s | < 1.2s |
| FID | < 100ms | < 50ms |
| CLS | < 0.1 | < 0.05 |

## 文件结构

```
wpforge-theme/
├── style.css              # 主题主样式（极简，主要用变量）
├── functions.php          # 主题功能入口
├── index.php              # 主模板
├── header.php             # 头部
├── footer.php             # 底部
├── sidebar.php            # 侧边栏
├── single.php             # 文章页
├── page.php               # 单页面
├── archive.php            # 归档页
├── category.php           # 分类页
├── tag.php                # 标签页
├── search.php             # 搜索页
├── 404.php                # 404页面
├── front-page.php         # 首页
├── home.php               # 博客页
├── screenshot.png         # 主题截图
├── readme.txt             # 主题说明
├── woocommerce/           # WooCommerce模板覆盖
│   ├── single-product.php
│   ├── archive-product.php
│   ├── cart.php
│   ├── checkout.php
│   ├── myaccount.php
│   └── ...
├── inc/                   # 核心功能
│   ├── customizer.php     # 自定义设置（10大面板）
│   ├── seo.php            # SEO优化模块
│   ├── performance.php    # 性能优化模块
│   ├── builder-support.php # 页面构建器支持
│   ├── woocommerce.php    # WooCommerce支持
│   ├── hooks.php          # 钩子系统
│   ├── wpforge-api.php    # WPForge API集成
│   ├── template-tags.php  # 模板标签
│   └── funnel-dashboard/  # 电商漏斗数据面板
│       ├── class-funnel-dashboard.php
│       ├── class-data-collector.php
│       ├── class-data-processor.php
│       ├── class-insights-engine.php
│       ├── class-rest-api.php
│       └── admin-page.php
├── assets/
│   ├── css/
│   │   ├── main.css       # 主样式
│   │   ├── header.css     # 头部样式
│   │   ├── footer.css     # 底部样式
│   │   ├── single.css     # 文章样式
│   │   ├── woocommerce.css # WooCommerce样式
│   │   └── funnel-dashboard.css
│   ├── js/
│   │   ├── main.js        # 主脚本
│   │   ├── navigation.js  # 导航脚本
│   │   └── funnel-dashboard.js
│   └── images/            # 主题图片
└── languages/             # 多语言支持
    └── wpforge-theme.pot  # 翻译模板
```

## 核心功能模块

### 1. Customizer自定义设置

主题提供10大设置面板，全部使用WordPress原生Customizer API。

#### 面板列表
1. **站点身份** - Logo、Favicon、标题、描述
2. **全局设置** - 布局、颜色、排版、按钮
3. **头部设置** - 布局、高度、粘性、顶部栏、移动端
4. **底部设置** - Widget列数、底部栏、回到顶部
5. **博客/文章设置** - 列表布局、单篇布局、显示元素
6. **页面设置** - 模板、标题、特色图片
7. **WooCommerce设置** - 产品列表、详情页、购物车
8. **SEO设置** - 基础SEO、Schema、面包屑、社交
9. **性能优化设置** - CSS、JS、图片、字体、WP优化
10. **数据面板设置** - 电商漏斗仪表盘配置

#### 使用示例
```php
// 获取主题设置
$primary_color = get_theme_mod('color_primary', '#2563eb');
$header_layout = get_theme_mod('header_layout', 'default');

// 输出CSS变量
function wpforge_custom_css_variables() {
    $primary = get_theme_mod('color_primary', '#2563eb');
    echo ":root { --wpforge-color-primary: {$primary}; }";
}
add_action('wp_head', 'wpforge_custom_css_variables');
```

### 2. SEO优化模块

内置完整的SEO优化功能，无需额外SEO插件。

#### 功能列表
- **标题优化**：自动生成SEO友好的标题，可自定义模板
- **Meta描述**：自动从内容提取，可自定义每个页面
- **关键词**：自动提取，可自定义
- **Schema结构化数据**：10+种类型自动生成
- **面包屑导航**：内置面包屑，支持Schema标记
- **社交分享优化**：Open Graph + Twitter Cards
- **Canonical URL**：自动生成规范URL
- **语义化HTML5**：正确使用header/nav/main/article/section等标签
- **图片ALT自动生成**：从图片文件名或文章标题生成

#### Schema类型
- Article / BlogPosting
- Product（WooCommerce）
- BreadcrumbList
- Review / AggregateRating
- FAQPage
- HowTo
- Organization
- WebSite
- LocalBusiness
- Person

#### 使用示例
```php
// 手动添加Schema
add_filter('wpforge_schema_data', function($schema) {
    $schema['@type'] = 'Product';
    $schema['name'] = 'Product Name';
    return $schema;
});

// 禁用自动Schema
add_filter('wpforge_enable_schema', '__return_false');
```

### 3. 性能优化模块

内置完整的性能优化功能，无需额外优化插件。

#### CSS优化
- CSS合并与压缩
- 关键CSS内联（Critical CSS）
- 非关键CSS延迟加载
- 移除未使用CSS（自动检测）
- 禁用Gutenberg块样式（不用时）
- 禁用表情符号样式

#### JS优化
- JS延迟加载（defer/async）
- 延迟到用户交互后加载
- JS合并与压缩
- 禁用jQuery Migrate
- 可选禁用jQuery（前端完全不依赖）
- 禁用WP Embed脚本

#### 图片优化
- 原生图片延迟加载（loading="lazy"）
- JS延迟加载（更可控）
- 响应式图片（srcset + sizes）
- WebP格式支持（自动检测浏览器支持）
- 图片尺寸自动裁剪
- 图片占位符（模糊/低质量/空白）
- 图片宽度/高度属性（防止CLS）

#### WordPress优化
- 禁用XML-RPC
- 禁用REST API未授权端点
- 移除WP版本号
- 移除wlmanifest/RSD链接
- 移除短链接
- 禁用表情符号
- 禁用Embeds
- 心跳API频率控制
- 修订版本数限制

#### 预加载优化
- DNS预解析（dns-prefetch）
- 预连接（preconnect）
- 预加载关键资源（preload）
- 预获取（prefetch）

#### 使用示例
```php
// 添加预连接
add_filter('wpforge_preconnect_urls', function($urls) {
    $urls[] = 'https://fonts.googleapis.com';
    return $urls;
});

// 禁用图片懒加载
add_filter('wpforge_enable_lazy_load', '__return_false');
```

### 4. 页面构建器支持

深度支持Elementor和Bricks Builder，完美兼容。

#### Elementor集成
- 原生支持Elementor全宽页面
- 主题样式与Elementor样式同步
  - 颜色同步：主题主色 → Elementor全局颜色
  - 字体同步：主题字体 → Elementor全局字体
  - 按钮样式同步
  - 表单样式同步
- Elementor主题位置支持（Header/Footer/Single/Archive等）
- Elementor Pro兼容
- 性能优化：Elementor CSS优化、延迟加载

#### Bricks Builder集成
- 原生支持Bricks Builder
- 主题样式与Bricks全局样式同步
- Bricks模板系统兼容
- Bricks条件逻辑支持

#### 页面模板
- 默认模板（有Header/Footer）
- 全宽模板（无侧边栏）
- Canvas模板（完全空白，只有内容）
- 无Header模板
- 无Footer模板
- 着陆页模板（Landing Page）

#### 使用示例
```php
// 启用Elementor主题位置
add_theme_support('elementor-theme-builder');

// 自定义Elementor颜色
add_filter('elementor/frontend/print_css/custom_css', function($css) {
    return $css;
});
```

### 5. WooCommerce集成

完整的WooCommerce模板覆盖和深度集成。

#### 产品列表页优化
- 产品卡片样式
- 悬停效果
- 快速查看按钮
- 添加到购物车AJAX
- 产品标签（新品、热销、特价）

#### 产品详情页优化
- 图片画廊优化
- 缩略图布局（底部/左侧/隐藏）
- 产品信息排版
- 变体选择器样式
- 数量选择器样式
- 添加到购物车按钮
- 相关产品/交叉销售/追加销售

#### 购物车与结算页优化
- 购物车页面优化
- 迷你购物车样式
- 结账页面优化
- 免运费提示
- 信任徽章
- 紧迫感元素

#### 与主题系统同步
- 颜色同步
- 字体同步
- 按钮样式同步
- 表单样式同步

#### 使用示例
```php
// 移除WooCommerce侧边栏
remove_action('woocommerce_sidebar', 'woocommerce_get_sidebar', 10);

// 自定义产品卡片
add_action('woocommerce_before_shop_loop_item', 'custom_product_card_start');
```

## 主题定制

### CSS变量系统

主题使用CSS变量实现主题色切换，无闪烁。

#### 可用CSS变量
```css
:root {
    /* 颜色 */
    --wpforge-color-primary: #2563eb;
    --wpforge-color-secondary: #3b82f6;
    --wpforge-color-accent: #06b6d4;
    --wpforge-color-text: #1e293b;
    --wpforge-color-text-light: #64748b;
    --wpforge-color-background: #ffffff;
    --wpforge-color-background-alt: #f8fafc;
    --wpforge-color-border: #e2e8f0;
    
    /* 字体 */
    --wpforge-font-body: "Inter", system-ui, sans-serif;
    --wpforge-font-heading: "Inter", system-ui, sans-serif;
    --wpforge-font-size-base: 16px;
    --wpforge-line-height-base: 1.6;
    
    /* 布局 */
    --wpforge-container-width: 1200px;
    --wpforge-gutter: 30px;
    
    /* 按钮 */
    --wpforge-button-radius: 6px;
}
```

#### 使用CSS变量
```css
.my-custom-element {
    color: var(--wpforge-color-primary);
    font-family: var(--wpforge-font-body);
    padding: var(--wpforge-gutter);
}
```

### 自定义颜色

通过Customizer或代码修改颜色。

#### 通过Customizer
1. 进入 WordPress 后台 → 外观 → 自定义
2. 点击「全局设置」→「颜色」
3. 修改主色调、辅助色、强调色等
4. 点击「发布」保存

#### 通过代码
```php
// 修改默认颜色
add_filter('wpforge_default_colors', function($colors) {
    $colors['primary'] = '#ff0000';
    return $colors;
});

// 动态修改颜色
add_filter('wpforge_css_variables', function($variables) {
    if (is_page('special')) {
        $variables['--wpforge-color-primary'] = '#ff0000';
    }
    return $variables;
});
```

### 自定义字体

主题支持系统字体、Google Fonts和自定义字体。

#### 系统字体（推荐）
默认使用系统字体栈，零加载时间，性能最佳。

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                 "Helvetica Neue", Arial, sans-serif;
}
```

#### Google Fonts
通过Customizer启用Google Fonts。

```php
// 注册Google Fonts
function wpforge_enqueue_google_fonts() {
    wp_enqueue_style('google-fonts', 
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
        array(), null
    );
}
add_action('wp_enqueue_scripts', 'wpforge_enqueue_google_fonts');
```

#### 自定义字体
上传自定义字体文件并使用。

```php
// 添加上传字体支持
add_filter('upload_mimes', function($mimes) {
    $mimes['woff'] = 'application/font-woff';
    $mimes['woff2'] = 'application/font-woff2';
    $mimes['ttf'] = 'application/font-ttf';
    return $mimes;
});
```

### 自定义布局

#### 布局模式
- **盒装（Boxed）**：内容区域有最大宽度，居中显示
- **全宽（Wide）**：内容区域占满屏幕宽度
- **流体（Fluid）**：完全流体布局

#### 侧边栏位置
- 右侧边栏（默认）
- 左侧边栏
- 无侧边栏

#### 自定义页面模板
```php
/*
Template Name: 自定义模板
Template Post Type: post, page
*/
```

## 钩子系统

主题提供丰富的动作钩子和过滤钩子，方便扩展。

### 动作钩子（Action Hooks）

#### 头部相关
- `wpforge_before_header` - 头部之前
- `wpforge_header` - 头部内容
- `wpforge_after_header` - 头部之后

#### 内容相关
- `wpforge_before_content` - 内容之前
- `wpforge_content` - 内容区域
- `wpforge_after_content` - 内容之后

#### 侧边栏相关
- `wpforge_before_sidebar` - 侧边栏之前
- `wpforge_sidebar` - 侧边栏内容
- `wpforge_after_sidebar` - 侧边栏之后

#### 底部相关
- `wpforge_before_footer` - 底部之前
- `wpforge_footer` - 底部内容
- `wpforge_after_footer` - 底部之后

#### 文章相关
- `wpforge_before_post` - 文章之前
- `wpforge_post` - 文章内容
- `wpforge_after_post` - 文章之后

#### 产品相关
- `wpforge_before_product` - 产品之前
- `wpforge_product` - 产品内容
- `wpforge_after_product` - 产品之后

### 过滤钩子（Filter Hooks）

- `wpforge_css_variables` - CSS变量
- `wpforge_body_classes` - Body类
- `wpforge_post_classes` - 文章类
- `wpforge_breadcrumb_items` - 面包屑项
- `wpforge_related_posts_args` - 相关文章参数
- `wpforge_schema_data` - Schema数据
- `wpforge_seo_title` - SEO标题
- `wpforge_seo_description` - SEO描述
- `wpforge_performance_settings` - 性能设置

### 使用示例

#### 动作钩子示例
```php
// 在头部之后添加内容
add_action('wpforge_after_header', function() {
    echo '<div class="custom-banner">这是自定义横幅</div>';
});

// 在文章内容之后添加相关文章
add_action('wpforge_after_post', function() {
    if (is_single()) {
        get_template_part('template-parts/related-posts');
    }
});
```

#### 过滤钩子示例
```php
// 修改CSS变量
add_filter('wpforge_css_variables', function($variables) {
    $variables['--wpforge-color-primary'] = '#ff0000';
    return $variables;
});

// 修改面包屑
add_filter('wpforge_breadcrumb_items', function($items) {
    $items[] = [
        'title' => '自定义项',
        'url' => '/custom/',
    ];
    return $items;
});

// 修改Schema数据
add_filter('wpforge_schema_data', function($schema) {
    $schema['author'] = [
        '@type' => 'Person',
        'name' => 'Author Name',
    ];
    return $schema;
});
```

## WPForge API集成

主题提供专用REST API端点，WPForge可以完全控制主题。

### API端点列表

#### 主题设置
- `GET /wpforge/v1/theme/settings` - 获取所有主题设置
- `POST /wpforge/v1/theme/settings` - 更新主题设置
- `GET /wpforge/v1/theme/settings/{section}` - 获取某部分设置
- `POST /wpforge/v1/theme/settings/{section}` - 更新某部分设置

#### 配置管理
- `POST /wpforge/v1/theme/reset` - 重置主题设置
- `POST /wpforge/v1/theme/import` - 导入主题配置
- `GET /wpforge/v1/theme/export` - 导出主题配置

#### 预设模板
- `GET /wpforge/v1/theme/presets` - 获取预设模板列表
- `POST /wpforge/v1/theme/preset/{id}/apply` - 应用预设模板

### API认证

使用WordPress REST API标准认证方式：
- Cookie认证（登录用户）
- Application Passwords
- JWT认证（需要插件）

### 使用示例

#### 获取主题设置
```javascript
fetch('/wp-json/wpforge/v1/theme/settings')
    .then(response => response.json())
    .then(data => console.log(data));
```

#### 更新主题设置
```javascript
fetch('/wp-json/wpforge/v1/theme/settings', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': wpApiSettings.nonce
    },
    body: JSON.stringify({
        colors: {
            primary: '#ff0000'
        }
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

#### 导入配置
```javascript
const config = {
    colors: { primary: '#ff0000' },
    typography: { body_font: 'Inter' }
};

fetch('/wp-json/wpforge/v1/theme/import', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-WP-Nonce': wpApiSettings.nonce
    },
    body: JSON.stringify(config)
});
```

#### 应用预设
```javascript
fetch('/wp-json/wpforge/v1/theme/preset/modern_blue/apply', {
    method: 'POST',
    headers: {
        'X-WP-Nonce': wpApiSettings.nonce
    }
});
```

### 配置格式

主题配置使用JSON格式，包含以下部分：

```json
{
    "name": "Theme Name",
    "version": "1.0.0",
    "colors": {
        "primary": "#2563eb",
        "secondary": "#3b82f6",
        "accent": "#06b6d4",
        "text": "#1e293b",
        "background": "#ffffff"
    },
    "typography": {
        "body_font": "Inter, system-ui, sans-serif",
        "heading_font": "Inter, system-ui, sans-serif",
        "base_font_size": "16px",
        "base_line_height": 1.6
    },
    "layout": {
        "container_width": "1200px",
        "layout_style": "boxed",
        "sidebar_position": "right"
    },
    "header": {
        "layout": "default",
        "height": "80px",
        "sticky": true
    },
    "footer": {
        "widget_columns": 4,
        "show_back_to_top": true
    },
    "blog": {
        "archive_layout": "grid",
        "archive_columns": 3
    },
    "woocommerce": {
        "product_columns": 4,
        "product_per_page": 12
    },
    "seo": {
        "auto_title": true,
        "schema_markup": true
    },
    "performance": {
        "css_minify": true,
        "image_lazy_load": true
    },
    "custom_css": "",
    "custom_js": ""
}
```

## 电商漏斗数据面板

主题内置专业的电商漏斗数据分析面板。

### 功能特性
- 10个KPI数据卡片（带环比+迷你趋势图）
- 五层转化漏斗图（访客→浏览→加购→结账→购买）
- 销售趋势图（折线+柱状组合）
- 转化漏斗趋势图（多线折线）
- 热销产品TOP10
- 弃购产品TOP10
- 流量来源分析
- 设备类型分布
- 智能洞察与优化建议
- 时间筛选（今天/昨天/7天/30天/90天/自定义）
- 维度筛选（分类/标签/设备/来源/地域）
- 数据导出（Excel/CSV/PDF/PNG）
- 自动报告（周报/月报）

### 数据采集方式
1. **内置轻量统计脚本**（默认）：<1KB gzip，异步加载
2. **Google Analytics API**：对接GA数据
3. **Matomo/Piwik**：对接Matomo数据

### REST API端点
- `GET /wpforge/v1/funnel/overview` - 获取总览数据
- `GET /wpforge/v1/funnel/sales-trend` - 销售趋势
- `GET /wpforge/v1/funnel/conversion-trend` - 转化趋势
- `GET /wpforge/v1/funnel/top-products` - 热销产品
- `GET /wpforge/v1/funnel/abandoned-products` - 弃购产品
- `GET /wpforge/v1/funnel/traffic-sources` - 流量来源
- `GET /wpforge/v1/funnel/device-types` - 设备类型
- `GET /wpforge/v1/funnel/insights` - 智能洞察
- `POST /wpforge/v1/funnel/export` - 导出数据

### 使用示例
```php
// 获取漏斗数据
$funnel_api = new WPForge_Funnel_REST_API();
$overview = $funnel_api->get_overview_data();

// 添加自定义指标
add_filter('wpforge_funnel_kpi_cards', function($cards) {
    $cards[] = [
        'id' => 'custom_metric',
        'label' => '自定义指标',
        'value' => 1234,
        'change' => 12.5,
    ];
    return $cards;
});
```

## 性能优化

### CSS优化策略

#### 1. CSS变量
使用CSS变量实现主题切换，无需重新加载CSS。

#### 2. 关键CSS内联
自动提取首屏关键CSS，内联到HTML中。

#### 3. 非关键CSS延迟加载
非关键CSS异步加载，不阻塞渲染。

#### 4. CSS合并压缩
自动合并和压缩CSS文件。

### JS优化策略

#### 1. 延迟加载
使用defer属性延迟加载JS。

#### 2. 按需加载
只在需要的页面加载对应的JS。

#### 3. 无jQuery依赖
前端完全不依赖jQuery，减少体积。

### 图片优化策略

#### 1. 懒加载
原生懒加载 + JS懒加载双重保障。

#### 2. WebP格式
自动生成WebP格式，根据浏览器支持返回。

#### 3. 响应式图片
使用srcset和sizes提供合适尺寸的图片。

#### 4. 尺寸属性
自动添加width和height属性，防止CLS。

### 数据库优化

#### 1. 减少查询
使用缓存减少数据库查询。

#### 2. 优化查询
优化SQL查询语句。

#### 3. 瞬态缓存
使用WordPress瞬态API缓存数据。

### 性能测试工具

推荐使用以下工具测试性能：
- Google PageSpeed Insights
- GTmetrix
- WebPageTest
- Lighthouse

## 子主题开发

### 子主题的好处
- 安全更新：主题更新不会丢失自定义
- 版本控制：方便管理自定义代码
- 回滚方便：出问题可以快速回滚

### 创建子主题

#### 1. 创建子主题目录
```
wpforge-child/
├── style.css
├── functions.php
└── screenshot.png
```

#### 2. style.css
```css
/*
Theme Name: WPForge Child
Theme URI: https://wpforge.io/
Description: WPForge子主题
Author: WPForge Team
Author URI: https://wpforge.io/
Template: wpforge-theme
Version: 1.0.0
License: GNU General Public License v3.0
License URI: http://www.gnu.org/licenses/gpl-3.0.html
Text Domain: wpforge-child
*/
```

#### 3. functions.php
```php
<?php
/**
 * WPForge子主题函数
 */

// 加载父主题样式
function wpforge_child_enqueue_styles() {
    wp_enqueue_style('parent-style', 
        get_template_directory_uri() . '/style.css'
    );
}
add_action('wp_enqueue_scripts', 'wpforge_child_enqueue_styles');

// 在这里添加你的自定义代码
```

### 子主题常用定制

#### 自定义模板
复制父主题的模板文件到子主题，进行修改。

```
wpforge-child/
├── single.php        # 自定义文章页
├── page.php          # 自定义页面
├── header.php        # 自定义头部
└── woocommerce/      # 自定义WooCommerce模板
    └── single-product.php
```

#### 自定义函数
在子主题的functions.php中添加自定义功能。

```php
// 添加自定义侧边栏
function wpforge_child_register_sidebars() {
    register_sidebar([
        'name' => '自定义侧边栏',
        'id' => 'custom-sidebar',
        'description' => '自定义侧边栏描述',
        'before_widget' => '<div class="widget">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ]);
}
add_action('widgets_init', 'wpforge_child_register_sidebars');
```

#### 自定义样式
在子主题的style.css或自定义CSS中添加样式。

```css
/* 自定义按钮样式 */
.btn-custom {
    background: var(--wpforge-color-primary);
    color: white;
    padding: 12px 24px;
    border-radius: var(--wpforge-button-radius);
}

/* 自定义文章样式 */
.custom-post {
    margin-bottom: 30px;
    padding: 20px;
    background: var(--wpforge-color-background-alt);
}
```

## 常见问题

### 1. 如何修改主题颜色？
有两种方式：
- 通过WordPress后台 → 外观 → 自定义 → 全局设置 → 颜色
- 通过代码使用wpforge_css_variables过滤器

### 2. 如何禁用懒加载？
```php
add_filter('wpforge_enable_lazy_load', '__return_false');
```

### 3. 如何添加自定义字体？
1. 上传字体文件到主题目录
2. 在functions.php中注册字体
3. 在CSS中使用字体

### 4. 主题支持哪些页面构建器？
- Elementor（推荐，深度集成）
- Bricks Builder（深度集成）
- Gutenberg（原生支持）
- 其他构建器（基本兼容）

### 5. 如何提高PageSpeed分数？
- 启用所有性能优化选项
- 优化图片（压缩、WebP、合适尺寸）
- 使用CDN
- 减少插件数量
- 使用缓存插件

### 6. 主题支持WooCommerce吗？
是的，主题完整支持WooCommerce，包括：
- 产品列表页
- 产品详情页
- 购物车页
- 结算页
- 我的账户页

### 7. 如何更新主题？
- 通过WPForge后台一键更新
- 通过WordPress后台更新
- 手动上传更新（需要FTP）

### 8. 主题更新会丢失自定义吗？
不会，如果你使用子主题的话。建议使用子主题进行自定义，这样主题更新不会影响你的自定义。

### 9. 如何获取技术支持？
- 查看本文档
- 提交Issue到GitHub
- 联系WPForge支持团队

### 10. 主题是免费的吗？
是的，WPForge Theme是完全免费的开源软件，采用GPL v3许可证。

---

## 下一步

- [用户手册](USER_GUIDE.md) - 了解如何使用主题
- [API文档](API.md) - 了解REST API
- [开发指南](DEVELOPMENT.md) - 了解WPForge开发
- [贡献指南](CONTRIBUTING.md) - 参与贡献

---

**最后更新：2026-06-22**
