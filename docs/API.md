# WPForge API 文档

## 目录

- [概述](#概述)
- [认证](#认证)
- [错误处理](#错误处理)
- [分页](#分页)
- [系统接口](#系统接口)
- [v1 API 端点](#v1-api-端点)
  - [认证 API](#认证-api)
  - [站点管理 API](#站点管理-api)
  - [产品管理 API](#产品管理-api)
  - [任务管理 API](#任务管理-api)
  - [采集 API](#采集-api)
  - [翻译 API](#翻译-api)
  - [SEO API](#seo-api)
  - [价格 API](#价格-api)
  - [WordPress API](#wordpress-api)
  - [AI API](#ai-api)
  - [代理 API](#代理-api)
  - [监控 API](#监控-api)
- [通用 API 端点](#通用-api-端点)
  - [通用 AI API](#通用-ai-api)
  - [通用价格 API](#通用价格-api)
  - [通用采集 API](#通用采集-api)
  - [通用 SEO API](#通用-seo-api)
  - [通用翻译 API](#通用翻译-api)
  - [通用 WordPress API](#通用-wordpress-api)
- [示例代码](#示例代码)
- [WebSocket](#websocket)
- [速率限制](#速率限制)

## 概述

WPForge 提供完整的 RESTful API，共 **124 个端点**，分布在 **112 个路径**上，支持所有功能的程序化访问。

### 基础信息

- **API 版本**: v1（主版本）+ 通用接口
- **基础 URL**: `http://localhost:8000`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **API 文档（Swagger）**: `http://localhost:8000/api/docs`
- **API 文档（ReDoc）**: `http://localhost:8000/api/redoc`
- **OpenAPI Schema**: `http://localhost:8000/api/openapi.json`
- **健康检查**: `http://localhost:8000/api/health`

### 路由前缀说明

WPForge 后端使用两种路由前缀：

| 前缀 | 说明 | 示例 |
|------|------|------|
| `/api/v1/*` | v1 版本接口（推荐使用） | `/api/v1/auth/login` |
| `/api/api/*` | 通用接口（带 `/api` 子前缀） | `/api/api/scraping/tasks` |
| `/api/*` | 系统级接口 | `/api/health`、`/api/docs` |

> 注意：通用接口路径中包含双重 `/api/api/`，这是历史路由结构所致。新集成建议优先使用 `/api/v1/*` 接口。

### 请求头

所有请求都应包含以下请求头：

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {access_token}
```

## 认证

WPForge 使用 JWT (JSON Web Token) 进行认证。

### 获取访问令牌

**请求**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

**响应**

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  }
}
```

### 刷新令牌

```http
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer {refresh_token}
```

### 登出

```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

### 获取当前用户信息

```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

## 错误处理

API 使用标准的 HTTP 状态码和统一的错误响应格式。

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "detail": "详细错误信息",
  "errors": {
    "field_name": ["错误说明"]
  }
}
```

### 常见状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或令牌过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

## 分页

列表接口支持分页，使用 `page` 和 `page_size` 参数控制。

### 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | integer | 1 | 页码 |
| page_size | integer | 20 | 每页数量，最大100 |

### 响应格式

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 系统接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/health` | 健康检查 | 否 |

### 健康检查示例

```bash
curl http://localhost:8000/api/health
```

```json
{
  "status": "healthy",
  "version": "0.9.1-beta"
}
```

## v1 API 端点

以下为 `/api/v1/*` 前缀下的接口，是推荐使用的主版本接口。

### 认证 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 | 否 |
| POST | `/api/v1/auth/register` | 用户注册 | 否 |
| POST | `/api/v1/auth/logout` | 用户登出 | 是 |
| POST | `/api/v1/auth/refresh` | 刷新令牌 | 是 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 | 是 |

### 站点管理 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/sites` | 获取站点列表 | 是 |
| POST | `/api/v1/sites` | 创建站点 | 是 |
| GET | `/api/v1/sites/{site_id}` | 获取站点详情 | 是 |
| PUT | `/api/v1/sites/{site_id}` | 更新站点 | 是 |
| DELETE | `/api/v1/sites/{site_id}` | 删除站点 | 是 |
| POST | `/api/v1/sites/{site_id}/test-connection` | 测试站点连接 | 是 |
| GET | `/api/v1/sites/{site_id}/stats` | 获取站点统计 | 是 |

### 产品管理 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/products` | 获取产品列表 | 是 |
| POST | `/api/v1/products` | 创建产品 | 是 |
| GET | `/api/v1/products/{product_id}` | 获取产品详情 | 是 |
| PUT | `/api/v1/products/{product_id}` | 更新产品 | 是 |
| DELETE | `/api/v1/products/{product_id}` | 删除产品 | 是 |
| POST | `/api/v1/products/batch-delete` | 批量删除产品 | 是 |

### 任务管理 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/tasks` | 获取任务列表 | 是 |
| POST | `/api/v1/tasks` | 创建任务 | 是 |
| GET | `/api/v1/tasks/{task_id}` | 获取任务详情 | 是 |
| DELETE | `/api/v1/tasks/{task_id}` | 删除任务 | 是 |
| POST | `/api/v1/tasks/{task_id}/cancel` | 取消任务 | 是 |
| GET | `/api/v1/tasks/{task_id}/logs` | 获取任务日志 | 是 |
| GET | `/api/v1/tasks/stats/summary` | 获取任务统计 | 是 |

### 采集 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/scraping/start` | 开始采集 | 是 |
| POST | `/api/v1/scraping/analyze` | 分析网站结构 | 是 |
| POST | `/api/v1/scraping/quick-scrape` | 快速采集单个产品 | 是 |
| GET | `/api/v1/scraping/status/{task_id}` | 获取采集状态 | 是 |

### 翻译 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/translation/translate` | 翻译文本 | 是 |
| POST | `/api/v1/translation/batch-translate` | 批量翻译 | 是 |
| POST | `/api/v1/translation/polish` | 文本润色 | 是 |
| GET | `/api/v1/translation/engines` | 获取可用翻译引擎 | 是 |
| GET | `/api/v1/translation/languages` | 获取支持的语言 | 是 |
| GET | `/api/v1/translation/terms` | 获取术语库 | 是 |
| POST | `/api/v1/translation/terms` | 添加术语 | 是 |

### SEO API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/seo/audit` | SEO 审计 | 是 |
| POST | `/api/v1/seo/optimize` | SEO 优化 | 是 |
| POST | `/api/v1/seo/generate-title` | 生成 SEO 标题 | 是 |
| POST | `/api/v1/seo/generate-description` | 生成 Meta 描述 | 是 |
| POST | `/api/v1/seo/generate-schema` | 生成 Schema 结构化数据 | 是 |
| GET | `/api/v1/seo/schema-types` | 获取 Schema 类型列表 | 是 |
| GET | `/api/v1/seo/checklist` | 获取 SEO 检查清单 | 是 |

### 价格 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/price/calculate` | 计算价格 | 是 |
| POST | `/api/v1/price/batch-calculate` | 批量计算价格 | 是 |
| POST | `/api/v1/price/optimize` | 优化价格 | 是 |
| POST | `/api/v1/price/suggest` | 价格建议 | 是 |
| GET | `/api/v1/price/exchange-rate` | 获取汇率 | 是 |
| GET | `/api/v1/price/exchange-rates` | 获取多个汇率 | 是 |
| GET | `/api/v1/price/currencies` | 获取支持的货币 | 是 |
| GET | `/api/v1/price/strategies` | 获取定价策略 | 是 |

### WordPress API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/wordpress/import` | 导入到 WordPress | 是 |
| POST | `/api/v1/wordpress/test-connection` | 测试 WordPress 连接 | 是 |
| POST | `/api/v1/wordpress/check-compatibility` | 检查 WordPress 兼容性 | 是 |
| GET | `/api/v1/wordpress/import-methods` | 获取导入方式 | 是 |
| GET | `/api/v1/wordpress/categories` | 获取 WordPress 分类 | 是 |
| GET | `/api/v1/wordpress/products` | 获取 WordPress 产品列表 | 是 |

### AI API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/ai/chat` | AI 对话 | 是 |
| POST | `/api/v1/ai/analyze-site` | AI 分析网站 | 是 |
| POST | `/api/v1/ai/analyze-content` | AI 分析内容 | 是 |
| POST | `/api/v1/ai/generate-content` | AI 生成内容 | 是 |
| POST | `/api/v1/ai/rewrite-content` | AI 改写内容 | 是 |
| GET | `/api/v1/ai/models` | 获取可用 AI 模型 | 是 |
| GET | `/api/v1/ai/providers` | 获取 AI 提供商 | 是 |

### 代理 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/proxy/add` | 添加代理 | 是 |
| POST | `/api/v1/proxy/batch-add` | 批量添加代理 | 是 |
| POST | `/api/v1/proxy/check` | 检测代理可用性 | 是 |
| GET | `/api/v1/proxy/list` | 获取代理列表 | 是 |
| DELETE | `/api/v1/proxy/{proxy_id}` | 移除代理 | 是 |
| GET | `/api/v1/proxy/providers` | 获取代理服务商 | 是 |
| GET | `/api/v1/proxy/pool/stats` | 获取代理池统计 | 是 |
| GET | `/api/v1/proxy/strategies` | 获取代理策略 | 是 |
| GET | `/api/v1/proxy/countries` | 获取支持的国家 | 是 |

### 监控 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/monitoring/overview` | 获取监控概览 | 是 |
| GET | `/api/v1/monitoring/sites/{site_id}/status` | 获取站点监控状态 | 是 |
| GET | `/api/v1/monitoring/sites/{site_id}/ssl` | 获取站点 SSL 状态 | 是 |
| GET | `/api/v1/monitoring/performance/{site_id}` | 获取站点性能数据 | 是 |
| GET | `/api/v1/monitoring/alerts` | 获取告警列表 | 是 |
| GET | `/api/v1/monitoring/settings` | 获取监控设置 | 是 |
| POST | `/api/v1/monitoring/settings` | 更新监控设置 | 是 |
| GET | `/api/v1/monitoring/notification-channels` | 获取通知渠道 | 是 |

## 通用 API 端点

以下为 `/api/api/*` 前缀下的通用接口，提供与 v1 接口类似但路径不同的功能。这些接口由 `app/api/` 目录下的路由模块提供，路径中包含双重 `/api/api/` 前缀。

### 通用 AI API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/api/ai/chat` | AI 对话补全 | 是 |
| GET | `/api/api/ai/config` | 获取 AI 配置 | 是 |
| GET | `/api/api/ai/models` | 获取 AI 模型列表 | 是 |
| GET | `/api/api/ai/providers` | 获取 AI 提供商 | 是 |
| POST | `/api/api/ai/providers` | 添加 AI 提供商 | 是 |
| POST | `/api/api/ai/test` | 测试 AI 连接 | 是 |

### 通用价格 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/api/price/calculate` | 计算价格 | 是 |
| POST | `/api/api/price/product` | 计算产品价格 | 是 |
| POST | `/api/api/price/optimize` | 优化价格 | 是 |
| GET | `/api/api/price/exchange-rate` | 获取汇率 | 是 |
| GET | `/api/api/price/exchange-rates` | 获取多个汇率 | 是 |
| GET | `/api/api/price/currencies` | 获取支持的货币 | 是 |
| GET | `/api/api/price/strategies` | 获取定价策略 | 是 |
| GET | `/api/api/price/cache/stats` | 获取汇率缓存统计 | 是 |
| POST | `/api/api/price/cache/clear` | 清除汇率缓存 | 是 |

### 通用采集 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/api/scraping/tasks` | 创建采集任务 | 是 |
| GET | `/api/api/scraping/tasks/{task_id}` | 获取采集任务 | 是 |
| GET | `/api/api/scraping/tasks/{task_id}/products` | 获取采集的产品 | 是 |
| POST | `/api/api/scraping/selectors/generate` | 生成选择器 | 是 |
| GET | `/api/api/scraping/selectors/presets` | 获取选择器预设 | 是 |
| POST | `/api/api/scraping/proxy/check` | 检测代理 | 是 |
| GET | `/api/api/scraping/proxy/stats` | 获取代理统计 | 是 |

### 通用 SEO API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/api/seo/analyze` | SEO 分析 | 是 |
| POST | `/api/api/seo/optimize/content` | 优化内容 | 是 |
| POST | `/api/api/seo/generate/title` | 生成 SEO 标题 | 是 |
| POST | `/api/api/seo/generate/description` | 生成 Meta 描述 | 是 |
| POST | `/api/api/seo/speed/htaccess` | 生成 .htaccess 规则 | 是 |
| GET | `/api/api/seo/speed/suggestions` | 获取速度优化建议 | 是 |
| GET | `/api/api/seo/checklist` | 获取 SEO 检查清单 | 是 |

### 通用翻译 API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/api/translation/translate` | 翻译文本 | 是 |
| POST | `/api/api/translation/translate/batch` | 批量翻译 | 是 |
| POST | `/api/api/translation/product` | 翻译产品 | 是 |
| GET | `/api/api/translation/engines` | 获取可用引擎 | 是 |
| GET | `/api/api/translation/stats` | 获取翻译统计 | 是 |
| POST | `/api/api/translation/terms` | 添加术语 | 是 |
| POST | `/api/api/translation/terms/batch` | 批量添加术语 | 是 |

### 通用 WordPress API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/api/wordpress/import/tasks` | 创建导入任务 | 是 |
| GET | `/api/api/wordpress/import/tasks/{task_id}` | 获取导入任务 | 是 |
| POST | `/api/api/wordpress/sites/test` | 测试 WordPress 连接 | 是 |
| POST | `/api/api/wordpress/sites/health-check` | WordPress 健康检查 | 是 |
| GET | `/api/api/wordpress/sites/categories` | 获取分类 | 是 |
| POST | `/api/api/wordpress/sites/categories` | 创建分类 | 是 |

## 示例代码

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 登录
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["data"]["access_token"]

# 获取站点列表
def get_sites(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/sites", headers=headers)
    return response.json()["data"]

# 开始采集
def start_scrape(token, url, site_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "url": url,
        "site_id": site_id,
        "max_products": 100,
        "auto_translate": True,
        "auto_import": True
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/scraping/start",
        headers=headers,
        json=data
    )
    return response.json()["data"]

# 使用示例
token = login("admin", "your_password")
sites = get_sites(token)
print(f"共有 {sites['total']} 个站点")
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:8000";

// 登录
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  return data.data.access_token;
}

// 获取站点列表
async function getSites(token) {
  const response = await fetch(`${BASE_URL}/api/v1/sites`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await response.json();
  return data.data;
}

// 使用示例
(async () => {
  const token = await login("admin", "your_password");
  const sites = await getSites(token);
  console.log(`共有 ${sites.total} 个站点`);
})();
```

### cURL 示例

```bash
# 健康检查
curl http://localhost:8000/api/health

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# 获取站点列表
curl -X GET http://localhost:8000/api/v1/sites \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 开始采集
curl -X POST http://localhost:8000/api/v1/scraping/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "url": "https://example.com/products",
    "site_id": 1,
    "max_products": 100,
    "auto_translate": true,
    "auto_import": true
  }'
```

## WebSocket

WPForge 通过 Relay Server（端口 3001）支持 WebSocket 实时推送任务进度。

### 连接

```
ws://localhost:3001
```

### 消息格式

```json
{
  "type": "progress",
  "data": {
    "task_id": "task_123",
    "status": "running",
    "progress": 50,
    "status_message": "正在采集产品...",
    "total_items": 100,
    "processed_items": 50,
    "failed_items": 2
  }
}
```

## 速率限制

API 有速率限制，默认限制为：

- 认证接口：10次/分钟
- 普通接口：100次/分钟
- 采集接口：10次/分钟

超出限制会返回 429 状态码。

## 下一步

- 阅读 [安装指南](INSTALL.md) 了解如何安装系统
- 阅读 [使用手册](USER_GUIDE.md) 了解如何使用系统
- 阅读 [开发指南](DEVELOPMENT.md) 了解如何开发
- 访问 `http://localhost:8000/api/docs` 查看交互式 API 文档
