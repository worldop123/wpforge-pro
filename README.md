# WPForge - 全智能化WordPress跨境电商建站AI系统

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D.svg)](https://vuejs.org/)

> 一键AI驱动的WordPress跨境电商建站解决方案，从产品采集到SEO优化全自动化

## ✨ 核心特性

### 🤖 全智能化
- **AI决策优先**：自动识别网站平台、字段结构、分页、语言、货币
- **智能映射**：自动字段映射、自动判断翻译需求
- **智能策略**：AI定价、AI SEO策略、AI设计策略
- **质量评估**：自动检测数据完整性、翻译质量、SEO评分

### 🚀 一键完成
- 输入URL → AI自动识别配置 → 自动采集 → 自动翻译 → 自动导入
- 零配置启动，核心流程一键搞定
- 支持整站采集、增量采集、定时采集

### 🛡️ 反检测与稳定性
- 浏览器指纹完全随机化
- 真人行为模拟（鼠标/滚动/输入/浏览路径）
- 动态代理系统（BrightData/Oxylabs/Smartproxy等）
- 验证码自动处理
- 智能限速与自动重试

### 🔌 插件化架构
- 模块化设计，支持未来扩展
- 多AI模型抽象层（OpenAI/Anthropic/Gemini/Ollama）
- 多页面构建器支持（Elementor/Bricks）
- 多翻译引擎支持（DeepL/Google/OpenAI等）

## 🏗️ 技术栈

### 后端
- **Python 3.11+** - 主编程语言
- **FastAPI** - 高性能Web框架
- **Celery + Redis** - 异步任务队列
- **PostgreSQL** - 主数据库
- **SQLAlchemy 2.0** - ORM
- **Playwright + stealth** - 浏览器自动化与反检测
- **Pydantic v2** - 数据验证

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - UI组件库
- **Vite** - 下一代前端构建工具
- **Pinia** - 状态管理
- **Vue Router** - 路由管理

### 部署
- **Docker + Docker Compose** - 容器化部署
- **Nginx** - 反向代理
- **Redis** - 缓存与消息队列
- **PostgreSQL** - 数据库

## 📦 核心模块

### 1. AI决策层
- 智能识别引擎
- 字段自动映射
- AI策略生成
- 质量评估系统

### 2. 智能产品采集器
- 一键全量采集
- 动态代理系统
- 完整反检测
- 增量/定时采集

### 3. 智能翻译引擎
- 多引擎支持（DeepL/Google/OpenAI/Anthropic/本地模型）
- 术语库与翻译记忆
- AI润色与SEO优化
- 自动降级与用量统计

### 4. 智能价格引擎
- AI智能定价
- 汇率自动转换
- 价格尾数优化
- 促销价自动生成

### 5. WordPress智能导入
- REST API（优先）> WP-CLI > 浏览器模拟（兜底）
- AI字段映射
- 图片智能处理（压缩、WebP、ALT自动生成）
- 自动建分类与变体

### 6. AI仿站引擎
- 一键整站仿站
- 多源模式（单站复刻、整站迁移、多站融合）
- 内容原创化（文本改写、图片重绘）
- 差异化保证

### 7. 页面构建器智能引擎
- PEDL中间格式统一抽象层
- Elementor深度支持（数据库直接写入 + 模拟人工拖拽）
- Bricks深度支持（数据库直接写入 + 模拟人工拖拽）
- AI自动设计

### 8. 全自动SEO优化
- 页面SEO（标题、描述、Slug、关键词密度）
- 技术SEO（Schema全类型、内链建设、图片SEO）
- 速度优化（缓存、CDN、数据库优化）
- GEO优化与多语言SEO

### 9. 搜索引擎自动提交
- GSC全自动（验证、Sitemap、Indexing API）
- Bing、DuckDuckGo等
- 索引监控与异常告警

### 10. WooCommerce全自动配置
- 产品变体、评论AI生成
- 支付物流网关自动配置
- 营销自动化（优惠券、邮件营销、弃购挽回）
- CRO优化（信任徽章、库存紧迫感、社交证明）

### 11. 站点管理与监控
- 多站点集中管理
- 任务队列与实时进度
- 全自动监控（可用性、SSL、域名、磁盘、收录、排名）
- 智能告警

### 12. 安全与反检测增强
- WordPress操作安全
- 浏览器反检测
- 动态代理与验证码处理

## 🚀 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB RAM
- 至少 20GB 磁盘空间

### 一键启动

```bash
# 克隆项目
git clone https://github.com/wpforge/wpforge.git
cd wpforge

# 复制环境配置
cp .env.example .env

# 启动所有服务
docker-compose up -d

# 访问应用
# 前端: http://localhost:3000
# API文档: http://localhost:8000/api/docs
```

### 默认账号
- 用户名: `admin`
- 密码: `admin123`

## 📖 文档

- [安装指南](docs/installation.md)
- [使用手册](docs/usage.md)
- [API文档](docs/api.md)
- [开发指南](docs/development.md)
- [插件开发](docs/plugins.md)
- [部署指南](docs/deployment.md)

## 🧪 测试

```bash
# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行所有测试并生成覆盖率报告
pytest --cov=app --cov-report=html tests/
```

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 **GNU General Public License v3.0** 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

本软件仅供学习和研究使用。使用本软件进行数据采集时，请遵守目标网站的robots.txt协议和相关法律法规。使用者需对使用本软件产生的一切后果负责。

## 🌟 路线图

- [x] MVP版本：基础框架 + AI识别 + 全自动采集 + 翻译 + 定价 + 导入
- [ ] Elementor + Bricks深度支持
- [ ] 全自动SEO + GSC集成
- [ ] 多站点管理 + 任务队列
- [ ] WooCommerce深度集成
- [ ] AI仿站引擎
- [ ] 完整反检测系统
- [ ] 插件市场
- [ ] 更多编辑器支持
- [ ] 更多平台支持
- [ ] 性能优化

## 📞 联系方式

- 项目主页：[https://github.com/wpforge/wpforge](https://github.com/wpforge/wpforge)
- 问题反馈：[Issues](https://github.com/wpforge/wpforge/issues)
- 讨论区：[Discussions](https://github.com/wpforge/wpforge/discussions)

---

**Made with ❤️ by WPForge Team**
