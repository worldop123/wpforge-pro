# WPForge API 文档

## 目录

- [概述](#概述)
- [认证](#认证)
- [错误处理](#错误处理)
- [分页](#分页)
- [API 端点](#api-端点)
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

## 概述

WPForge 提供完整的 RESTful API，支持所有功能的程序化访问。

### 基础信息

- **API 版本**: v1
- **基础 URL**: `https://your-domain.com/api/v1`
- **数据格式**: JSON
- **字符编码**: UTF-8

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

**请求**

```http
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer {refresh_token}
```

**响应**

```json
{
  "success": true,
  "message": "令牌刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 登出

**请求**

```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**响应**

```json
{
  "success": true,
  "message": "登出成功"
}
```

### 获取当前用户信息

**请求**

```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

**响应**

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "avatar": null,
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
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

## API 端点

### 认证 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/register` | 用户注册 |
| POST | `/auth/logout` | 用户登出 |
| POST | `/auth/refresh` | 刷新令牌 |
| GET | `/auth/me` | 获取当前用户信息 |
| PUT | `/auth/me` | 更新当前用户信息 |
| POST | `/auth/change-password` | 修改密码 |

### 站点管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/sites` | 获取站点列表 |
| POST | `/sites` | 创建站点 |
| GET | `/sites/{id}` | 获取站点详情 |
| PUT | `/sites/{id}` | 更新站点 |
| DELETE | `/sites/{id}` | 删除站点 |
| POST | `/sites/{id}/test-connection` | 测试连接 |
| GET | `/sites/{id}/stats` | 获取站点统计 |
| GET | `/sites/{id}/categories` | 获取产品分类 |

### 产品管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/products` | 获取产品列表 |
| POST | `/products` | 创建产品 |
| GET | `/products/{id}` | 获取产品详情 |
| PUT | `/products/{id}` | 更新产品 |
| DELETE | `/products/{id}` | 删除产品 |
| POST | `/products/batch-delete` | 批量删除产品 |
| GET | `/products/{id}/translations` | 获取产品翻译 |
| POST | `/products/{id}/translate` | 翻译产品 |

### 任务管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tasks` | 获取任务列表 |
| POST | `/tasks` | 创建任务 |
| GET | `/tasks/{id}` | 获取任务详情 |
| DELETE | `/tasks/{id}` | 删除任务 |
| POST | `/tasks/{id}/cancel` | 取消任务 |
| POST | `/tasks/{id}/retry` | 重试任务 |
| GET | `/tasks/{id}/logs` | 获取任务日志 |
| GET | `/tasks/stats` | 获取任务统计 |

### 采集 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/scraping/scrape` | 开始采集 |
| POST | `/scraping/analyze` | 分析网站结构 |
| GET | `/scraping/status/{task_id}` | 获取采集状态 |
| POST | `/scraping/quick-scrape` | 快速采集单个产品 |
| GET | `/scraping/history` | 获取采集历史 |

### 翻译 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/translation/translate` | 翻译文本 |
| POST | `/translation/batch-translate` | 批量翻译 |
| POST | `/translation/translate-products` | 翻译产品 |
| GET | `/translation/engines` | 获取翻译引擎列表 |
| GET | `/translation/languages` | 获取支持的语言 |
| GET | `/translation/terminology` | 获取术语库 |
| POST | `/translation/terminology` | 添加术语 |
| GET | `/translation/history` | 获取翻译历史 |
| GET | `/translation/stats` | 获取翻译统计 |

### SEO API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/seo/audit` | SEO审计 |
| POST | `/seo/optimize` | SEO优化 |
| POST | `/seo/generate-title` | 生成SEO标题 |
| POST | `/seo/generate-description` | 生成Meta描述 |
| GET | `/seo/schema-types` | 获取Schema类型 |
| POST | `/seo/generate-schema` | 生成Schema |
| GET | `/seo/checklist` | 获取SEO检查清单 |

### 价格 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/price/calculate` | 计算价格 |
| GET | `/price/currencies` | 获取支持的货币 |
| GET | `/price/exchange-rate` | 获取汇率 |
| GET | `/price/strategies` | 获取定价策略 |

### WordPress API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/wordpress/import` | 导入到WordPress |
| POST | `/wordpress/test-connection` | 测试连接 |
| GET | `/wordpress/import-methods` | 获取导入方式 |
| POST | `/wordpress/check-compatibility` | 检查兼容性 |
| GET | `/wordpress/categories` | 获取产品分类 |
| GET | `/wordpress/products` | 获取产品列表 |

### AI API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/ai/chat` | AI对话 |
| POST | `/ai/analyze-site` | AI分析网站 |
| GET | `/ai/models` | 获取可用模型 |
| POST | `/ai/generate-content` | AI生成内容 |
| POST | `/ai/rewrite-content` | AI改写内容 |
| POST | `/ai/analyze-content` | AI分析内容 |
| GET | `/ai/providers` | 获取AI提供商 |

### 代理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/proxy/providers` | 获取代理服务商 |
| GET | `/proxy/pool/stats` | 获取代理池统计 |
| POST | `/proxy/add` | 添加代理 |
| POST | `/proxy/batch-add` | 批量添加代理 |
| POST | `/proxy/check` | 检测代理可用性 |
| GET | `/proxy/list` | 获取代理列表 |
| DELETE | `/proxy/{id}` | 移除代理 |
| GET | `/proxy/strategies` | 获取代理策略 |
| GET | `/proxy/countries` | 获取支持的国家 |

### 监控 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/monitoring/overview` | 获取监控概览 |
| GET | `/monitoring/sites/{id}/status` | 获取站点状态 |
| GET | `/monitoring/sites/{id}/ssl` | 获取SSL状态 |
| GET | `/monitoring/alerts` | 获取告警列表 |
| GET | `/monitoring/performance/{id}` | 获取性能数据 |
| GET | `/monitoring/settings` | 获取监控设置 |
| POST | `/monitoring/settings` | 更新监控设置 |
| GET | `/monitoring/notification-channels` | 获取通知渠道 |

## 示例代码

### Python 示例

```python
import requests

BASE_URL = "https://your-domain.com/api/v1"

# 登录
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["data"]["access_token"]

# 获取站点列表
def get_sites(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/sites", headers=headers)
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
        f"{BASE_URL}/scraping/scrape",
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
const BASE_URL = "https://your-domain.com/api/v1";

// 登录
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  return data.data.access_token;
}

// 获取站点列表
async function getSites(token) {
  const response = await fetch(`${BASE_URL}/sites`, {
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
# 登录
curl -X POST https://your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# 获取站点列表
curl -X GET https://your-domain.com/api/v1/sites \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 开始采集
curl -X POST https://your-domain.com/api/v1/scraping/scrape \
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

WPForge 支持 WebSocket 实时推送任务进度。

### 连接

```
wss://your-domain.com/ws/tasks/{task_id}
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
- 阅读 [贡献指南](CONTRIBUTING.md) 了解如何贡献代码
