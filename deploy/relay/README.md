# WPForge Relay 部署说明

## 快速开始

### 1. 环境准备

确保已安装 Docker 和 Docker Compose：
- Docker >= 20.10
- Docker Compose >= 2.0

### 2. 配置环境变量

```bash
cd deploy/relay
cp .env.example .env
```

编辑 `.env` 文件，修改以下关键配置：

```env
# 必须修改的安全配置
JWT_SECRET=your-very-long-random-secret-key
ADMIN_API_KEY=your-admin-api-key
SUPER_ADMIN_API_KEY=your-super-admin-api-key

# 可选修改
CORS_ORIGIN=https://your-domain.com
```

### 3. 启动服务

#### 基础部署（中转服务器 + Redis + 管理面板）

```bash
docker-compose up -d
```

#### 完整部署（包含 Nginx 反向代理）

```bash
docker-compose --profile nginx up -d
```

### 4. 验证部署

检查服务状态：
```bash
docker-compose ps
```

查看日志：
```bash
docker-compose logs -f relay-server
```

### 5. 访问管理面板

- 直接访问：http://localhost:8080
- 通过Nginx访问：http://localhost

默认管理员账号：
- 用户名：admin
- 密码：admin123

**重要：首次登录后请立即修改默认密码！**

## 配置说明

### 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| relay-server | 3001 | 中转服务器（WebSocket + HTTP API） |
| admin-panel | 8080 | 管理面板 |
| redis | 6379 | Redis缓存 |
| nginx | 80/443 | Nginx反向代理（可选） |

### 数据持久化

- `relay-data` - 中转服务器数据（SQLite数据库）
- `redis-data` - Redis数据
- `./logs` - 日志文件
- `./ssl` - SSL证书（使用Nginx时）

## 生产环境部署建议

### 1. 使用Nginx + SSL

1. 将SSL证书放入 `./ssl` 目录：
   - `fullchain.pem` - 证书链
   - `privkey.pem` - 私钥

2. 创建Nginx站点配置：
```nginx
server {
    listen 443 ssl http2;
    server_name relay.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # 中转服务器代理
    location / {
        proxy_pass http://relay-server:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### 2. 安全加固

- 修改所有默认密码和密钥
- 配置防火墙，只开放必要端口
- 启用HTTPS
- 配置IP白名单
- 定期更新镜像

### 3. 性能优化

- 根据连接数调整Redis内存限制
- 配置适当的文件描述符限制
- 使用SSD存储提升SQLite性能

## 常见问题

### 1. WebSocket连接失败

- 检查防火墙是否允许WebSocket连接
- 确保Nginx配置了Upgrade头
- 检查CORS配置

### 2. 站点连接后立即断开

- 检查Token是否正确
- 查看服务器日志获取详细错误信息
- 检查心跳配置

### 3. 消息丢失

- 检查Redis是否正常运行
- 检查离线消息配置
- 查看消息队列状态

## 监控与运维

### 健康检查

所有服务都配置了健康检查，可以通过以下方式监控：

```bash
# 中转服务器
curl http://localhost:3001/health

# 管理面板
curl http://localhost:8080/health

# Redis
docker-compose exec redis redis-cli ping
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f relay-server

# 查看最近100行
docker-compose logs --tail=100 relay-server
```

### 备份与恢复

```bash
# 备份Redis数据
docker-compose exec redis redis-cli BGSAVE
docker cp wpforge-relay-redis:/data/dump.rdb ./backup/

# 备份SQLite数据库
docker cp wpforge-relay-server:/app/data/relay.db ./backup/
```

## 升级

```bash
# 拉取最新镜像
docker-compose pull

# 重新构建并启动
docker-compose up -d --build
```

## 卸载

```bash
# 停止并删除容器
docker-compose down

# 删除数据卷（谨慎操作！）
docker-compose down -v
```
