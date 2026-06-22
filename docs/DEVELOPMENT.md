# WPForge 开发指南

## 目录

- [项目结构](#项目结构)
- [技术栈](#技术栈)
- [开发环境搭建](#开发环境搭建)
- [后端开发](#后端开发)
- [前端开发](#前端开发)
- [数据库](#数据库)
- [插件开发](#插件开发)
- [测试](#测试)
- [代码规范](#代码规范)
- [调试技巧](#调试技巧)

## 项目结构

```
wpforge/
├── backend/                    # 后端代码（FastAPI）
│   ├── app/
│   │   ├── main.py             # FastAPI 应用入口
│   │   ├── celery.py           # Celery 配置
│   │   ├── cli.py              # 命令行工具（create-admin 等）
│   │   ├── api/                # API 路由
│   │   │   ├── __init__.py     # 通用 API 路由聚合（/api 前缀）
│   │   │   ├── v1/             # v1 版本 API（/api/v1 前缀）
│   │   │   │   ├── __init__.py # v1 路由聚合
│   │   │   │   ├── auth.py
│   │   │   │   ├── sites.py
│   │   │   │   ├── products.py
│   │   │   │   ├── tasks.py
│   │   │   │   ├── scraping.py
│   │   │   │   ├── translation.py
│   │   │   │   ├── seo.py
│   │   │   │   ├── price.py
│   │   │   │   ├── wordpress.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── proxy.py
│   │   │   │   └── monitoring.py
│   │   │   ├── scraping.py     # 通用采集 API
│   │   │   ├── wordpress.py    # 通用 WordPress API
│   │   │   ├── translation.py
│   │   │   ├── seo.py
│   │   │   ├── ai.py
│   │   │   └── price.py
│   │   ├── core/               # 核心模块
│   │   │   ├── config.py       # 配置管理（pydantic-settings）
│   │   │   ├── database.py     # 数据库连接、init_db()
│   │   │   ├── security.py     # JWT、密码哈希、get_current_user
│   │   │   ├── hooks.py        # 钩子系统
│   │   │   └── logging.py      # 日志
│   │   ├── middleware/         # 中间件
│   │   │   ├── error_handler.py
│   │   │   ├── rate_limiting.py
│   │   │   └── request_logging.py
│   │   ├── models/             # SQLAlchemy 数据模型（13 张表）
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── services/           # 业务服务
│   │   │   ├── ai_service.py
│   │   │   ├── scraper_service.py
│   │   │   ├── translation_service.py
│   │   │   ├── price_service.py
│   │   │   ├── wordpress_service.py
│   │   │   ├── seo_service.py
│   │   │   ├── proxy_service.py
│   │   │   ├── monitoring_service.py
│   │   │   ├── plugin_system.py
│   │   │   ├── theme_config_generator.py
│   │   │   ├── woocommerce_automation.py
│   │   │   ├── page_builder/   # PEDL + Elementor + Bricks
│   │   │   ├── proxy/          # 反检测体系（fingerprint/behavior/network/captcha/...）
│   │   │   ├── relay/          # 中转通信客户端
│   │   │   ├── scraper/
│   │   │   ├── seo/
│   │   │   ├── monitoring/
│   │   │   ├── search_console/
│   │   │   └── woocommerce/
│   │   ├── tasks/              # Celery 异步任务
│   │   ├── utils/              # 工具函数
│   │   └── plugins/            # 插件目录
│   ├── tests/                  # 测试代码
│   │   ├── conftest.py         # pytest 配置和 fixture
│   │   └── unit/               # 单元测试（21 个测试文件）
│   ├── pytest.ini              # pytest 配置
│   ├── .coveragerc             # 覆盖率配置
│   ├── setup.cfg
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端代码（Vue 3 + TypeScript）
│   ├── src/
│   │   ├── api/                # API 调用封装
│   │   ├── views/              # 页面视图
│   │   ├── store/              # Pinia 状态管理
│   │   ├── router/             # 路由配置
│   │   ├── types/              # TypeScript 类型
│   │   ├── assets/             # 静态资源
│   │   ├── App.vue
│   │   ├── main.ts             # 应用入口
│   │   └── env.d.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── relay-server/               # 中转服务器（Node.js + Socket.io）
│   ├── src/
│   │   ├── index.js            # 入口
│   │   ├── config/
│   │   ├── server/             # SocketServer、ClientManager
│   │   ├── message/            # 消息队列、路由
│   │   ├── site/               # 站点管理
│   │   ├── auth/               # 认证
│   │   ├── storage/            # Redis + SQLite
│   │   ├── routes/             # REST API
│   │   └── utils/
│   └── package.json
├── relay-admin/                # 中转服务器管理面板（Vue 3）
├── wpforge-theme/              # WPForge 专属 WordPress 主题（39 个 PHP 文件）
├── wpforge-theme-child/        # 子主题
├── wp-plugin/                  # WPForge 中转 WordPress 插件
├── wordpress-plugin/           # 旧版 WordPress 插件
├── docker/                     # Docker 配置（Dockerfile、nginx）
├── docs/                       # 文档
├── docker-compose.yml          # Docker Compose 统一入口
├── .env.example                # 环境变量示例
├── README.md
├── CHANGELOG.md
├── PROGRESS.md
└── LICENSE
```

## 技术栈

### 后端技术栈

- **编程语言**: Python 3.11+
- **Web 框架**: FastAPI 0.115
- **任务队列**: Celery 5.4 + Redis 7
- **主数据库**: PostgreSQL 15（生产）/ SQLite（开发测试）
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic v2 / pydantic-settings
- **认证**: python-jose (JWT) + passlib[bcrypt]（要求 `bcrypt<4.1`）
- **浏览器自动化**: Playwright + playwright-stealth
- **HTTP 客户端**: httpx（异步）/ requests
- **HTML 解析**: BeautifulSoup4 + lxml

> 注意：项目不使用 Alembic 做数据库迁移，表结构通过 `app.core.database.init_db()` 创建。

### 前端技术栈

- **框架**: Vue 3.4
- **UI 组件库**: Element Plus 2.5
- **状态管理**: Pinia 2.1
- **构建工具**: Vite 5
- **路由**: Vue Router 4.2
- **语言**: TypeScript 5.9（构建时 `vue-tsc` 类型检查）
- **图表**: ECharts 5.4
- **HTTP**: axios

### 中转服务器技术栈

- **运行时**: Node.js 18+（推荐 20+）
- **WebSocket**: Socket.io 4.7
- **存储**: Redis 4.6 + better-sqlite3 11.7
- **认证**: jsonwebtoken + bcryptjs
- **HTTP**: Express 4.18

### 部署技术栈

- **容器化**: Docker 20.10+
- **容器编排**: Docker Compose 2.0+
- **反向代理**: Nginx（可选 profile）

## 开发环境搭建

### 1. 克隆项目

```bash
git clone https://github.com/worldop123/wpforge.git
cd wpforge
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库、Redis、AI API 等信息。开发环境可使用 SQLite：

```
DATABASE_URL=sqlite:///./wpforge.db
```

### 3. 启动依赖服务

使用 Docker 启动 PostgreSQL 和 Redis（推荐）：

```bash
docker-compose up -d postgres redis
```

或者手动安装 PostgreSQL 和 Redis。

### 4. 后端开发环境

```bash
cd backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 初始化数据库（不使用 Alembic）
python -c "from app.core.database import init_db; init_db()"

# 创建管理员
python -m app.cli create-admin --username admin --password admin123 --email admin@example.com

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- API 文档 (Swagger): http://localhost:8000/api/docs
- API 文档 (ReDoc): http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/api/health

### 5. 前端开发环境

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 类型检查 + 构建
npm run build
```

### 6. 启动 Celery Worker（可选）

```bash
cd backend
source venv/bin/activate

# 启动 Worker
celery -A app.tasks worker --loglevel=info --concurrency=2

# 启动 Beat (定时任务)
celery -A app.tasks beat --loglevel=info
```

### 7. 启动中转服务器（可选）

```bash
cd relay-server
npm install
npm run dev
# 默认监听 3001 端口
```

## 后端开发

### 添加新的 API 端点

1. 在 `app/api/v1/` 下创建或编辑路由文件

```python
# app/api/v1/example.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas import SuccessResponse

router = APIRouter(prefix="/examples", tags=["示例"])


@router.get("", response_model=SuccessResponse)
async def list_examples(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取示例列表"""
    return SuccessResponse(message="获取成功", data={"items": []})
```

2. 在 `app/api/v1/__init__.py` 中注册路由

```python
from app.api.v1.example import router as example_router
api_v1_router.include_router(example_router)
```

### 添加新的数据库模型

1. 在 `app/models/` 下创建模型文件

```python
# app/models/example.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Example(BaseModel):
    __tablename__ = "examples"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
```

2. 在 `app/models/__init__.py` 中导出模型

```python
from app.models.example import Example

__all__ = [
    # ... 现有模型
    "Example",
]
```

3. 在 `app/core/database.py` 的 `init_db()` 中导入新模型，然后执行：

```bash
python -c "from app.core.database import init_db; init_db()"
```

> WPForge 不使用 Alembic 迁移工具，新增表通过 `Base.metadata.create_all()` 创建。

### 添加新的服务

在 `app/services/` 下创建服务文件，参考现有服务（如 `price_service.py`、`translation_service.py`）的实现模式。

### 添加 Celery 任务

在 `app/tasks/` 下创建任务文件，参考 `scraping_tasks.py`、`import_tasks.py` 等。

## 前端开发

### 添加新页面

1. 在 `frontend/src/views/` 下创建页面组件（`.vue` 文件）
2. 在 `frontend/src/router/index.ts` 中添加路由
3. 在 `frontend/src/api/` 下添加对应的 API 调用

### 添加 API 封装

在 `frontend/src/api/` 下创建 API 文件，使用 axios 封装请求。参考现有 `sites.ts`、`products.ts` 等。

## 数据库

### 数据表清单

WPForge 共有 13 张数据表（定义在 `app/models/`）：

| 模型 | 表名 | 说明 |
|------|------|------|
| `User` | `users` | 用户 |
| `Site` | `sites` | 站点 |
| `Task` | `tasks` | 任务 |
| `TaskLog` | `task_logs` | 任务日志 |
| `Product` | `products` | 产品 |
| `ProductCategory` | `product_categories` | 产品分类 |
| `Translation` | `translations` | 翻译记录 |
| `TranslationTerm` | `translation_terms` | 翻译术语 |
| `SEOAudit` | `seo_audits` | SEO 审计 |
| `SEOSetting` | `seo_settings` | SEO 设置 |
| `GSCProperty` | `gsc_properties` | GSC 属性 |
| `Plugin` | `plugins` | 插件 |
| `PluginSetting` | `plugin_settings` | 插件设置 |

### 数据库初始化

```python
from app.core.database import init_db
init_db()  # 创建所有表
```

### 数据库连接配置

- 配置文件：`backend/app/core/config.py`
- 数据库 URL：从环境变量 `DATABASE_URL` 读取
- 默认（Docker）：`postgresql+psycopg2://wpforge:wpforge@postgres:5432/wpforge`
- 开发测试：`sqlite:///./wpforge.db`

## 插件开发

WPForge 支持插件扩展，可以通过插件添加新功能。

### 插件结构

```
plugins/
└── my_plugin/
    ├── __init__.py
    ├── plugin.json
    ├── routes.py
    ├── services.py
    └── templates/
```

### 钩子系统

WPForge 使用钩子系统实现插件扩展：

```python
from app.core.hooks import add_action, add_filter

# 动作钩子
def my_custom_action(data):
    pass

add_action('after_product_import', my_custom_action)

# 过滤器钩子
def my_custom_filter(content):
    return modified_content

add_filter('product_description', my_custom_filter)
```

详见 `app/core/hooks.py` 和 `app/services/plugin_system.py`。

## 测试

### 运行测试

测试位于 `backend/tests/` 目录，使用 pytest 框架。

```bash
cd backend

# 运行所有测试
pytest tests/

# 运行单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_utils.py

# 运行特定测试函数
pytest tests/unit/test_utils.py::test_function_name

# 显示详细输出
pytest -v

# 运行并停止在第一个失败
pytest -x

# 运行带标记的测试
pytest -m unit
pytest -m "not slow"
```

### 覆盖率报告

```bash
# 生成覆盖率报告（终端 + HTML + XML）
pytest --cov=app --cov-report=html

# 仅生成 HTML 报告
pytest --cov=app --cov-report=html tests/

# 查看报告
# 在浏览器打开 backend/htmlcov/index.html
```

> 当前测试状态：967 个测试 100% 通过，覆盖率 59%。

### 测试配置

- `backend/pytest.ini`：pytest 配置（已默认开启 `--cov=app` 和 HTML 报告）
- `backend/.coveragerc`：覆盖率配置
- `backend/tests/conftest.py`：测试 fixture

### 编写测试

参考 `backend/tests/unit/` 下现有测试文件，使用 pytest fixture 和 mock。

```python
# tests/unit/test_example.py
import pytest
from unittest.mock import Mock

def test_something():
    """测试示例"""
    assert 1 + 1 == 2


def test_with_mock(mocker):
    """使用 mock 的测试"""
    mock_func = mocker.patch('some.module.function')
    mock_func.return_value = 'mocked'
    # ...
```

## 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 使用类型注解（Type Hints）
- 文档字符串使用 Google 风格
- 代码格式化使用 black
- 导入排序使用 isort

### 前端代码规范

- 遵循 Vue 3 风格指南
- 使用 TypeScript（构建时 `vue-tsc` 类型检查）
- 组件命名使用 PascalCase
- 组合式 API（Composition API）优先

### PHP 代码规范（WordPress 主题/插件）

- 遵循 WordPress 编码规范
- 类名 PascalCase，函数名 snake_case
- 钩子名 `wpforge_` 前缀

## 调试技巧

### 后端调试

#### 1. 使用日志

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

def my_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

通过环境变量 `LOG_LEVEL=DEBUG` 开启调试日志。

#### 2. 使用 VS Code 调试器

创建 `.vscode/launch.json`：

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
        "PYTHONPATH": "${workspaceFolder}/backend",
        "DATABASE_URL": "sqlite:///./wpforge.db"
      },
      "justMyCode": true
    }
  ]
}
```

#### 3. 查看 SQL 查询

在 `.env` 中设置 `DEBUG=true`，SQLAlchemy 会输出所有 SQL 语句（`echo=True`）。

或者在代码中临时开启：

```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

#### 4. 使用 pdb / breakpoint

```python
def my_function():
    breakpoint()  # Python 3.7+ 内置
    # 或 import pdb; pdb.set_trace()
    # ...
```

#### 5. 交互式 Shell

```bash
cd backend
python -c "
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(u.id, u.username, u.email)
db.close()
"
```

### 前端调试

#### 1. 使用 Vue DevTools

安装 Vue.js DevTools 浏览器扩展，查看组件树、Pinia 状态、路由等。

#### 2. 使用 console

```typescript
console.log('Message')
console.warn('Warning')
console.error('Error')
console.table(data)
```

#### 3. 网络请求调试

在浏览器开发者工具的 Network 面板中查看 API 请求和响应。

#### 4. 类型检查

```bash
cd frontend
npx vue-tsc --noEmit  # 仅类型检查，不构建
```

### API 调试

使用 Swagger UI 调试 API：

- 访问 `http://localhost:8000/api/docs`
- 直接在界面上测试每个 API
- 或使用 Postman、curl、httpie 等工具

```bash
# 健康检查
curl http://localhost:8000/api/health

# 登录获取 token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 使用 token 访问受保护接口
curl http://localhost:8000/api/v1/sites \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Docker 调试

```bash
# 查看后端日志
docker-compose logs -f backend

# 进入后端容器
docker-compose exec backend bash

# 在容器内执行 Python
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"

# 查看数据库
docker-compose exec postgres psql -U wpforge -d wpforge
```

## 重要入口文件速查表

### 后端入口

| 功能 | 文件路径 |
|------|----------|
| 应用入口 | `backend/app/main.py` |
| 配置管理 | `backend/app/core/config.py` |
| 数据库连接 | `backend/app/core/database.py` |
| 安全相关 | `backend/app/core/security.py` |
| 钩子系统 | `backend/app/core/hooks.py` |
| 日志系统 | `backend/app/core/logging.py` |
| 命令行工具 | `backend/app/cli.py` |
| Celery 配置 | `backend/app/celery.py` |

### API 路由入口

| 功能 | 文件路径 |
|------|----------|
| 通用 API 路由聚合 | `backend/app/api/__init__.py` |
| v1 API 路由聚合 | `backend/app/api/v1/__init__.py` |
| 认证 API | `backend/app/api/v1/auth.py` |
| 站点 API | `backend/app/api/v1/sites.py` |
| 产品 API | `backend/app/api/v1/products.py` |
| 任务 API | `backend/app/api/v1/tasks.py` |
| 采集 API | `backend/app/api/v1/scraping.py` |
| 翻译 API | `backend/app/api/v1/translation.py` |
| SEO API | `backend/app/api/v1/seo.py` |
| 价格 API | `backend/app/api/v1/price.py` |
| WordPress API | `backend/app/api/v1/wordpress.py` |
| AI API | `backend/app/api/v1/ai.py` |
| 代理 API | `backend/app/api/v1/proxy.py` |
| 监控 API | `backend/app/api/v1/monitoring.py` |

### 服务层入口

| 功能 | 文件路径 |
|------|----------|
| AI 服务 | `backend/app/services/ai_service.py` |
| 采集服务 | `backend/app/services/scraper_service.py` |
| 翻译服务 | `backend/app/services/translation_service.py` |
| 价格引擎 | `backend/app/services/price_service.py` |
| WordPress 导入 | `backend/app/services/wordpress_service.py` |
| SEO 服务 | `backend/app/services/seo_service.py` |
| 反检测服务 | `backend/app/services/proxy/stealth_service.py` |
| 代理池 | `backend/app/services/proxy/proxy_pool.py` |
| 主题配置生成器 | `backend/app/services/theme_config_generator.py` |
| 页面构建器 | `backend/app/services/page_builder/` |
| 插件系统 | `backend/app/services/plugin_system.py` |
| 监控服务 | `backend/app/services/monitoring_service.py` |
| WooCommerce 自动化 | `backend/app/services/woocommerce_automation.py` |
| 中转通信客户端 | `backend/app/services/relay/` |

### 前端入口

| 功能 | 文件路径 |
|------|----------|
| 应用入口 | `frontend/src/main.ts` |
| 根组件 | `frontend/src/App.vue` |
| 路由配置 | `frontend/src/router/index.ts` |
| 状态管理 | `frontend/src/store/` |
| API 封装 | `frontend/src/api/` |
| 页面视图 | `frontend/src/views/` |
| Vite 配置 | `frontend/vite.config.ts` |

### 中转服务器入口

| 功能 | 文件路径 |
|------|----------|
| 服务入口 | `relay-server/src/index.js` |
| 配置 | `relay-server/src/config/index.js` |
| Socket 服务 | `relay-server/src/server/SocketServer.js` |
| 客户端管理 | `relay-server/src/server/ClientManager.js` |
| 消息路由 | `relay-server/src/message/MessageRouter.js` |
| 消息队列 | `relay-server/src/message/MessageQueue.js` |
| 站点管理 | `relay-server/src/site/SiteManager.js` |
| 认证 | `relay-server/src/auth/AuthManager.js` |
| SQLite 存储 | `relay-server/src/storage/SQLiteDB.js` |
| Redis 客户端 | `relay-server/src/storage/RedisClient.js` |
| REST API | `relay-server/src/routes/api.js` |

### WordPress 主题入口

| 功能 | 文件路径 |
|------|----------|
| 主题功能入口 | `wpforge-theme/functions.php` |
| 自定义设置 | `wpforge-theme/inc/customizer.php` |
| SEO 优化 | `wpforge-theme/inc/seo.php` |
| 性能优化 | `wpforge-theme/inc/performance.php` |
| 钩子系统 | `wpforge-theme/inc/hooks.php` |
| WPForge API | `wpforge-theme/inc/wpforge-api.php` |
| 漏斗数据面板 | `wpforge-theme/inc/funnel-dashboard/` |
| WooCommerce 支持 | `wpforge-theme/inc/woocommerce.php` |
| 构建器支持 | `wpforge-theme/inc/builder-support.php` |

### 测试入口

| 功能 | 文件路径 |
|------|----------|
| 测试配置 | `backend/tests/conftest.py` |
| 单元测试目录 | `backend/tests/unit/` |
| pytest 配置 | `backend/pytest.ini` |
| 覆盖率配置 | `backend/.coveragerc` |

## 下一步

- 阅读 [安装指南](INSTALL.md) 了解如何安装系统
- 阅读 [使用手册](USER_GUIDE.md) 了解如何使用系统
- 阅读 [API 文档](API.md) 了解 API 接口
- 阅读 [贡献指南](CONTRIBUTING.md) 了解如何贡献代码
