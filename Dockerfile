# WPForge Backend Dockerfile
# 多阶段构建，优化镜像体积

FROM python:3.11-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖到临时目录
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# 第二阶段：运行时镜像
FROM python:3.11-slim

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从builder阶段复制已安装的依赖
COPY --from=builder /install /usr/local

# 创建非root用户
RUN groupadd -r wpforge && useradd -r -g wpforge wpforge

# 复制应用代码
COPY backend/ /app/

# 复制项目根目录的配置文件
COPY .env.example /app/.env.example

# 设置工作目录
WORKDIR /app

# 创建必要的目录
RUN mkdir -p /app/data /app/logs /app/tmp && \
    chown -R wpforge:wpforge /app

# 切换到非root用户
USER wpforge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
