# WPForge Theme

**AI-Driven Ultra-Lightweight WordPress Theme**

专为WPForge仿站系统量身定制的高性能SEO主题。

## 特性

### 🚀 极致性能
- **CSS总大小 < 50KB**（gzip后 < 15KB）
- **JS总大小 < 30KB**（gzip后 < 10KB）
- 无jQuery依赖（前端完全不加载jQuery）
- Google PageSpeed Insights：移动端 > 95分，桌面端 > 98分
- Core Web Vitals：全部绿色
- LCP < 1.5s，FID < 100ms，CLS < 0.1

### 🎯 SEO原生优化
- Schema结构化数据（Article、Product、Breadcrumb等）
- 语义化HTML5标签
- 标题优化、Meta描述、关键词
- Canonical URL自动生成
- Open Graph & Twitter Cards
- 面包屑导航
- 图片ALT自动生成

### 🎨 高度可定制
- 10个设置面板（站点身份、全局设置、头部、底部、博客、页面、WooCommerce、SEO、性能、WPForge集成）
- 10种预设配色方案
- CSS变量系统，轻松定制
- WordPress Customizer实时预览

### 🔌 深度集成
- **Elementor** - 原生支持，样式同步
- **Bricks Builder** - 原生支持，样式同步
- **WooCommerce** - 完整模板覆盖
- **WPForge** - REST API集成，配置导入导出

### 📱 响应式设计
- 移动端优先
- 三种断点（1024px、768px、480px）
- 完美适配各种设备

## 安装

### 方法一：WordPress后台安装
1. 登录WordPress后台
2. 进入「外观」→「主题」→「添加新主题」
3. 点击「上传主题」
4. 选择 `wpforge-theme.zip` 文件
5. 点击「立即安装」
6. 安装完成后点击「激活」

### 方法二：FTP安装
1. 将 `wpforge-theme` 文件夹上传到 `/wp-content/themes/` 目录
2. 登录WordPress后台
3. 进入「外观」→「主题」
4. 找到「WPForge Theme」并点击「激活」

## 子主题使用

建议使用子主题进行自定义修改，避免主题更新时丢失修改。

子主题已包含在 `wpforge-theme-child` 文件夹中。

### 子主题安装
1. 将 `wpforge-theme-child` 文件夹上传到 `/wp-content/themes/` 目录
2. 登录WordPress后台
3. 进入「外观」→「主题」
4. 找到「WPForge Theme Child」并点击「激活」

## 页面模板

主题包含以下页面模板：
- **默认模板** - 带侧边栏的标准布局
- **全宽模板** - 无侧边栏，内容全宽
- **Canvas（空白）** - 完全空白，适合页面构建器
- **无头部** - 没有网站头部
- **无底部** - 没有网站底部
- **落地页** - 简洁的落地页布局

## WPForge集成

### REST API端点

主题提供以下REST API端点（需要 `edit_theme_options` 权限）：

#### 获取主题设置
```
GET /wp-json/wpforge/v1/theme/settings
```

#### 更新主题设置
```
POST /wp-json/wpforge/v1/theme/settings
Content-Type: application/json

{
  "settings": {
    "wpforge_primary_color": "#2563eb",
    "wpforge_secondary_color": "#64748b"
  }
}
```

#### 获取预设列表
```
GET /wp-json/wpforge/v1/theme/presets
```

#### 应用预设
```
POST /wp-json/wpforge/v1/theme/preset/{preset_name}
```

#### 导出配置
```
GET /wp-json/wpforge/v1/theme/export
```

#### 导入配置
```
POST /wp-json/wpforge/v1/theme/import
Content-Type: application/json

{
  "config": { ... }
}
```

#### 获取主题信息
```
GET /wp-json/wpforge/v1/theme/info
```

### 预设模板

主题内置10种预设：
- `default` - 默认现代风格
- `modern` - 现代蓝色商务风
- `elegant` - 优雅紫色
- `fresh` - 清新绿色
- `warm` - 温暖橙色
- `dark` - 深色模式
- `minimal` - 极简黑白
- `ecommerce` - 电商优化
- `blog` - 博客风格
- `corporate` - 企业风格

## 性能优化

### CSS优化
- 关键CSS内联
- 非关键CSS延迟加载
- CSS合并与压缩
- CSS变量实现主题色切换

### JavaScript优化
- JS延迟加载（defer）
- 可选禁用jQuery
- 禁用WP Embed脚本

### 图片优化
- 原生图片延迟加载
- 响应式图片（srcset + sizes）
- WebP格式支持
- 图片尺寸自动裁剪

### WordPress优化
- 禁用XML-RPC
- 移除WP版本号
- 禁用表情符号
- 禁用Embeds
- 心跳API频率控制

## 开发

### 目录结构
```
wpforge-theme/
├── style.css              # 主题主样式
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
├── page-templates/        # 页面模板
│   ├── full-width.php
│   ├── canvas.php
│   ├── no-header.php
│   ├── no-footer.php
│   └── landing-page.php
├── inc/                   # 核心功能
│   ├── customizer.php     # 自定义设置
│   ├── seo.php            # SEO优化
│   ├── performance.php    # 性能优化
│   ├── builder-support.php # 页面构建器支持
│   ├── woocommerce.php    # WooCommerce支持
│   ├── hooks.php          # 钩子系统
│   ├── template-tags.php  # 模板标签
│   └── wpforge-api.php    # WPForge API集成
├── assets/
│   ├── css/
│   │   ├── main.css       # 主样式
│   │   └── woocommerce.css # WooCommerce样式
│   └── js/
│       ├── main.js        # 主脚本
│       └── navigation.js  # 导航脚本
└── languages/             # 多语言支持
```

### 钩子系统

#### 动作钩子
- `wpforge_before_header` - 头部之前
- `wpforge_header` - 头部内容
- `wpforge_after_header` - 头部之后
- `wpforge_before_content` - 内容之前
- `wpforge_content` - 内容区域
- `wpforge_after_content` - 内容之后
- `wpforge_before_sidebar` - 侧边栏之前
- `wpforge_sidebar` - 侧边栏内容
- `wpforge_after_sidebar` - 侧边栏之后
- `wpforge_before_footer` - 底部之前
- `wpforge_footer` - 底部内容
- `wpforge_after_footer` - 底部之后

#### 过滤钩子
- `wpforge_css_variables` - CSS变量
- `wpforge_body_classes` - Body类
- `wpforge_schema_data` - Schema数据
- `wpforge_seo_title` - SEO标题
- `wpforge_seo_description` - SEO描述
- `wpforge_theme_presets` - 预设列表

## 系统要求

- WordPress 5.6+
- PHP 7.4+
- MySQL 5.7+ 或 MariaDB 10.3+

## 浏览器兼容性

- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

## 许可证

GNU General Public License v3.0

## 作者

WPForge Team

## 变更日志

### 1.0.0
- 初始版本发布
- 完整的主题核心功能
- SEO优化模块
- 性能优化模块
- Customizer设置系统
- Elementor & Bricks Builder支持
- WooCommerce深度集成
- WPForge REST API集成
- 10种预设配色方案
- 子主题模板
