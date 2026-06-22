# WPForge 安装指南

## 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [Docker 部署](#docker-部署)
- [手动部署](#手动部署)
- [环境配置](#环境配置)
- [常见问题](#常见问题)

## 系统要求

### 最低配置
- CPU: 2 核心
- 内存: 4 GB
- 磁盘: 20 GB 可用空间
- 操作系统: Linux (推荐 Ubuntu 20.04+)

### 推荐配置
- CPU: 4 核心及以上
- 内存: 8 GB 及以上
- 磁盘: 50 GB SSD 及以上
- 操作系统: Ubuntu 22.04 LTS

### 软件依赖

Docker 部署（推荐）：
- Docker 20.10+
- Docker Compose 2.0+

手动部署：
- Python 3.11+
- Node.js 18+（前端构建，推荐 20+）
- PostgreSQL 14+（生产环境）
- Redis 7+
- Git

> 说明：WPForge 不使用 Alembic 做数据库迁移，初始化通过 `app.core.database.init_db()` 创建所有表。开发/测试环境可直接使用 SQLite。

## 快速开始

### 使用 Docker Compose (推荐)

1. **克隆项目**

```bash
git clone https://github.com/worldop123/wpforge.git
cd wpforge
```

2. **配置环境变量**

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据需要修改配置（数据库密码、SECRET_KEY、AI API Key 等）。

3. **启动服务**

在项目根目录执行：

```bash
docker-compose up -d
```

> 注意：请在项目根目录执行，不要 `cd docker`，根目录的 `docker-compose.yml` 是统一入口。

4. **初始化数据库**

WPForge 不使用 Alembic，数据库表通过 SQLAlchemy `Base.metadata.create_all` 创建。首次启动后执行：

```bash
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
```

5. **创建管理员账户**

```bash
docker-compose exec backend python -m app.cli create-admin --username admin --password yourpassword --email admin@example.com
```

6. **访问系统**

启动完成后，可通过以下地址访问：

- 前端 Web 界面: http://localhost:8080
- 后端 API: http://localhost:8000
- API 文档 (Swagger UI): http://localhost:8000/api/docs
- API 文档 (ReDoc): http://localhost:8000/api/redoc
- 健康检查: http://localhost:8000/api/health
- Flower 监控 (需启用 monitoring profile): http://localhost:5555
- Relay Server (需启用 relay profile): http://localhost:3001

### 启用可选服务

```bash
# 启用 Nginx 反向代理
docker-compose --profile nginx up -d

# 启用中转服务器 (Relay Server)
docker-compose --profile relay up -d

# 启用 Flower 监控
docker-compose --profile monitoring up -d
```

## Docker 部署

### 服务说明

| 服务 | 端口 | 说明 | 启动方式 |
|------|------|------|----------|
| frontend | 8080 | 前端 Web 界面 | 默认 |
| backend | 8000 | 后端 API 服务 | 默认 |
| postgres | 5432 | PostgreSQL 数据库 | 默认 |
| redis | 6379 | Redis 缓存和消息队列 | 默认 |
| celery-worker | - | Celery 任务 Worker | 默认 |
| celery-beat | - | Celery 定时任务 | 默认 |
| nginx | 80 / 443 | Nginx 反向代理 | `--profile nginx` |
| relay-server | 3001 | 中转服务器 | `--profile relay` |
| flower | 5555 | Celery 任务监控 | `--profile monitoring` |

### 常用命令

```bash
# 启动所有默认服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 重新构建镜像
docker-compose build

# 更新镜像并重启
docker-compose up -d --build
```

### 健康检查

后端健康检查路径为 `/api/health`，已在 `docker-compose.yml` 中配置：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
```

### 数据持久化

Docker Compose 使用命名卷存储数据：
- `postgres_data`: PostgreSQL 数据
- `redis_data`: Redis 数据
- `backend_static`: 后端静态文件
- `backend_media`: 后端媒体文件
- `backend_logs`: 后端日志文件
- `nginx_logs`: Nginx 日志（启用 nginx 时）

## 手动部署

### 1. 安装系统依赖

#### Ubuntu/Debian

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11+
sudo apt install -y python3.11 python3.11-pip python3.11-venv

# 安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 安装 Redis
sudo apt install -y redis-server

# 安装 Playwright 依赖
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

### 2. 配置数据库

```bash
# 创建数据库和用户
sudo -u postgres psql
```

```sql
CREATE DATABASE wpforge;
CREATE USER wpforge WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE wpforge TO wpforge;
\q
```

### 3. 安装后端

```bash
# 克隆项目
git clone https://github.com/worldop123/wpforge.git
cd wpforge

# 创建虚拟环境（在 backend 目录）
cd backend
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 文件，配置 DATABASE_URL、REDIS_URL、SECRET_KEY 等

# 初始化数据库（不使用 Alembic，直接建表）
python -c "from app.core.database import init_db; init_db()"

# 创建管理员
python -m app.cli create-admin --username admin --password yourpassword --email admin@example.com

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
# 开发模式（自动重载）：
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 安装前端

```bash
cd ../frontend

# 安装依赖
npm install

# 配置 API 地址（如需）
# 编辑 vite.config.ts 中的 proxy 或环境变量

# 构建前端
npm run build

# 使用 Nginx 或其他 Web 服务器托管 dist 目录
```

### 5. 配置 Celery（可选，用于异步任务）

```bash
cd ../backend
source venv/bin/activate

# 启动 Celery Worker
celery -A app.tasks worker --loglevel=info --concurrency=4

# 启动 Celery Beat (定时任务)
celery -A app.tasks beat --loglevel=info
```

建议使用 systemd 或 supervisor 管理这些进程。

### 6. 启动中转服务器（可选）

```bash
cd ../relay-server
npm install
npm start
# 默认监听 3001 端口
```

## 环境配置

完整的环境变量示例见 `.env.example`，以下为常用配置项。

### 必需配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | 应用密钥，用于 JWT 加密等 | `change-this-to-...` |
| `DATABASE_URL` | 数据库连接字符串 | `postgresql+psycopg2://...` |
| `REDIS_URL` | Redis 连接字符串 | `redis://redis:6379/0` |

### 数据库配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POSTGRES_DB` | 数据库名 | `wpforge` |
| `POSTGRES_USER` | 数据库用户名 | `wpforge` |
| `POSTGRES_PASSWORD` | 数据库密码 | `wpforge_password` |
| `POSTGRES_PORT` | 数据库端口 | `5432` |

> 开发/测试环境可使用 SQLite：`DATABASE_URL=sqlite:///./wpforge.db`

### Redis 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `REDIS_PASSWORD` | Redis 密码 | `redis_password` |
| `REDIS_PORT` | Redis 端口 | `6379` |

### JWT 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ALGORITHM` | JWT 算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌过期时间(分钟) | `10080` |

### AI 模型配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEFAULT_AI_PROVIDER` | 默认 AI 提供商 | `openai` |
| `DEFAULT_AI_MODEL` | 默认 AI 模型 | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_BASE_URL` | OpenAI API 地址 | `https://api.openai.com/v1` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |
| `GOOGLE_API_KEY` | Google API 密钥 | - |
| `OLLAMA_BASE_URL` | Ollama 地址 | `http://localhost:11434` |

### 翻译配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPL_API_KEY` | DeepL API 密钥 | - |
| `GOOGLE_TRANSLATE_API_KEY` | Google 翻译 API 密钥 | - |
| `DEFAULT_SOURCE_LANG` | 默认源语言 | `auto` |
| `DEFAULT_TARGET_LANG` | 默认目标语言 | `en` |

### 代理配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PROXY_ENABLED` | 是否启用代理 | `false` |
| `DEFAULT_PROXY_PROVIDER` | 默认代理提供商 | `none` |
| `BRIGHTDATA_USER` | BrightData 用户名 | - |
| `BRIGHTDATA_PASSWORD` | BrightData 密码 | - |
| `OXYLABS_USER` | Oxylabs 用户名 | - |
| `OXYLABS_PASSWORD` | Oxylabs 密码 | - |

### 采集配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MAX_CONCURRENT_SCRAPERS` | 采集并发数 | `3` |
| `SCRAPER_DELAY_BETWEEN_REQUESTS` | 请求间隔(秒) | `2.0` |
| `MAX_RETRIES` | 重试次数 | `3` |

### 日志配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FILE` | 日志文件路径 | - |
| `DEBUG` | 调试模式 | `false` |

### Docker Compose 端口配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `BACKEND_PORT` | 后端端口 | `8000` |
| `FRONTEND_PORT` | 前端端口 | `8080` |
| `RELAY_PORT` | 中转服务器端口 | `3001` |
| `FLOWER_PORT` | Flower 监控端口 | `5555` |
| `NGINX_PORT` | Nginx HTTP 端口 | `80` |
| `NGINX_SSL_PORT` | Nginx HTTPS 端口 | `443` |

## 常见问题

### 1. 如何重置管理员密码？

WPForge 当前未提供 reset-password 子命令，可通过 Python 交互式命令重置：

```bash
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == 'admin').first()
if user:
    user.hashed_password = get_password_hash('new_password')
    db.commit()
    print('密码已重置')
db.close()
"
```

### 2. 如何备份数据？

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U wpforge wpforge > backup.sql

# 备份媒体文件
docker cp wpforge-backend:/app/media ./media_backup
```

### 3. 如何恢复数据？

```bash
# 恢复数据库
cat backup.sql | docker-compose exec -T postgres psql -U wpforge wpforge

# 恢复媒体文件
docker cp ./media_backup wpforge-backend:/app/media
```

### 4. 如何查看日志？

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看 Celery 日志
docker-compose logs -f celery-worker

# 查看所有日志
docker-compose logs -f
```

### 5. 如何更新系统？

```bash
# 拉取最新代码
git pull

# 重新构建镜像并启动
docker-compose up -d --build

# 重新初始化数据库（如有新表）
docker-compose exec backend python -c "from app.core.database import init_db; init_db()"
```

> 注意：WPForge 不使用 Alembic 迁移工具，数据库表结构通过 `init_db()` 创建。新增字段需手动处理或重建数据库。

### 6. Playwright 浏览器安装失败怎么办？

```bash
# 手动安装浏览器
playwright install chromium --with-deps

# 或使用系统包管理器安装依赖
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2
```

### 7. 如何修改端口？

编辑根目录的 `docker-compose.yml` 文件，或在 `.env` 中设置对应端口变量（如 `BACKEND_PORT`、`FRONTEND_PORT`）。

### 8. 如何配置 HTTPS？

建议使用 Nginx 反向代理 + Let's Encrypt 证书，或使用 Cloudflare 等 CDN 服务。启用 Nginx profile：

```bash
docker-compose --profile nginx up -d
```

并将 SSL 证书放置到 `docker/nginx/ssl/` 目录。

### 9. bcrypt 安装报错怎么办？

WPForge 要求 `bcrypt<4.1`（见 `requirements.txt`），与 `passlib[bcrypt]` 配合使用。如遇安装问题：

```bash
pip install "bcrypt<4.1"
pip install "passlib[bcrypt]==1.7.4"
```

## 下一步

- 阅读 [使用手册](USER_GUIDE.md) 了解如何使用系统
- 阅读 [API 文档](API.md) 了解 API 接口
- 阅读 [开发指南](DEVELOPMENT.md) 了解如何开发
- 阅读 [贡献指南](CONTRIBUTING.md) 了解如何贡献代码
