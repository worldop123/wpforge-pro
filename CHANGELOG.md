# 更新日志

所有重要的WPForge项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [未发布]

### 新增
- WPForge专属主题（WPForge Theme）
  - 极致轻量化设计，CSS < 50KB，JS < 30KB
  - 10大Customizer设置面板
  - 内置SEO优化模块
  - 内置性能优化模块
  - Elementor和Bricks Builder深度集成
  - WooCommerce完整支持
  - 丰富的钩子系统
  - WPForge API集成
  - 电商漏斗可视化数据面板
- 主题配置生成器
  - 8套预设配色方案
  - 12种行业默认配置
  - 自动从网站分析生成主题配置
  - 颜色色相调整功能
  - CSS变量生成
- 浏览器指纹与反检测体系全面升级
  - Canvas指纹深度伪造
  - WebGL指纹完全伪造
  - AudioContext指纹深度伪造
  - 字体指纹完全随机化
  - Navigator对象全面伪造
  - Screen对象完全伪造
  - 时间与时区指纹
  - 地理位置与IP匹配
  - WebRTC防泄漏与伪造
  - 存储相关指纹
  - 性能与硬件指纹
  - 其他API指纹
- 真人行为模拟
  - 鼠标移动轨迹模拟（贝塞尔曲线）
  - 点击行为模拟
  - 滚动行为模拟
  - 键盘输入模拟
  - 浏览路径模拟
  - 页面交互模拟
  - WordPress后台操作行为模拟
- 网络层反检测
  - TLS指纹（JA3/JA3S）伪造
  - HTTP/2指纹
  - 请求头伪造
  - Cookie处理
  - 缓存行为模拟
- 动态代理系统增强
  - 多供应商支持（BrightData/Oxylabs/Smartproxy等）
  - 代理智能管理（质量检测、健康评分）
  - GEO智能匹配
  - 代理轮换策略
- 验证码与反爬绕过
  - 多种验证码类型支持
  - 多打码平台对接
  - Cloudflare绕过
  - 其他反爬绕过
- 中转服务器与双向通信系统
  - Node.js + Socket.io + Redis服务端
  - 三种客户端类型支持
  - 消息转发引擎
  - 离线消息队列
  - 站点管理
  - 认证与安全
  - Vue 3管理面板
  - WP插件端（PHP WebSocket客户端）
  - WPForge本地端（Python WebSocket客户端）
  - Docker Compose一键部署
- 页面构建器深度完善
  - PEDL统一抽象层（页面元素描述语言）
  - Elementor深度支持（数据库直接写入）
  - Bricks Builder深度支持（数据库直接写入）
  - AI自动设计引擎
  - 6种配色方案
  - 4种字体方案
  - 8种设计风格
  - 10种行业推荐设计
- AI仿站引擎
  - 整站爬取与分析
  - 内容原创化（文本改写、图片处理）
  - AI重设计（配色、字体、布局）
  - 多源模式支持
  - 差异化保证
- 插件化架构
  - 钩子系统（Hooks/Filters）
  - 插件管理器
  - 插件信息管理
- 站点监控与告警
  - 可用性监控
  - SSL证书监控
  - 域名到期监控
  - 磁盘空间监控
  - 收录监控
  - 性能监控
  - 智能告警系统
  - 多渠道告警通知
- WooCommerce深度自动化
  - 产品评论AI自动生成
  - 支付网关自动配置
  - 配送区域和运费自动设置
  - 优惠券自动生成
  - 相关产品自动关联
- 全自动SEO模块
  - 页面SEO优化
  - Schema结构化数据（10+类型）
  - 内部链接自动建设
  - 图片SEO优化
  - 速度优化配置
- 搜索引擎自动提交
  - Google Search Console API对接
  - Bing Webmaster Tools对接
  - 收录状态监控
  - 排名追踪

### 改进
- 动态代理系统完善
  - 多供应商适配接口
  - 自动质量检测
  - GEO匹配
  - 自动轮换
- 智能采集器增强
  - 变体采集支持
  - 增量采集
  - 定时采集任务
  - 与反检测体系深度集成
- 智能翻译引擎增强
  - 多引擎支持
  - 术语库
  - 翻译记忆库
  - AI润色
  - SEO翻译优化
- 智能价格引擎
  - AI智能定价
  - 汇率自动转换
  - 价格尾数优化
- WordPress智能导入
  - 三种导入方式自动选择
  - AI字段映射
  - 图片智能处理

### 技术
- 后端：Python 3.11+ + FastAPI + SQLAlchemy + Celery
- 前端：Vue 3 + Pinia + TypeScript + Element Plus
- 数据库：PostgreSQL 15 + Redis 7
- 浏览器自动化：Playwright + stealth
- 部署：Docker + Docker Compose + Nginx
- WordPress生态：Astra主题 + Elementor + Bricks + WooCommerce

---

## [0.9.1-beta] - 2026-06-23

### 新增
- 搜索引擎提交服务完整实现
  - Google Search Console API：站点验证（HTML meta/DNS TXT/HTML文件）、Sitemap提交、URL提交（单个和批量）、收录状态查询、索引覆盖率报告
  - Bing Webmaster API：站点验证、Sitemap提交、URL提交、关键词排名查询
  - 百度站长平台：站点验证、链接提交（普通收录和快速收录）、Sitemap提交、收录量查询
  - 凭证加密存储、速率限制、指数退避重试、异步方法供 Celery 调用
- 站点监控与告警完整实现
  - 8项监控：HTTP状态码、响应时间、SSL证书有效期、域名到期、首页内容变化、关键词排名、外链数量、流量统计
  - 告警渠道：邮件、Webhook（飞书/钉钉/企业微信）、站内消息
  - 告警规则：阈值配置、连续N次失败才告警、告警静默期、告警升级
  - 监控历史记录、趋势图表数据接口
- 插件化架构完整实现
  - 插件安装/卸载/启用/禁用/升级生命周期
  - 插件市场（本地目录扫描、远程仓库拉取）
  - 插件依赖管理（依赖检查、循环检测、拓扑排序）
  - 插件事件系统（事件总线、订阅/发布、优先级、历史记录）
  - 插件配置管理（配置模式注册、校验、配置页面）
  - 2个示例插件：SEO增强插件、安全扫描插件
- 示例数据 Demo
  - CLI 命令 `python -m app.cli load-demo` 加载示例数据
  - 3个示例站点（博客/电商/企业站）、10个示例产品、5个示例采集任务
  - 3个示例用户（admin/editor/viewer）、AI模型配置、代理配置、SEO配置
  - 数据可重复加载（先清理再导入）
- 性能优化
  - 数据库索引优化（Site/Product/Task 模型新增复合索引）
  - SQLAlchemy eager loading（selectinload）减少 N+1 查询
  - 站点统计内存缓存（TTL 30秒）
  - 前端代码分割（vue-vendor/element-plus/utils-vendor 分包）
  - terser 压缩、CSS 代码分割、hash 文件名
- 安全加固
  - CSRF 中间件（Bearer Token 豁免 + auth 端点豁免）
  - 安全头中间件（X-Content-Type-Options/X-Frame-Options/X-XSS-Protection 等）
  - 密码策略强化（长度6-128/非纯数字/非纯字母）
  - 移除 passlib 改用 bcrypt 直调
  - API 限流中间件
- WooCommerce 自动化完善
  - ProductQA 数据类、QAGenerator 类
  - generate_product_reviews、generate_product_qa
  - configure_payment_gateways、setup_marketing_automation、setup_cro_optimization
- AI 仿站引擎完善
  - rewrite_content（4种风格：natural/formal/casual/professional）
  - redesign_style（HSL 色相旋转）
  - ensure_differentiation（Jaccard 相似度）
  - multi_site_fusion（多站融合）

### 修复
- 后端导入错误修复
  - 修复 FastAPI 应用启动时的模块导入错误
  - 修复数据库连接配置（支持 SQLite 开发环境与 PostgreSQL 生产环境）
  - 修复 `app.cli` 模块路径，统一使用 `python -m app.cli create-admin`
  - 修复 `app.commands` 模块引用错误（已迁移至 `app.cli`）
- 前端构建修复
  - 修复 `vue-tsc` 类型检查错误
  - 修复 `vite build` 构建错误
  - 前端构建现已完全通过（`vue-tsc && vite build`）
- Relay Server 修复
  - 修复 Node.js + Socket.io 中转服务器启动问题
  - 确认监听端口 3001 正常工作
  - 修复依赖配置（Node.js 18+）
- Docker 配置修复
  - 统一 `docker-compose.yml` 配置
  - 修复健康检查路径为 `/api/health`（非 `/api/v1/health`）
  - 修复服务端口映射（前端 8080、后端 8000、Flower 5555、Relay 3001）
  - 添加 Docker Compose profiles（nginx、relay、monitoring）
- 数据库初始化修复
  - 移除 Alembic 迁移工具引用（本项目不使用 Alembic）
  - 统一使用 `init_db()`（`Base.metadata.create_all()`）初始化数据库
  - 修复数据库迁移命令文档错误
- 依赖修复
  - 固定 `bcrypt<4.1` 以兼容 `passlib`
  - 修复 Python 3.11+ 依赖兼容性
  - 修复 Node.js 18+ 依赖兼容性
  - 添加 `pytest-asyncio==0.24.0` 并配置 `asyncio_mode = auto`
- 模型修复
  - Site/Product 模型新增 `is_deleted` 软删除字段
  - 修复 `error_handler.py` 中 `settings` 未导入问题
  - 修复 `woocommerce_automation.py:628` 语法错误
  - 修复 `proxy/fingerprint/__init__.py` 漏导出问题
  - 修复 `proxy/captcha/__init__.py` 漏导出 `CaptchaType`

### 改进
- 测试套件大幅扩展
  - 测试数量：967 → 1908 个（+941）
  - 通过率：100%
  - 代码覆盖率：59% → 75.20%
  - 测试框架：pytest + pytest-cov + pytest-asyncio
  - 测试配置：`pytest.ini` 统一配置（asyncio_mode = auto）
- 文档全面修复
  - 修复 `docs/INSTALL.md`：安装命令、端口、API 文档路径、环境要求
  - 修复 `docs/DEVELOPMENT.md`：项目结构、入口文件速查表、测试命令、调试指南
  - 修复 `docs/USER_GUIDE.md`：系统访问地址、API 端点示例、健康检查
  - 重写 `docs/API.md`：列出实际 124 个 API 端点（112 个路径）
  - 修复 `README.md`：克隆地址、技术栈、快速开始、测试状态
  - 修复 `PROGRESS.md`：实际完成度、测试覆盖率、文件统计
- API 文档完善
  - 文档化所有 124 个 API 端点
  - 区分 `/api/v1/*`（v1 接口）与 `/api/api/*`（通用接口）
  - 文档化系统接口（`/api/health`、`/api/docs`、`/api/redoc`）
- 前端页面完善
  - Tasks.vue 重写：6个统计卡、实时进度、日志查看、失败重试、详情对话框、自动刷新
  - Settings.vue 重写：7个Tab（基础设置/AI模型/代理/反检测/中转服务器/用户管理/系统信息）
  - App.vue 增强：用户下拉菜单、新建任务按钮、用户名显示

### 验证
- 后端：FastAPI 正常启动，124 个 API 操作注册成功
- 前端：`vue-tsc && vite build` 构建通过（代码分割 + terser 压缩）
- Relay Server：Node.js 服务正常监听端口 3001
- WP 主题：55 个 PHP 文件语法检查通过
- 测试：1908 个测试 100% 通过，覆盖率 75.20%
- Docker：`docker-compose.yml` 配置统一，健康检查路径 `/api/health`

### 技术栈确认
- 后端：Python 3.11+ / FastAPI 0.115+ / SQLAlchemy 2.0 / Pydantic v2
- 前端：Vue 3.4 / Element Plus 2.5 / Vite 5 / Pinia / TypeScript 5.9
- Relay Server：Node.js 18+ / Socket.io 4.7 / Express 4.18
- 数据库：PostgreSQL 15（生产）/ SQLite（开发）/ Redis 7
- 认证：python-jose + passlib[bcrypt]（bcrypt<4.1）
- 部署：Docker 20.10+ / Docker Compose 2.0+

---

## [0.2.0] - 2026-06-22

### 新增
- 第二阶段功能增强版
- 页面构建器模块（PEDL + Elementor + Bricks）
- 全自动SEO模块
- 搜索引擎提交模块（GSC + Bing）
- WooCommerce深度自动化
- 多站点管理
- 任务队列系统完善
- 前端管理面板完善

### 改进
- 智能采集器增强
- 动态代理系统完善
- 反检测增强

---

## [0.1.0] - 2026-06-22

### 新增
- MVP版本首次发布
- 基础框架（FastAPI + PostgreSQL + Redis）
- AI决策层（智能识别、智能映射、智能策略）
- 智能产品采集器（一键采集、全量字段）
- 动态代理系统（基础版）
- 智能翻译引擎（多引擎支持）
- 智能价格引擎（AI定价、汇率转换）
- WordPress智能导入（REST API + WP-CLI + 浏览器模拟）
- 基础反检测服务
- 站点管理基础功能
- 任务队列基础实现
- 前端基础面板

### 技术
- 后端：Python 3.11 + FastAPI
- 数据库：PostgreSQL 15
- 缓存：Redis 7
- 前端：Vue 3 + Element Plus
- 部署：Docker Compose

---

## 版本说明

### 版本号格式
主版本号.次版本号.修订号

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 版本类型
- **Alpha**：内部测试版，功能不完整
- **Beta**：公开测试版，功能基本完整
- **RC**：候选发布版，即将正式发布
- **Stable**：稳定版，生产环境可用

### 支持的WordPress版本
- WordPress 5.8+
- PHP 7.4+
- WooCommerce 6.0+

### 支持的浏览器
- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

---

## 升级指南

### 从 0.1.x 升级到 0.2.0

1. **备份数据**
   ```bash
   # 备份数据库
   docker-compose exec postgres pg_dump -U wpforge wpforge > backup.sql
   
   # 备份配置
   cp .env .env.backup
   ```

2. **拉取最新代码**
   ```bash
   git pull origin main
   ```

3. **更新环境变量**
   ```bash
   # 对比新的.env.example，添加新的配置项
   diff .env .env.example
   ```

4. **重新构建并启动**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

5. **初始化数据库**
   ```bash
   # 本项目不使用 Alembic，使用 init_db() 初始化
   docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
   ```

6. **验证升级**
   - 访问前端面板检查功能
   - 查看日志确认无错误
   - 测试核心功能

### 注意事项
- 升级前务必备份数据
- 大版本升级建议在测试环境先验证
- 如有自定义插件，需要检查兼容性
- 升级后建议清除浏览器缓存

---

## 路线图

### v1.0.0 - 正式版（计划中）
- [ ] 所有核心功能稳定
- [ ] 完整的测试覆盖
- [ ] 完善的文档
- [ ] 插件市场正式上线
- [ ] 多语言支持完善
- [ ] 性能优化达到最佳

### v1.1.0 - 生态扩展（计划中）
- [ ] 更多页面构建器支持
- [ ] 更多电商平台支持
- [ ] 更多代理供应商
- [ ] 更多AI模型
- [ ] 高级分析功能

### v2.0.0 - 企业版（计划中）
- [ ] 多租户支持
- [ ] 团队协作
- [ ] 高级权限管理
- [ ] SSO集成
- [ ] 企业级支持

---

**最后更新：2026-06-22**
