# 常见问题 (FAQ)

## 目录

- [安装与部署](#安装与部署)
- [功能使用](#功能使用)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [安全相关](#安全相关)
- [开发相关](#开发相关)

---

## 安装与部署

### Q: WPForge的系统要求是什么？

**A:** 
- **操作系统**: Linux (推荐 Ubuntu 22.04+)
- **Python**: 3.11+
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **内存**: 最低 4GB，推荐 8GB+
- **磁盘**: 最低 20GB 可用空间
- **Docker**: 20.10+ (推荐使用Docker部署)

### Q: 如何快速安装WPForge？

**A:** 推荐使用Docker Compose一键安装：

```bash
# 克隆项目
git clone https://github.com/worldop123/wpforge.git
cd wpforge

# 复制配置文件
cp .env.example .env

# 启动服务
docker-compose up -d
```

### Q: 支持哪些操作系统？

**A:** 
- ✅ Linux (Ubuntu, Debian, CentOS等) - 完全支持
- ✅ macOS - 开发环境支持
- ⚠️ Windows - 通过WSL2支持
- ✅ Docker - 跨平台支持

### Q: 如何升级到最新版本？

**A:** 

```bash
# 1. 备份数据
docker-compose exec postgres pg_dump -U wpforge wpforge > backup.sql

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建并启动
docker-compose build
docker-compose up -d

# 4. 初始化数据库（不使用 Alembic）
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
```

### Q: 可以在共享主机上安装吗？

**A:** 不建议。WPForge需要Python、PostgreSQL、Redis等服务，共享主机通常不支持。推荐使用VPS或云服务器。

---

## 功能使用

### Q: WPForge支持哪些WordPress主题？

**A:** 
- ✅ WPForge Theme (官方推荐，深度集成)
- ✅ Astra
- ✅ GeneratePress
- ✅ OceanWP
- ✅ Hello Elementor
- ✅ 大多数符合WordPress标准的主题

### Q: 支持哪些页面构建器？

**A:** 
- ✅ Elementor (深度支持，数据库直接写入)
- ✅ Bricks Builder (深度支持，数据库直接写入)
- ✅ Gutenberg (基础支持)
- 🔄 Beaver Builder (计划中)
- 🔄 Divi (计划中)

### Q: 支持哪些电商平台采集？

**A:** 
- ✅ Shopify
- ✅ WooCommerce
- ✅ Amazon
- ✅ AliExpress
- ✅ eBay
- ✅ 大多数独立站
- 🔄 更多平台持续添加中

### Q: AI功能需要API Key吗？

**A:** 是的，需要配置至少一个AI服务提供商：
- OpenAI (推荐)
- Anthropic
- Google Gemini
- 本地模型 (Ollama)

### Q: 代理服务是必需的吗？

**A:** 
- 基础功能可以不使用代理
- 大规模采集建议使用代理
- 反检测功能需要代理配合
- 支持 BrightData、Oxylabs、Smartproxy 等主流代理服务商

### Q: 支持多语言吗？

**A:** 
- ✅ 系统界面：中文、英文
- ✅ 内容翻译：支持100+语言
- ✅ 多语言站点管理
- 🔄 更多语言界面持续添加

---

## 故障排除

### Q: 启动后无法访问前端？

**A:** 请检查：

1. **端口是否被占用**
   ```bash
   netstat -tlnp | grep 8080
   ```

2. **容器是否正常运行**
   ```bash
   docker-compose ps
   ```

3. **查看日志**
   ```bash
   docker-compose logs frontend
   docker-compose logs backend
   ```

4. **防火墙设置**
   - 确保 8080 端口已开放

### Q: 数据库连接失败？

**A:** 请检查：

1. **PostgreSQL是否启动**
   ```bash
   docker-compose ps postgres
   ```

2. **环境变量配置**
   - 检查 `.env` 文件中的 `DATABASE_URL`
   - 确保用户名、密码、数据库名正确

3. **数据库初始化**
   ```bash
   # 本项目不使用 Alembic，使用 init_db() 初始化
   docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
   ```

### Q: Redis连接失败？

**A:** 请检查：

1. **Redis是否启动**
   ```bash
   docker-compose ps redis
   ```

2. **环境变量配置**
   - 检查 `.env` 文件中的 `REDIS_URL`

3. **测试连接**
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Q: 采集任务失败？

**A:** 常见原因：

1. **网络问题**
   - 检查网络连接
   - 检查代理配置

2. **目标网站反爬**
   - 启用反检测功能
   - 降低采集速度
   - 使用代理IP

3. **选择器失效**
   - 网站结构可能已更新
   - 重新配置选择器

4. **查看任务日志**
   - 在任务中心查看详细错误信息

### Q: WordPress导入失败？

**A:** 请检查：

1. **WordPress站点是否可访问**
   - 确保站点URL正确
   - 确保站点正常运行

2. **REST API是否启用**
   - WordPress 4.7+ 默认启用
   - 检查是否被安全插件禁用

3. **认证信息是否正确**
   - 检查应用密码
   - 检查用户权限

4. **导入方式选择**
   - REST API (优先)
   - WP-CLI (需要SSH访问)
   - 浏览器模拟 (兜底方案)

### Q: AI功能不工作？

**A:** 请检查：

1. **API Key是否配置**
   - 在系统设置 → AI模型配置中检查

2. **API Key是否有效**
   - 测试API连接
   - 检查账户余额

3. **网络是否可访问**
   - 某些API可能需要代理访问

4. **模型是否支持**
   - 确保选择的模型可用

---

## 性能优化

### Q: 如何提升采集速度？

**A:** 

1. **使用代理池**
   - 多IP并行采集
   - 避免单IP限速

2. **调整并发数**
   - 根据服务器配置调整
   - 建议 5-20 并发

3. **启用缓存**
   - 已采集的页面缓存
   - 避免重复采集

4. **选择性采集**
   - 只采集需要的字段
   - 跳过不需要的页面

### Q: 如何优化数据库性能？

**A:** 

1. **索引优化**
   - 确保常用查询字段有索引
   - 定期分析慢查询

2. **连接池**
   - 合理配置数据库连接池
   - 避免连接泄漏

3. **定期清理**
   - 清理过期的任务日志
   - 清理临时数据

4. **读写分离** (高级)
   - 主从复制
   - 读操作走从库

### Q: 如何优化WordPress站点性能？

**A:** 

1. **使用WPForge Theme**
   - 内置性能优化
   - CSS < 50KB, JS < 30KB

2. **启用缓存**
   - 页面缓存
   - 对象缓存 (Redis)

3. **图片优化**
   - 自动WebP转换
   - 懒加载
   - 响应式图片

4. **CDN加速**
   - 静态资源CDN
   - 全球加速

### Q: 服务器配置建议？

**A:** 

| 规模 | CPU | 内存 | 磁盘 | 并发站点 |
|------|-----|------|------|----------|
| 小型 | 2核 | 4GB | 50GB | 10-20 |
| 中型 | 4核 | 8GB | 100GB | 20-50 |
| 大型 | 8核 | 16GB | 200GB | 50-100 |
| 企业 | 16核+ | 32GB+ | 500GB+ | 100+ |

---

## 安全相关

### Q: WPForge安全吗？

**A:** 是的，我们非常重视安全：

- ✅ 密码使用 bcrypt 加密存储
- ✅ API 使用 JWT 认证
- ✅ 支持 HTTPS/TLS 加密
- ✅ 输入验证和输出转义
- ✅ SQL注入防护
- ✅ XSS防护
- ✅ CSRF防护
- ✅ 定期安全审计
- ✅ 依赖安全扫描

### Q: 数据会被泄露吗？

**A:** 

- 所有数据存储在您自己的服务器上
- 我们不会收集或存储您的数据
- API密钥等敏感信息加密存储
- 建议定期备份数据

### Q: 如何保障WordPress站点安全？

**A:** 

1. **使用强密码**
   - 应用密码而非账户密码
   - 定期更换

2. **限制登录尝试**
   - 使用安全插件
   - 防止暴力破解

3. **定期更新**
   - WordPress核心
   - 主题和插件

4. **备份**
   - 定期备份数据库和文件
   - 异地备份

### Q: 支持双因素认证吗？

**A:** 
- 🔄 WPForge管理面板 - 计划中
- ✅ WordPress站点 - 支持 (通过插件)

---

## 开发相关

### Q: 如何参与开发？

**A:** 

1. **Fork项目**
   - Fork到您的GitHub账户

2. **克隆代码**
   ```bash
   git clone https://github.com/your-username/wpforge.git
   cd wpforge
   ```

3. **创建分支**
   ```bash
   git checkout -b feature/your-feature
   ```

4. **提交更改**
   ```bash
   git commit -m "Add your feature"
   ```

5. **提交PR**
   - 提交Pull Request
   - 等待代码审查

详细信息请参考 [CONTRIBUTING.md](CONTRIBUTING.md)

### Q: 如何开发插件？

**A:** 

WPForge支持插件扩展，您可以：

1. 使用插件API扩展功能
2. 添加新的采集源
3. 添加新的翻译引擎
4. 添加新的AI提供商
5. 自定义导入导出格式

详细信息请参考 [PLUGIN_DEV.md](docs/PLUGIN_DEV.md)

### Q: 如何自定义主题？

**A:** 

1. **使用子主题**
   - 安全更新不丢失自定义
   - 推荐方式

2. **使用Customizer**
   - 可视化配置
   - 实时预览

3. **使用WPForge API**
   - 批量配置
   - 自动化配置

详细信息请参考 [THEME_DEV.md](docs/THEME_DEV.md)

### Q: 支持哪些编程语言？

**A:** 
- **后端**: Python 3.11+
- **前端**: Vue 3 + TypeScript
- **WordPress主题**: PHP + CSS + JS
- **数据库**: PostgreSQL
- **缓存**: Redis

### Q: API文档在哪里？

**A:** 
- 在线文档: 访问 `/docs` 端点 (Swagger UI)
- Markdown文档: [API.md](docs/API.md)
- 启动后自动生成交互式文档

---

## 其他

### Q: WPForge是免费的吗？

**A:** 
- ✅ 社区版 - 完全免费，开源 (GPL-3.0)
- 🔄 企业版 - 计划中 (更多功能和支持)

### Q: 有技术支持吗？

**A:** 
- 社区支持: GitHub Issues
- 文档: 完整的使用和开发文档
- 企业支持: 计划中

### Q: 可以商用吗？

**A:** 
- ✅ 可以，GPL-3.0许可证允许商用
- ✅ 可以修改和分发
- ⚠️ 修改后也需要开源 (GPL传染性)
- ⚠️ 不提供担保，使用风险自负

### Q: 如何报告Bug或提交建议？

**A:** 
- GitHub Issues: https://github.com/worldop123/wpforge/issues
- 请详细描述问题和复现步骤
- 建议添加截图和日志

---

**还有其他问题？**
- 查看 [文档](docs/)
- 提交 [Issue](https://github.com/worldop123/wpforge/issues)
- 阅读 [用户指南](USER_GUIDE.md)

---

**最后更新**: 2026-06-22
