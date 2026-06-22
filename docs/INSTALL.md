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
- Docker 20.10+
- Docker Compose 2.0+
- 或 Python 3.11+、Node.js 18+、PostgreSQL 14+、Redis 7+

## 快速开始

### 使用 Docker Compose (推荐)

1. **克隆项目**

```bash
git clone https://github.com/wpforge/wpforge.git
cd wpforge
```

2. **配置环境变量**

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据需要修改配置。

3. **启动服务**

```bash
cd docker
docker-compose up -d
```

4. **初始化数据库**

```bash
docker-compose exec backend alembic upgrade head
```

5. **创建管理员账户**

```bash
docker-compose exec backend python -m app.commands create-admin --username admin --password your_password --email admin@example.com
```

6. **访问系统**

- 前端: http://localhost
- 后端 API: http://localhost/api/v1
- API 文档: http://localhost/api/v1/docs
- Flower 监控: http://localhost:5555

## Docker 部署

### 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 80 | 前端 Web 界面 |
| backend | 8000 | 后端 API 服务 |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存和消息队列 |
| celery-worker | - | Celery 任务 Worker |
| celery-beat | - | Celery 定时任务 |
| flower | 5555 | Celery 任务监控 |
| nginx | 8080 | Nginx 反向代理 |

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend

# 重启服务
docker-compose restart backend

# 更新镜像
docker-compose pull
docker-compose up -d
```

### 数据持久化

Docker Compose 使用命名卷存储数据：
- `postgres_data`: PostgreSQL 数据
- `redis_data`: Redis 数据
- `backend_static`: 后端静态文件
- `backend_media`: 后端媒体文件
- `backend_logs`: 后端日志文件
- `frontend_static`: 前端静态文件

## 手动部署

### 1. 安装依赖

#### Ubuntu/Debian

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python
sudo apt install -y python3 python3-pip python3-venv

# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
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
git clone https://github.com/wpforge/wpforge.git
cd wpforge

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 文件，配置数据库连接等信息

# 初始化数据库
alembic upgrade head

# 创建管理员
python -m app.commands create-admin --username admin --password your_password --email admin@example.com

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 安装前端

```bash
cd ../frontend

# 安装依赖
npm install

# 配置 API 地址
# 编辑 .env 文件，设置 VITE_API_BASE_URL

# 构建前端
npm run build

# 使用 Nginx 或其他 Web 服务器托管 dist 目录
```

### 5. 配置 Celery

```bash
# 启动 Celery Worker
celery -A app.tasks worker --loglevel=info --concurrency=4

# 启动 Celery Beat (定时任务)
celery -A app.tasks beat --loglevel=info
```

建议使用 systemd 或 supervisor 管理这些进程。

## 环境配置

### 必需配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | 应用密钥，用于加密等 | - |
| `DATABASE_URL` | 数据库连接字符串 | - |
| `REDIS_URL` | Redis 连接字符串 | - |

### 数据库配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POSTGRES_DB` | 数据库名 | `wpforge` |
| `POSTGRES_USER` | 数据库用户名 | `wpforge` |
| `POSTGRES_PASSWORD` | 数据库密码 | `wpforge_password` |
| `POSTGRES_HOST` | 数据库主机 | `localhost` |
| `POSTGRES_PORT` | 数据库端口 | `5432` |

### Redis 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `REDIS_PASSWORD` | Redis 密码 | `redis_password` |
| `REDIS_HOST` | Redis 主机 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |

### JWT 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JWT_SECRET` | JWT 密钥 | 与 SECRET_KEY 相同 |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 访问令牌过期时间(分钟) | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 刷新令牌过期时间(天) | `7` |

### AI 模型配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AI_PROVIDER` | 默认 AI 提供商 | `openai` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `OPENAI_MODEL` | OpenAI 模型 | `gpt-3.5-turbo` |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |
| `ANTHROPIC_MODEL` | Anthropic 模型 | `claude-3-sonnet-20240229` |
| `GOOGLE_API_KEY` | Google API 密钥 | - |
| `GOOGLE_MODEL` | Google 模型 | `gemini-pro` |
| `OLLAMA_BASE_URL` | Ollama 地址 | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama 模型 | `llama2` |

### 翻译配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TRANSLATION_PROVIDER` | 默认翻译引擎 | `google` |
| `DEEPL_API_KEY` | DeepL API 密钥 | - |
| `GOOGLE_TRANSLATE_API_KEY` | Google 翻译 API 密钥 | - |

### 代理配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PROXY_ENABLED` | 是否启用代理 | `false` |
| `PROXY_PROVIDER` | 代理提供商 | `brightdata` |
| `BRIGHTDATA_USERNAME` | BrightData 用户名 | - |
| `BRIGHTDATA_PASSWORD` | BrightData 密码 | - |
| `OXYLABS_USERNAME` | Oxylabs 用户名 | - |
| `OXYLABS_PASSWORD` | Oxylabs 密码 | - |

### 采集配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SCRAPING_CONCURRENCY` | 采集并发数 | `5` |
| `SCRAPING_DELAY_MIN` | 最小延迟(秒) | `1` |
| `SCRAPING_DELAY_MAX` | 最大延迟(秒) | `3` |
| `SCRAPING_TIMEOUT` | 超时时间(秒) | `30` |
| `SCRAPING_RETRY_TIMES` | 重试次数 | `3` |

### 日志配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `LOG_FILE` | 日志文件路径 | `logs/wpforge.log` |
| `LOG_MAX_SIZE` | 日志文件最大大小 | `10MB` |
| `LOG_BACKUP_COUNT` | 日志备份数量 | `5` |

## 常见问题

### 1. 如何重置管理员密码？

```bash
docker-compose exec backend python -m app.commands reset-password --username admin --password new_password
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

# 重新构建镜像
cd docker
docker-compose build

# 重启服务
docker-compose up -d

# 执行数据库迁移
docker-compose exec backend alembic upgrade head
```

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

编辑 `docker/docker-compose.yml` 文件，修改对应服务的端口映射即可。

### 8. 如何配置 HTTPS？

建议使用 Nginx 反向代理 + Let's Encrypt 证书，或使用 Cloudflare 等 CDN 服务。

## 下一步

- 阅读 [使用手册](USER_GUIDE.md) 了解如何使用系统
- 阅读 [API 文档](API.md) 了解 API 接口
- 阅读 [开发指南](DEVELOPMENT.md) 了解如何开发
- 阅读 [贡献指南](CONTRIBUTING.md) 了解如何贡献代码
