# WPForge 开发提示词文档

**版本**: v0.8.0-beta
**最后更新**: 2026-06-22
**状态**: 开发中，约80%完成度

---

## 一、项目整体介绍

### 1.1 项目简介

**WPForge** 是一款全智能化的WordPress建站与自动化平台，专为跨境电商和SEO优化设计。通过AI技术实现一键采集、自动翻译、智能定价、批量建站等功能。

**官方定位**：WordPress全自动AI仿站原创软件，开源的全智能化WordPress跨境电商建站AI系统

**许可证**：GNU General Public License v3.0

### 1.2 核心理念

1. **全智能化**：AI决策优先，能自动判断的绝不让用户选
2. **一键完成**：核心流程一键搞定，零配置启动
3. **稳定性**：反检测 > 速度，容错性强，完整测试无bug
4. **扩展性**：插件化架构，支持未来扩展

### 1.3 技术栈

**后端**:
- Python 3.11+
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- Celery (任务队列)
- PostgreSQL 15 (主数据库)
- Redis 7 (缓存 + 消息队列)

**前端**:
- Vue 3
- Pinia (状态管理)
- TypeScript
- Element Plus (UI组件库)

**浏览器自动化**:
- Playwright
- 完整反检测体系（47个模块）

**WordPress生态**:
- WPForge Theme (专属主题)
- Elementor (页面构建器)
- Bricks Builder (页面构建器)
- WooCommerce (电商)

**部署**:
- Docker
- Docker Compose
- Nginx

**中转服务器**:
- Node.js
- Socket.io
- Redis
- SQLite

### 1.4 项目位置

项目根目录：`/home/user/.super_doubao/super-doubao-runtime/workspace/wpforge/`

---

## 二、当前进度状态

### 2.1 整体进度

- **核心功能**: 90% 完成
- **高级功能**: 75% 完成
- **测试覆盖**: 40% 完成
- **文档完善**: 85% 完成
- **整体进度**: 约 80%

### 2.2 已完成的核心模块

#### 第一组：WPForge专属主题（含电商漏斗数据面板）
- ✅ 主题核心框架 + 所有模板文件
- ✅ 10大Customizer设置面板
- ✅ SEO优化模块（内置）
- ✅ 性能优化模块（内置）
- ✅ Elementor + Bricks 深度集成
- ✅ WooCommerce 完整支持
- ✅ 钩子系统（20+动作钩子，10+过滤钩子）
- ✅ WPForge API 集成（REST API + 配置导入导出）
- ✅ 电商漏斗可视化数据面板（8种图表 + AI洞察）

#### 第二组：WPForge本地端主题相关功能
- ✅ 主题配置生成器（8套预设，12种行业）
- ✅ 主题配置管理器
- ✅ 主题一键安装
- ✅ 仿站流程集成
- ✅ 多站点漏斗数据集中管理

#### 第三组：页面构建器深度完善
- ✅ PEDL统一抽象层（50+种Widget类型）
- ✅ Elementor深度支持（数据库直接写入，30+种Widget）
- ✅ Bricks Builder深度支持
- ✅ AI自动设计（6种配色，4种字体，8种风格，10种行业）

#### 第四组：智能采集器增强
- ✅ 可视化点选选择器（框架）
- ✅ 采集功能增强（变体、增量、定时、整站、分页）
- ✅ 与反检测体系深度集成

#### 第五组：全自动SEO模块
- ✅ 页面SEO（标题、描述、Slug、关键词、内链）
- ✅ Schema结构化数据（10+类型）
- ✅ 技术SEO（图片、Canonical、面包屑、Open Graph）
- ✅ 速度优化配置

#### 第六组：搜索引擎自动提交与索引
- ✅ Google Search Console API对接
- ✅ Bing Webmaster Tools对接
- ✅ 收录监控

#### 第七组：WooCommerce深度自动化
- ✅ 产品增强（评论、问答、相关产品、交叉销售）
- ✅ 支付与物流
- ✅ 营销自动化

#### 第八组：前端管理面板完善
- ✅ 仪表盘页面（框架）
- ✅ 一键建站页面（框架）
- ✅ 采集任务页面（框架）
- ✅ 站点管理页面（框架）
- ✅ SEO中心页面（框架）
- ✅ 任务中心页面（框架）
- ✅ 电商漏斗数据页面（框架）
- ✅ 系统设置页面（框架）
- ✅ 插件市场页面（框架）

#### 第九组：AI仿站引擎
- ✅ 整站爬取与分析
- ✅ 内容原创化
- ✅ AI重设计
- ✅ 多源模式

#### 第十组：模拟人工拖拽操作
- ✅ Elementor模拟拖拽（框架）
- ✅ Bricks Builder模拟拖拽（框架）
- ✅ 应用场景

#### 第十一组：多语言完整支持
- ✅ 翻译引擎增强（多引擎支持）
- ✅ 多语言版本管理

#### 第十二组：CRO转化率优化自动化
- ✅ 信任元素
- ✅ 紧迫感元素
- ✅ 转化优化

#### 第十三组：站点监控与告警
- ✅ 监控项（可用性、SSL、域名、磁盘、收录、排名）
- ✅ 告警机制

#### 第十四组：插件化架构完善
- ✅ 核心引擎
- ✅ 插件API
- ✅ 官方插件（框架）

#### 第十五组：完整测试与文档
- ✅ 单元测试（17个测试文件）
- ✅ 文档（14个文档）

### 2.3 反检测体系（行业顶级水平）

**浏览器指纹完全随机化（12大模块）**:
- ✅ Canvas指纹深度伪造
- ✅ WebGL指纹完全伪造
- ✅ AudioContext指纹深度伪造
- ✅ 字体指纹完全随机化
- ✅ Navigator对象全面伪造
- ✅ Screen对象完全伪造
- ✅ 时间与时区指纹
- ✅ 地理位置与IP匹配
- ✅ WebRTC防泄漏与伪造
- ✅ 存储相关指纹
- ✅ 性能与硬件指纹
- ✅ 其他API指纹

**行为指纹真人模拟（7大模块）**:
- ✅ 鼠标移动轨迹模拟（贝塞尔曲线）
- ✅ 点击行为模拟
- ✅ 滚动行为模拟
- ✅ 键盘输入模拟
- ✅ 浏览路径模拟
- ✅ 页面交互模拟
- ✅ WordPress后台操作行为模拟

**网络层反检测（5大模块）**:
- ✅ TLS指纹（JA3/JA3S）伪造
- ✅ HTTP/2指纹
- ✅ 请求头伪造
- ✅ Cookie处理
- ✅ 缓存行为模拟

**动态代理系统增强（4大模块）**:
- ✅ 多供应商支持（BrightData/Oxylabs/Smartproxy等）
- ✅ 代理智能管理（质量检测、健康评分）
- ✅ GEO智能匹配
- ✅ 代理轮换策略

**验证码与反爬绕过（4大模块）**:
- ✅ 多种验证码类型支持
- ✅ 多打码平台对接
- ✅ Cloudflare绕过
- ✅ 其他反爬绕过

### 2.4 中转服务器与双向通信系统

**中转服务端（Node.js + Socket.io + Redis）**:
- ✅ WebSocket服务端：三种客户端类型
- ✅ 连接认证、心跳保活、连接状态管理
- ✅ 消息转发引擎：6种消息类型
- ✅ 离线消息队列：Redis缓存+SQLite持久化
- ✅ 站点管理：注册绑定、分组、标签
- ✅ 认证与安全：三级权限、JWT+API Key

**管理面板（Vue 3 + Element Plus）**:
- ✅ 仪表盘
- ✅ 站点管理
- ✅ 消息中心
- ✅ 系统设置

**WP插件端（PHP WebSocket客户端）**:
- ✅ WebSocket客户端：自动连接、断线重连、心跳保活
- ✅ 事件推送引擎
- ✅ 指令执行引擎
- ✅ 本地缓存与队列

**WPForge本地端（Python WebSocket客户端）**:
- ✅ 站点连接管理
- ✅ 指令下发
- ✅ 事件接收
- ✅ 消息中心

### 2.5 待完善的部分

1. ⚠️ 单元测试覆盖率需要提升（目标>70%）
2. ⚠️ 前端页面需要完善细节（目前是框架）
3. ⚠️ 部分高级功能需要优化
4. ⚠️ 性能优化和bug修复
5. ⚠️ 更多的集成测试
6. ⚠️ 部署脚本（一键安装、升级、数据迁移）
7. ⚠️ 安装向导

---

## 三、项目架构详解

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Frontend)                       │
│  Vue 3 + Pinia + TypeScript + Element Plus                  │
│  仪表盘 / 一键建站 / 采集任务 / 站点管理 / SEO中心 / ...    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ REST API / WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     后端 (Backend)                           │
│  FastAPI + SQLAlchemy + Celery                               │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  AI服务  │  │ 采集服务 │  │ 翻译服务 │  │ 价格引擎 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ WP导入   │  │ SEO服务  │  │ 监控服务 │  │ 插件系统 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           反检测体系 (Stealth System)                 │  │
│  │  浏览器指纹 / 行为模拟 / 代理池 / 验证码处理          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  PostgreSQL   │   │     Redis     │   │   Celery      │
│  (主数据库)   │   │  (缓存/队列)  │   │  (任务队列)   │
└───────────────┘   └───────────────┘   └───────────────┘
        │
        │ 中转通信
        ▼
┌─────────────────────────────────────────────────────────────┐
│              中转服务器 (Relay Server)                       │
│  Node.js + Socket.io + Redis + SQLite                       │
│  消息转发 / 离线队列 / 站点管理 / 认证授权                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              WordPress 站点 (目标站点)                       │
│  WPForge Theme + WPForge Plugin + WooCommerce               │
│  Elementor / Bricks Builder                                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 目录结构详解

```
wpforge/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── main.py                   # FastAPI应用入口
│   │   ├── api/                      # API路由
│   │   │   ├── v1/                   # v1版本API
│   │   │   │   ├── auth.py           # 认证API
│   │   │   │   ├── sites.py          # 站点管理API
│   │   │   │   ├── scraping.py       # 采集API
│   │   │   │   ├── products.py       # 产品API
│   │   │   │   ├── translation.py    # 翻译API
│   │   │   │   ├── seo.py            # SEO API
│   │   │   │   ├── ai.py             # AI API
│   │   │   │   ├── price.py          # 价格API
│   │   │   │   ├── wordpress.py      # WordPress API
│   │   │   │   ├── proxy.py          # 代理API
│   │   │   │   ├── monitoring.py     # 监控API
│   │   │   │   └── tasks.py          # 任务API
│   │   │   └── ...
│   │   ├── core/                     # 核心模块
│   │   │   ├── config.py             # 配置管理
│   │   │   ├── database.py           # 数据库连接
│   │   │   ├── security.py           # 安全相关
│   │   │   ├── hooks.py              # 钩子系统
│   │   │   └── logging.py            # 日志系统
│   │   ├── models/                   # 数据模型
│   │   │   ├── base.py               # 基础模型
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── site.py               # 站点模型
│   │   │   ├── product.py            # 产品模型
│   │   │   ├── task.py               # 任务模型
│   │   │   ├── seo.py                # SEO模型
│   │   │   ├── translation.py        # 翻译模型
│   │   │   └── plugin.py             # 插件模型
│   │   ├── schemas/                  # Pydantic模式
│   │   ├── services/                 # 业务服务
│   │   │   ├── ai_service.py         # AI模型抽象层
│   │   │   ├── ai_orchestrator.py    # AI编排服务
│   │   │   ├── ai_scraper_service.py # AI智能采集识别
│   │   │   ├── ai_seo_service.py     # AI SEO服务
│   │   │   ├── ai_clone_service.py   # AI仿站服务
│   │   │   ├── scraper_service.py    # 产品采集器
│   │   │   ├── translation_service.py # 翻译引擎
│   │   │   ├── price_service.py      # 价格引擎
│   │   │   ├── wordpress_service.py  # WordPress导入
│   │   │   ├── seo_service.py        # SEO服务
│   │   │   ├── seo_enhanced.py       # SEO增强
│   │   │   ├── monitoring_service.py # 监控服务
│   │   │   ├── plugin_system.py      # 插件系统
│   │   │   ├── search_console_service.py # 搜索控制台
│   │   │   ├── woocommerce_automation.py # WooCommerce自动化
│   │   │   ├── theme_config_generator.py # 主题配置生成器
│   │   │   ├── page_builder/         # 页面构建器模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pedl.py           # PEDL统一抽象层
│   │   │   │   ├── elementor_converter.py # Elementor转换器
│   │   │   │   ├── bricks_converter.py    # Bricks转换器
│   │   │   │   └── ai_design.py     # AI自动设计
│   │   │   ├── proxy/                # 代理与反检测模块
│   │   │   │   ├── proxy_pool.py     # 代理池
│   │   │   │   ├── stealth_service.py # 反检测服务
│   │   │   │   ├── fingerprint/      # 浏览器指纹模块
│   │   │   │   │   ├── canvas_fingerprint.py
│   │   │   │   │   ├── webgl_fingerprint.py
│   │   │   │   │   ├── audio_fingerprint.py
│   │   │   │   │   ├── font_fingerprint.py
│   │   │   │   │   ├── navigator_fingerprint.py
│   │   │   │   │   ├── screen_fingerprint.py
│   │   │   │   │   ├── timezone_fingerprint.py
│   │   │   │   │   ├── geolocation_fingerprint.py
│   │   │   │   │   ├── webrtc_fingerprint.py
│   │   │   │   │   ├── storage_fingerprint.py
│   │   │   │   │   ├── performance_fingerprint.py
│   │   │   │   │   ├── sensor_fingerprint.py
│   │   │   │   │   ├── fingerprint_generator.py
│   │   │   │   │   ├── fingerprint_consistency.py
│   │   │   │   │   ├── fingerprint_authenticity.py
│   │   │   │   │   └── fingerprint_diversity.py
│   │   │   │   ├── behavior/         # 行为模拟模块
│   │   │   │   │   ├── mouse_behavior.py
│   │   │   │   │   ├── click_behavior.py
│   │   │   │   │   ├── scroll_behavior.py
│   │   │   │   │   ├── keyboard_behavior.py
│   │   │   │   │   ├── browsing_behavior.py
│   │   │   │   │   ├── interaction_behavior.py
│   │   │   │   │   ├── wordpress_behavior.py
│   │   │   │   │   └── human_behavior.py
│   │   │   │   ├── network/          # 网络层反检测
│   │   │   │   │   ├── tls_fingerprint.py
│   │   │   │   │   ├── http2_fingerprint.py
│   │   │   │   │   ├── request_headers.py
│   │   │   │   │   ├── cookie_handler.py
│   │   │   │   │   └── cache_simulator.py
│   │   │   │   ├── captcha/          # 验证码模块
│   │   │   │   │   ├── captcha_solver.py
│   │   │   │   │   ├── captcha_providers.py
│   │   │   │   │   ├── cloudflare_bypass.py
│   │   │   │   │   └── antibot_bypass.py
│   │   │   │   ├── consistency/      # 指纹一致性
│   │   │   │   ├── verification/     # 检测与验证
│   │   │   │   └── config/           # 配置管理
│   │   │   ├── monitoring/           # 监控模块
│   │   │   ├── scraper/              # 采集器模块
│   │   │   ├── search_console/       # 搜索控制台模块
│   │   │   ├── seo/                  # SEO模块
│   │   │   ├── woocommerce/          # WooCommerce模块
│   │   │   └── relay/                # 中转通信模块
│   │   └── middleware/               # 中间件
│   │       ├── error_handler.py
│   │       ├── rate_limiting.py
│   │       └── request_logging.py
│   ├── tests/                        # 测试
│   │   ├── conftest.py               # 测试配置
│   │   └── unit/                     # 单元测试
│   │       ├── test_utils.py
│   │       ├── test_theme_config_generator.py
│   │       ├── test_page_builder.py
│   │       ├── test_plugin_system.py
│   │       ├── test_stealth.py
│   │       ├── test_seo_service.py
│   │       ├── test_translation_service.py
│   │       ├── test_price_service.py
│   │       ├── test_wordpress_service.py
│   │       ├── test_ai_service.py
│   │       ├── test_scraper_service.py
│   │       ├── test_monitoring_service.py
│   │       ├── test_search_console_service.py
│   │       ├── test_woocommerce_automation.py
│   │       ├── test_api.py
│   │       └── test_database.py
│   ├── pytest.ini                    # pytest配置
│   ├── .coveragerc                   # 覆盖率配置
│   ├── setup.cfg                     # 项目配置
│   └── requirements.txt              # Python依赖
│
├── frontend/                         # 前端项目
│   ├── src/
│   │   ├── views/                    # 页面视图
│   │   │   ├── Dashboard.vue         # 仪表盘
│   │   │   ├── OneClickSite.vue      # 一键建站
│   │   │   ├── ScrapingTasks.vue     # 采集任务
│   │   │   ├── SiteManager.vue       # 站点管理
│   │   │   ├── SEOCenter.vue         # SEO中心
│   │   │   ├── TaskCenter.vue        # 任务中心
│   │   │   ├── FunnelDashboard.vue   # 电商漏斗
│   │   │   ├── Settings.vue          # 系统设置
│   │   │   ├── PluginMarket.vue      # 插件市场
│   │   │   └── Login.vue             # 登录页
│   │   ├── components/               # 组件
│   │   ├── stores/                   # Pinia状态管理
│   │   ├── api/                      # API调用
│   │   ├── router/                   # 路由
│   │   └── ...
│   └── package.json
│
├── wpforge-theme/                    # WPForge专属主题
│   ├── style.css                     # 主题主样式
│   ├── functions.php                 # 主题功能入口
│   ├── index.php                     # 主模板
│   ├── header.php                    # 头部
│   ├── footer.php                    # 底部
│   ├── sidebar.php                   # 侧边栏
│   ├── single.php                    # 文章页
│   ├── page.php                      # 单页面
│   ├── archive.php                   # 归档页
│   ├── category.php                  # 分类页
│   ├── tag.php                       # 标签页
│   ├── search.php                    # 搜索页
│   ├── 404.php                       # 404页面
│   ├── front-page.php                # 首页
│   ├── home.php                      # 博客页
│   ├── inc/                          # 核心功能
│   │   ├── customizer.php            # 自定义设置
│   │   ├── seo.php                   # SEO优化
│   │   ├── performance.php           # 性能优化
│   │   ├── builder-support.php       # 页面构建器支持
│   │   ├── woocommerce.php           # WooCommerce支持
│   │   ├── hooks.php                 # 钩子系统
│   │   ├── wpforge-api.php           # WPForge API集成
│   │   └── funnel-dashboard/         # 电商漏斗数据面板
│   │       ├── class-funnel-dashboard.php
│   │       ├── class-data-collector.php
│   │       ├── class-data-processor.php
│   │       ├── class-insights-engine.php
│   │       ├── class-rest-api.php
│   │       └── admin-page.php
│   ├── assets/                       # 静态资源
│   │   ├── css/
│   │   └── js/
│   └── languages/                    # 多语言
│
├── wpforge-theme-child/              # 子主题模板
│   └── functions.php
│
├── wp-plugin/                        # WPForge中转插件
│   ├── wpforge-relay.php
│   └── includes/
│       ├── class-websocket-client.php
│       ├── class-event-pusher.php
│       ├── class-command-executor.php
│       ├── class-message-queue.php
│       └── class-admin-settings.php
│
├── wordpress-plugin/                 # WordPress插件（旧版）
│   └── ...
│
├── relay-server/                     # 中转服务器
│   ├── package.json
│   ├── src/
│   │   ├── index.js                  # 入口文件
│   │   ├── config/
│   │   ├── utils/
│   │   ├── storage/
│   │   ├── auth/
│   │   ├── server/
│   │   ├── message/
│   │   ├── site/
│   │   └── routes/
│   └── ...
│
├── docs/                             # 文档
│   ├── README.md
│   ├── INSTALL.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPMENT.md
│   ├── API.md
│   ├── CONTRIBUTING.md
│   ├── THEME_DEV.md
│   ├── CHANGELOG.md
│   ├── FAQ.md
│   ├── SECURITY.md
│   └── CODE_OF_CONDUCT.md
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # CI/CD配置
│
├── Dockerfile                        # Docker配置
├── docker-compose.yml                # Docker Compose配置
├── .env.example                      # 环境变量示例
├── .gitignore                        # Git忽略
├── LICENSE                           # GPL v3许可证
├── README.md                         # 项目介绍
├── CHANGELOG.md                      # 更新日志
├── PROGRESS.md                       # 开发进度总结
├── RELEASE_CHECKLIST.md              # 发布清单
└── DEVELOPMENT_PROMPT.md             # 本文档
```

### 3.3 数据库表结构

**主要数据表**:
- `users` - 用户表
- `sites` - 站点表
- `products` - 产品表
- `tasks` - 任务表
- `scraping_tasks` - 采集任务表
- `translations` - 翻译记录表
- `seo_records` - SEO记录表
- `plugins` - 插件表
- `proxies` - 代理表
- `monitoring_records` - 监控记录表
- `search_console_data` - 搜索控制台数据

**数据库连接配置**:
- 配置文件：`backend/app/core/config.py`
- 数据库URL：从环境变量 `DATABASE_URL` 读取
- 默认：`postgresql://wpforge:wpforge@localhost:5432/wpforge`

### 3.4 API接口清单

**认证API**:
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/refresh` - 刷新Token
- `GET /api/v1/auth/me` - 获取当前用户信息

**站点管理API**:
- `GET /api/v1/sites` - 获取站点列表
- `POST /api/v1/sites` - 添加站点
- `GET /api/v1/sites/{id}` - 获取站点详情
- `PUT /api/v1/sites/{id}` - 更新站点
- `DELETE /api/v1/sites/{id}` - 删除站点
- `POST /api/v1/sites/{id}/test` - 测试站点连接
- `POST /api/v1/sites/batch` - 批量操作

**采集API**:
- `GET /api/v1/scraping/tasks` - 获取采集任务列表
- `POST /api/v1/scraping/tasks` - 创建采集任务
- `GET /api/v1/scraping/tasks/{id}` - 获取任务详情
- `POST /api/v1/scraping/tasks/{id}/start` - 开始采集
- `POST /api/v1/scraping/tasks/{id}/stop` - 停止采集
- `GET /api/v1/scraping/tasks/{id}/progress` - 获取采集进度
- `GET /api/v1/scraping/tasks/{id}/results` - 获取采集结果

**产品API**:
- `GET /api/v1/products` - 获取产品列表
- `POST /api/v1/products/import` - 导入产品到WordPress
- `GET /api/v1/products/{id}` - 获取产品详情

**翻译API**:
- `POST /api/v1/translation/translate` - 翻译文本
- `POST /api/v1/translation/batch` - 批量翻译
- `GET /api/v1/translation/engines` - 获取可用翻译引擎

**SEO API**:
- `GET /api/v1/seo/analyze` - 分析页面SEO
- `POST /api/v1/seo/optimize` - 优化页面SEO
- `GET /api/v1/seo/schema` - 获取Schema配置
- `POST /api/v1/seo/schema` - 更新Schema配置

**AI API**:
- `POST /api/v1/ai/generate` - AI生成内容
- `POST /api/v1/ai/clone/analyze` - 分析目标网站
- `POST /api/v1/ai/design` - AI设计页面

**价格API**:
- `POST /api/v1/price/calculate` - 计算价格
- `GET /api/v1/price/rates` - 获取汇率

**WordPress API**:
- `POST /api/v1/wordpress/import/product` - 导入产品
- `POST /api/v1/wordpress/theme/install` - 安装主题
- `POST /api/v1/wordpress/theme/settings` - 设置主题配置
- `GET /api/v1/wordpress/theme/settings` - 获取主题配置

**代理API**:
- `GET /api/v1/proxy/pool` - 获取代理池
- `POST /api/v1/proxy/test` - 测试代理
- `POST /api/v1/proxy/rotate` - 轮换代理

**监控API**:
- `GET /api/v1/monitoring/sites` - 获取站点监控状态
- `GET /api/v1/monitoring/alerts` - 获取告警列表
- `POST /api/v1/monitoring/check` - 执行监控检查

**任务API**:
- `GET /api/v1/tasks` - 获取任务列表
- `GET /api/v1/tasks/{id}` - 获取任务详情
- `POST /api/v1/tasks/{id}/retry` - 重试任务
- `GET /api/v1/tasks/{id}/logs` - 获取任务日志

**主题配置API**:
- `GET /api/v1/theme/config` - 获取主题配置
- `POST /api/v1/theme/config` - 更新主题配置
- `GET /api/v1/theme/presets` - 获取预设列表
- `POST /api/v1/theme/preset/{id}/apply` - 应用预设
- `POST /api/v1/theme/export` - 导出配置
- `POST /api/v1/theme/import` - 导入配置

### 3.5 配置文件说明

**环境变量配置** (`.env`):
```
# 数据库
DATABASE_URL=postgresql://wpforge:wpforge@localhost:5432/wpforge

# Redis
REDIS_URL=redis://localhost:6379/0

# 应用
APP_NAME=WPForge
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key-here

# AI配置
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434

# 代理配置
PROXY_PROVIDER=brightdata
BRIGHTDATA_USER=...
BRIGHTDATA_PASSWORD=...

# 翻译配置
TRANSLATION_PROVIDER=deepl
DEEPL_API_KEY=...
GOOGLE_TRANSLATE_KEY=...

# 中转服务器
RELAY_SERVER_URL=ws://localhost:3000
RELAY_SERVER_SECRET=...

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

**后端配置** (`backend/app/core/config.py`):
- Settings类：所有配置项
- 从环境变量读取
- 有默认值

---

## 四、代码规范

### 4.1 Python规范

**遵循标准**:
- PEP 8 代码风格
- 类型注解（Type Hints）
- Docstring（Google风格）

**命名规范**:
- 类名：PascalCase（大驼峰）
- 函数名：snake_case（下划线）
- 变量名：snake_case
- 常量名：UPPER_SNAKE_CASE
- 私有变量：_前缀

**文件结构**:
- 每个文件开头有文件说明docstring
- 每个类有类docstring
- 每个公共方法有方法docstring
- 复杂逻辑有行内注释

**示例**:
```python
"""
模块说明：这是一个示例模块
功能：演示代码规范
"""

from typing import List, Optional
from pydantic import BaseModel


class ExampleModel(BaseModel):
    """示例数据模型
    
    属性：
        name: 名称
        age: 年龄
    """
    name: str
    age: Optional[int] = None


class ExampleService:
    """示例服务类
    
    提供示例功能
    """
    
    def __init__(self, config: dict):
        """初始化示例服务
        
        参数：
            config: 配置字典
        """
        self.config = config
        self._private_var = "private"
    
    def process_data(self, data: List[str]) -> List[str]:
        """处理数据
        
        参数：
            data: 输入数据列表
            
        返回：
            处理后的数据列表
            
        异常：
            ValueError: 数据为空时抛出
        """
        if not data:
            raise ValueError("数据不能为空")
        
        # 处理逻辑
        result = [item.strip().lower() for item in data]
        return result
```

### 4.2 PHP规范

**遵循标准**:
- WordPress编码规范
- PSR-12 编码风格
- 类型声明（PHP 7.4+）

**命名规范**:
- 类名：PascalCase
- 方法名：snake_case（WordPress风格）
- 函数名：snake_case
- 变量名：snake_case
- 常量名：UPPER_SNAKE_CASE
- 钩子名：wpforge_前缀

**文件结构**:
- 每个文件开头有文件头注释
- 每个类有类docstring
- 每个方法有方法docstring
- 安全：输入验证、输出转义

**示例**:
```php
<?php
/**
 * 示例类文件
 *
 * 功能：演示PHP代码规范
 *
 * @package WPForge
 * @since 1.0.0
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * 示例类
 *
 * 提供示例功能
 *
 * @package WPForge
 * @since 1.0.0
 */
class WPForge_Example {
    
    /**
     * 配置数组
     *
     * @var array
     */
    private $config;
    
    /**
     * 构造函数
     *
     * @param array $config 配置数组
     */
    public function __construct($config = array()) {
        $this->config = wp_parse_args($config, array(
            'default_key' => 'default_value',
        ));
    }
    
    /**
     * 处理数据
     *
     * @param array $data 输入数据
     * @return array 处理后的数据
     * @throws InvalidArgumentException 数据为空时抛出
     */
    public function process_data($data) {
        if (empty($data)) {
            throw new InvalidArgumentException('数据不能为空');
        }
        
        // 安全处理
        $sanitized = array_map('sanitize_text_field', $data);
        
        return $sanitized;
    }
}
```

### 4.3 前端规范

**Vue规范**:
- 组件名：PascalCase
- Props：camelCase声明，kebab-case使用
- 事件名：kebab-case
- 组合式API优先（Composition API）
- TypeScript类型注解

**CSS规范**:
- BEM命名法
- CSS变量优先
- 响应式设计
- 移动端优先

**命名示例**:
```vue
<template>
  <div class="example-component">
    <div class="example-component__header">
      <h2 class="example-component__title">{{ title }}</h2>
    </div>
    <div class="example-component__content">
      <!-- 内容 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  items?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  items: () => []
})

const emit = defineEmits<{
  (e: 'item-click', item: string): void
}>()

const isLoading = ref(false)

const formattedTitle = computed(() => {
  return props.title.toUpperCase()
})

function handleClick(item: string) {
  emit('item-click', item)
}
</script>

<style scoped>
.example-component {
  /* 样式 */
}

.example-component__header {
  /* 样式 */
}

.example-component__title {
  /* 样式 */
}
</style>
```

### 4.4 注释规范

**Python Docstring**（Google风格）:
```python
def function_name(param1, param2):
    """函数简短描述
    
    详细描述函数的功能、用途、注意事项等
    
    参数：
        param1 (类型): 参数1说明
        param2 (类型): 参数2说明
        
    返回：
        返回类型: 返回值说明
        
    异常：
        异常类型: 异常情况说明
        
    示例：
        >>> function_name(val1, val2)
        result
    """
    pass
```

**PHP DocComment**:
```php
/**
 * 函数简短描述
 *
 * 详细描述
 *
 * @since 1.0.0
 * @param string $param1 参数1说明
 * @param int $param2 参数2说明
 * @return array 返回值说明
 * @throws Exception 异常说明
 */
function function_name($param1, $param2) {
    // ...
}
```

---

## 五、待开发任务清单

### 5.1 优先级P0（最高优先级）

#### 任务1：单元测试覆盖率提升到70%+
**目标**: 整体测试覆盖率达到70%以上，核心模块达到85%以上

**要做什么**:
1. 补充现有测试文件的测试用例
2. 为未覆盖的模块添加测试文件
3. 编写集成测试
4. 生成覆盖率报告

**怎么做**:
- 使用pytest + pytest-cov
- Mock外部依赖（API调用、数据库等）
- 每个函数至少3个测试用例（正常/边界/异常）
- 测试数据使用fixture

**验收标准**:
- `pytest --cov=app` 覆盖率 > 70%
- 核心服务模块覆盖率 > 85%
- 所有测试通过，无失败
- 测试报告生成

**入口文件**:
- 测试配置：`backend/tests/conftest.py`
- 现有测试：`backend/tests/unit/`

---

#### 任务2：前端页面完善（从框架到完整实现）
**目标**: 所有前端页面从框架级别完善为完整可用的功能页面

**要做什么**:
1. 仪表盘页面 - 完整的数据展示、图表、快捷操作
2. 一键建站页面 - 完整的向导流程、实时进度、结果预览
3. 采集任务页面 - 任务列表、新建向导、可视化配置、进度显示
4. 站点管理页面 - 站点列表、详情、分组、批量操作
5. SEO中心页面 - SEO评分、优化建议、Schema配置
6. 任务中心页面 - 任务列表、进度、日志、重试
7. 电商漏斗数据页面 - 多站点汇总、对比分析、排名
8. 系统设置页面 - 所有配置项的完整实现
9. 插件市场页面 - 插件列表、详情、安装卸载
10. 登录/注册页面 - 完整的认证流程

**怎么做**:
- 使用Vue 3 + Composition API + TypeScript
- Element Plus UI组件库
- Pinia状态管理
- 响应式设计（桌面/平板/手机）
- 加载状态、空状态、错误状态处理
- 交互动画和反馈

**验收标准**:
- 所有页面可正常访问和使用
- 响应式适配良好
- 加载/空/错误状态都有处理
- 与后端API正确对接
- UI美观、交互流畅

**入口文件**:
- 页面目录：`frontend/src/views/`
- 组件目录：`frontend/src/components/`
- API目录：`frontend/src/api/`
- Store目录：`frontend/src/stores/`

---

#### 任务3：Bug修复与代码审查
**目标**: 修复所有已知bug，进行全面代码审查

**要做什么**:
1. 通读所有核心代码，找出逻辑错误
2. 修复边界条件问题
3. 修复异常处理不完善的地方
4. 检查所有SQL查询，修复N+1查询问题
5. 添加必要的数据库索引
6. 检查所有API端点的参数验证
7. 修复错误响应格式不一致的问题
8. 检查权限控制漏洞
9. 检查并修复竞态条件
10. 优化内存使用

**怎么做**:
- 逐模块代码审查
- 编写测试用例复现bug
- 修复后验证
- 性能测试验证优化效果

**验收标准**:
- 无已知的严重bug
- 边界条件处理正确
- 异常都有妥善处理
- 无明显的N+1查询
- API参数验证完整
- 权限控制正确

**入口文件**:
- 后端服务：`backend/app/services/`
- API路由：`backend/app/api/`
- 数据模型：`backend/app/models/`

---

### 5.2 优先级P1（高优先级）

#### 任务4：集成测试与端到端测试
**目标**: 核心流程的集成测试和端到端测试

**要做什么**:
1. 完整仿站流程测试
2. 产品采集导入全流程测试
3. 多站点批量操作测试
4. 中转通信全链路测试
5. 反检测效果测试

**怎么做**:
- 使用pytest编写集成测试
- 使用Playwright进行端到端测试
- 测试环境隔离
- 测试数据准备和清理

**验收标准**:
- 核心流程端到端测试通过
- 集成测试覆盖主要业务场景
- 测试可重复执行
- 测试报告生成

---

#### 任务5：安全审计
**目标**: 全面的安全审计，确保无重大安全漏洞

**要做什么**:
1. SQL注入扫描
2. XSS漏洞扫描
3. CSRF防护检查
4. 权限控制测试
5. 认证授权测试
6. 敏感信息泄露检查
7. 依赖安全扫描
8. 数据加密检查

**怎么做**:
- 使用安全扫描工具（bandit、safety等）
- 手动代码审查
- 渗透测试
- 依赖漏洞扫描

**验收标准**:
- 无高危安全漏洞
- 中危漏洞有修复计划
- 敏感数据正确加密
- 依赖无已知严重漏洞

---

#### 任务6：部署与发布准备
**目标**: 完善部署脚本和发布流程

**要做什么**:
1. Dockerfile优化（多阶段构建、减小体积）
2. Docker Compose完善（生产环境配置）
3. 一键安装脚本
4. 升级脚本
5. 数据迁移脚本
6. 安装向导
7. 版本号管理
8. 发布包生成
9. 发布说明编写

**怎么做**:
- Docker最佳实践
- Shell脚本编写
- 数据库迁移工具（Alembic）
- 版本号语义化

**验收标准**:
- Docker镜像构建成功
- Docker Compose一键启动
- 安装脚本可正常运行
- 升级脚本可正常升级
- 安装向导流程完整

**入口文件**:
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`

---

### 5.3 优先级P2（中优先级）

#### 任务7：性能优化
**目标**: 后端和前端性能优化

**要做什么**:
1. API响应时间优化（目标：平均 < 100ms）
2. 数据库查询优化
3. 缓存策略优化
4. 批量操作优化
5. 前端首屏加载优化
6. 代码分割
7. 图片懒加载
8. 虚拟列表

**怎么做**:
- 性能分析工具（cProfile、py-spy）
- 数据库查询分析
- 前端性能分析（Lighthouse）
- Redis缓存热点数据

**验收标准**:
- API平均响应时间 < 200ms
- 数据库慢查询 < 1%
- 前端Lighthouse分数 > 90
- 首屏加载时间 < 2s

---

#### 任务8：日志系统完善
**目标**: 完善的日志系统，便于调试和监控

**要做什么**:
1. 日志分级（DEBUG/INFO/WARNING/ERROR/CRITICAL）
2. 日志轮转（按大小/时间）
3. 可配置日志级别和输出
4. 结构化日志（JSON格式）
5. 请求ID追踪
6. 错误日志告警

**怎么做**:
- Python logging模块
- 结构化日志库（structlog）
- 日志轮转（RotatingFileHandler）
- 日志收集（可选：ELK/Loki）

**验收标准**:
- 日志分级清晰
- 日志格式统一
- 错误日志有完整堆栈
- 可通过请求ID追踪完整请求链路

---

### 5.4 优先级P3（低优先级）

#### 任务9：Demo数据与示例
**目标**: 提供演示数据，便于展示和测试

**要做什么**:
1. 示例站点配置（电商/博客/企业）
2. 示例产品数据（20-50个）
3. 示例文章数据（10-20篇）
4. 示例订单数据
5. 示例用户数据
6. 快速开始教程数据

**怎么做**:
- 数据生成脚本
- Faker库生成假数据
- 真实感数据

**验收标准**:
- Demo数据可一键导入
- 数据真实感强
- 覆盖主要功能场景
- 便于演示和测试

---

## 六、开发流程指南

### 6.1 本地运行环境

#### 方式一：Docker Compose（推荐）

**前置要求**:
- Docker 20.10+
- Docker Compose 2.0+

**启动步骤**:
```bash
# 1. 克隆项目
git clone <repository-url>
cd wpforge

# 2. 复制环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的参数

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f backend
```

**服务访问地址**:
- 前端：http://localhost:8080
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs
- 中转服务器：ws://localhost:3000
- PostgreSQL：localhost:5432
- Redis：localhost:6379
- Flower (Celery监控)：http://localhost:5555

**停止服务**:
```bash
docker-compose down

# 停止并删除数据卷（慎用）
docker-compose down -v
```

---

#### 方式二：手动运行

**前置要求**:
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

**后端启动**:
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env

# 初始化数据库
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端启动**:
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**中转服务器启动**:
```bash
cd relay-server

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**启动Celery Worker**:
```bash
cd backend
source venv/bin/activate

celery -A app.celery worker --loglevel=info
```

---

### 6.2 调试指南

#### 后端调试

**使用VS Code调试**:
1. 安装Python扩展
2. 创建 `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

**日志调试**:
- 查看日志输出
- 设置日志级别为DEBUG
- 使用 `print()` 或 `logging.debug()`

**数据库调试**:
- 使用pgAdmin或DBeaver连接数据库
- 查看SQLAlchemy生成的SQL
- 开启SQL日志：`echo=True`

---

#### 前端调试

**使用Vue DevTools**:
- 安装Vue DevTools浏览器扩展
- 可以查看组件树、状态、事件

**使用VS Code调试**:
1. 安装Debugger for Chrome扩展
2. 创建调试配置

**控制台调试**:
- 使用 `console.log()`
- 使用 `debugger` 语句
- Network面板查看API请求

---

### 6.3 测试指南

#### 运行单元测试

```bash
cd backend

# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/unit/test_utils.py

# 运行指定测试函数
pytest tests/unit/test_utils.py::test_function_name

# 显示详细输出
pytest -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行并停止在第一个失败
pytest -x
```

#### 测试覆盖率

```bash
# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html

# 查看报告
open htmlcov/index.html
```

#### 代码质量检查

```bash
# 代码风格检查
flake8 app/

# 类型检查
mypy app/

# 安全检查
bandit -r app/

# 导入排序检查
isort --check-only app/
```

---

### 6.4 代码提交规范

#### Git提交信息格式

使用Conventional Commits规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type类型**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```
feat(theme): add dark mode support

Add dark mode toggle in customizer
Update CSS variables for dark mode
Add system preference detection

Closes #123
```

#### 分支策略

- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: bug修复分支
- `release/*`: 发布分支
- `hotfix/*`: 紧急修复分支

---

## 七、快速上手指南

### 新AI拿到项目后，按以下步骤开始：

#### 第一步：了解项目全貌（30分钟）

1. 阅读本文档（DEVELOPMENT_PROMPT.md）
2. 阅读 README.md 了解项目介绍
3. 阅读 PROGRESS.md 了解开发进度
4. 浏览项目目录结构，熟悉各模块位置
5. 查看 CHANGELOG.md 了解版本历史

#### 第二步：搭建开发环境（1小时）

1. 安装 Docker 和 Docker Compose
2. 复制 `.env.example` 为 `.env`
3. 运行 `docker-compose up -d` 启动所有服务
4. 验证服务是否正常运行
5. 访问 http://localhost:8000/docs 查看API文档

#### 第三步：阅读核心代码（2-4小时）

1. 从 `backend/app/main.py` 开始，了解应用入口
2. 阅读 `backend/app/core/config.py` 了解配置
3. 阅读 `backend/app/models/` 了解数据模型
4. 阅读 `backend/app/services/` 了解核心服务
5. 阅读 `backend/app/api/` 了解API接口
6. 阅读 `wpforge-theme/functions.php` 了解主题入口
7. 阅读 `wpforge-theme/inc/` 了解主题功能模块

#### 第四步：选择任务开始开发

1. 查看第五章「待开发任务清单」
2. 根据优先级选择任务
3. 从P0优先级开始
4. 每个任务完成后进行测试

#### 第五步：开发流程

1. 创建功能分支：`git checkout -b feature/xxx`
2. 编写代码，遵循代码规范
3. 编写单元测试
4. 运行测试确保通过
5. 代码自查
6. 提交代码

---

## 八、常见问题与解决方案

### 8.1 开发环境问题

#### Q: Docker启动失败怎么办？
**A**: 
1. 检查端口是否被占用：`lsof -i :5432` (PostgreSQL)
2. 检查Docker服务是否运行：`docker ps`
3. 查看详细错误日志：`docker-compose logs`
4. 清理旧容器：`docker-compose down -v` 然后重新启动

#### Q: 数据库连接失败怎么办？
**A**:
1. 检查PostgreSQL是否运行：`docker-compose ps db`
2. 检查数据库配置是否正确
3. 检查数据库是否已创建
4. 手动测试连接：`psql -h localhost -U wpforge -d wpforge`

#### Q: 后端启动报错怎么办？
**A**:
1. 查看错误日志：`docker-compose logs backend`
2. 检查依赖是否安装：`pip list`
3. 检查环境变量是否正确配置
4. 检查数据库迁移是否执行：`alembic upgrade head`

---

### 8.2 代码开发问题

#### Q: 找不到某个功能的代码位置？
**A**:
1. 使用全局搜索：`grep -r "关键词" .`
2. 查看第三章「项目架构详解」的目录结构
3. 按模块名查找：服务在 `services/`，API在 `api/`，模型在 `models/`

#### Q: 如何添加新的API接口？
**A**:
1. 在 `backend/app/api/v1/` 下创建或修改路由文件
2. 定义路由函数，添加类型注解
3. 在 `backend/app/api/v1/__init__.py` 中注册路由
4. 编写对应的service层逻辑
5. 添加测试用例

#### Q: 如何添加新的数据库表？
**A**:
1. 在 `backend/app/models/` 下创建模型类
2. 继承 `BaseModel`
3. 定义字段和关系
4. 生成迁移文件：`alembic revision --autogenerate -m "描述"`
5. 执行迁移：`alembic upgrade head`

---

### 8.3 WordPress主题开发问题

#### Q: 如何测试主题功能？
**A**:
1. 搭建本地WordPress环境
2. 将 `wpforge-theme/` 目录复制到 `wp-content/themes/`
3. 在WordPress后台激活主题
4. 测试各功能模块

#### Q: 主题Customizer设置如何添加？
**A**:
1. 编辑 `wpforge-theme/inc/customizer.php`
2. 在 `wpforge_customize_register()` 函数中添加
3. 使用 `$wp_customize->add_section()` 添加面板
4. 使用 `$wp_customize->add_setting()` 添加设置
5. 使用 `$wp_customize->add_control()` 添加控件

#### Q: 如何添加新的钩子？
**A**:
1. 动作钩子：`do_action('wpforge_hook_name', $args)`
2. 过滤钩子：`apply_filters('wpforge_hook_name', $value, $args)`
3. 在 `wpforge-theme/inc/hooks.php` 中注册
4. 在文档中记录钩子说明

---

### 8.4 反检测模块问题

#### Q: 如何使用反检测服务？
**A**:
1. 导入 `StealthService` 类
2. 创建实例：`stealth = StealthService(config)`
3. 生成指纹：`fingerprint = stealth.generate_fingerprint()`
4. 应用到浏览器：`stealth.apply_to_browser(page, fingerprint)`

#### Q: 如何测试反检测效果？
**A**:
1. 使用检测网站：browserleaks.com, fingerprintjs.com, amiunique.org
2. 编写自动化测试脚本
3. 对比指纹特征是否真实
4. 测试Cloudflare等反爬系统

---

### 8.5 测试相关问题

#### Q: 如何Mock外部API调用？
**A**:
1. 使用 `unittest.mock` 或 `pytest-mock`
2. Mock对应的服务类或函数
3. 设置返回值
4. 验证调用参数

示例：
```python
def test_something(mocker):
    # Mock外部API调用
    mock_api = mocker.patch('app.services.external_api.call')
    mock_api.return_value = {'result': 'success'}
    
    # 执行测试
    result = service.do_something()
    
    # 验证
    assert result == 'success'
    mock_api.assert_called_once_with(...)
```

#### Q: 测试数据库如何隔离？
**A**:
1. 使用测试数据库
2. 每个测试用例后回滚事务
3. 使用fixture管理测试数据
4. 参考 `backend/tests/conftest.py`

---

## 九、重要入口文件速查表

### 后端入口
| 功能 | 文件路径 |
|------|----------|
| 应用入口 | `backend/app/main.py` |
| 配置管理 | `backend/app/core/config.py` |
| 数据库连接 | `backend/app/core/database.py` |
| 安全相关 | `backend/app/core/security.py` |
| 钩子系统 | `backend/app/core/hooks.py` |

### 服务层入口
| 功能 | 文件路径 |
|------|----------|
| AI服务 | `backend/app/services/ai_service.py` |
| 采集服务 | `backend/app/services/scraper_service.py` |
| 翻译服务 | `backend/app/services/translation_service.py` |
| 价格引擎 | `backend/app/services/price_service.py` |
| WordPress导入 | `backend/app/services/wordpress_service.py` |
| SEO服务 | `backend/app/services/seo_service.py` |
| 反检测服务 | `backend/app/services/proxy/stealth_service.py` |
| 代理池 | `backend/app/services/proxy/proxy_pool.py` |
| 主题配置生成器 | `backend/app/services/theme_config_generator.py` |
| 页面构建器 | `backend/app/services/page_builder/` |

### API入口
| 功能 | 文件路径 |
|------|----------|
| v1 API路由 | `backend/app/api/v1/__init__.py` |
| 认证API | `backend/app/api/v1/auth.py` |
| 站点API | `backend/app/api/v1/sites.py` |
| 采集API | `backend/app/api/v1/scraping.py` |
| 产品API | `backend/app/api/v1/products.py` |

### 主题入口
| 功能 | 文件路径 |
|------|----------|
| 主题功能入口 | `wpforge-theme/functions.php` |
| 自定义设置 | `wpforge-theme/inc/customizer.php` |
| SEO优化 | `wpforge-theme/inc/seo.php` |
| 性能优化 | `wpforge-theme/inc/performance.php` |
| 钩子系统 | `wpforge-theme/inc/hooks.php` |
| WPForge API | `wpforge-theme/inc/wpforge-api.php` |
| 漏斗数据面板 | `wpforge-theme/inc/funnel-dashboard/` |

### 中转服务器入口
| 功能 | 文件路径 |
|------|----------|
| 服务入口 | `relay-server/src/index.js` |
| Socket服务 | `relay-server/src/server/SocketServer.js` |
| 消息路由 | `relay-server/src/message/MessageRouter.js` |
| 站点管理 | `relay-server/src/site/SiteManager.js` |

### 测试入口
| 功能 | 文件路径 |
|------|----------|
| 测试配置 | `backend/tests/conftest.py` |
| 单元测试目录 | `backend/tests/unit/` |
| pytest配置 | `backend/pytest.ini` |
| 覆盖率配置 | `backend/.coveragerc` |

---

## 十、依赖的第三方库

### Python后端依赖
- `fastapi` - Web框架
- `uvicorn` - ASGI服务器
- `sqlalchemy` - ORM
- `alembic` - 数据库迁移
- `pydantic` - 数据验证
- `python-jose` - JWT认证
- `passlib` - 密码哈希
- `python-multipart` - 文件上传
- `celery` - 任务队列
- `redis` - Redis客户端
- `playwright` - 浏览器自动化
- `requests` - HTTP客户端
- `httpx` - 异步HTTP客户端
- `beautifulsoup4` - HTML解析
- `lxml` - XML/HTML解析
- `pillow` - 图片处理
- `python-dotenv` - 环境变量
- `loguru` - 日志
- `deep-translator` - 翻译
- `money` - 货币处理

### 前端依赖
- `vue` - Vue 3
- `pinia` - 状态管理
- `vue-router` - 路由
- `element-plus` - UI组件库
- `axios` - HTTP客户端
- `echarts` - 图表库
- `dayjs` - 日期处理
- `typescript` - TypeScript
- `vite` - 构建工具

### Node.js中转服务器依赖
- `socket.io` - WebSocket
- `redis` - Redis客户端
- `better-sqlite3` - SQLite
- `jsonwebtoken` - JWT
- `express` - Express框架
- `winston` - 日志

### WordPress主题依赖
- 无外部依赖（纯原生WordPress）
- 可选集成：WooCommerce, Elementor, Bricks Builder

---

## 结语

这是一份完整的WPForge项目开发指南。拿到这份文档，你应该能够：

1. ✅ 了解项目的整体架构和技术栈
2. ✅ 知道当前的开发进度和待完成任务
3. ✅ 找到任何功能对应的代码位置
4. ✅ 按照代码规范进行开发
5. ✅ 搭建本地开发环境
6. ✅ 进行调试和测试
7. ✅ 解决常见的开发问题

**下一步行动建议**:
1. 从P0优先级任务开始
2. 优先提升测试覆盖率
3. 完善前端页面
4. 进行代码审查和bug修复
5. 逐步推进到v1.0正式版

祝你开发顺利！

---

**文档维护者**: WPForge Team
**最后更新**: 2026-06-22
**版本**: v0.8.0-beta
