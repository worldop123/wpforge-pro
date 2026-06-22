/**
 * WPForge Relay Server - 配置文件
 * 
 * 管理中转服务器的所有配置项
 */

require('dotenv').config();

const config = {
  // 服务器配置
  server: {
    port: parseInt(process.env.RELAY_PORT || '3001', 10),
    host: process.env.RELAY_HOST || '0.0.0.0',
    corsOrigin: process.env.CORS_ORIGIN || '*',
  },

  // Redis配置
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD || '',
    db: parseInt(process.env.REDIS_DB || '0', 10),
    keyPrefix: 'wpforge:relay:',
  },

  // SQLite配置
  sqlite: {
    path: process.env.SQLITE_PATH || './data/relay.db',
  },

  // JWT配置
  jwt: {
    secret: process.env.JWT_SECRET || 'wpforge-relay-secret-key-change-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
    issuer: 'wpforge-relay',
  },

  // 认证配置
  auth: {
    adminApiKey: process.env.ADMIN_API_KEY || 'admin-api-key-change-in-production',
    superAdminApiKey: process.env.SUPER_ADMIN_API_KEY || 'super-admin-api-key-change-in-production',
    tokenLength: 32,
  },

  // WebSocket配置
  socket: {
    pingInterval: 25000,
    pingTimeout: 20000,
    maxHttpBufferSize: 1e6,
    transports: ['websocket', 'polling'],
  },

  // 消息配置
  message: {
    maxSize: 1024 * 1024, // 1MB
    ttl: 7 * 24 * 60 * 60, // 7天
    maxOfflineMessages: 1000,
    priorityLevels: ['low', 'normal', 'high', 'urgent'],
  },

  // 心跳配置
  heartbeat: {
    interval: 30000, // 30秒
    timeout: 10000, // 10秒超时
    maxMissed: 3, // 最多错过3次心跳
  },

  // 限流配置
  rateLimit: {
    enabled: true,
    points: 100, // 每个客户端每秒100个消息
    duration: 1, // 1秒窗口
    blockDuration: 60, // 封禁60秒
  },

  // 日志配置
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || './logs/relay.log',
    maxSize: '10m',
    maxFiles: '14d',
  },

  // 客户端类型
  clientTypes: {
    ADMIN: 'admin',           // 管理端（WPForge后端）
    PLUGIN: 'plugin',         // 插件端（WordPress插件）
    ADMIN_PANEL: 'admin_panel', // 管理面板（前端）
  },

  // 消息类型
  messageTypes: {
    COMMAND: 'command',       // 指令
    EVENT: 'event',           // 事件
    RESPONSE: 'response',     // 响应
    BROADCAST: 'broadcast',   // 广播
    HEARTBEAT: 'heartbeat',   // 心跳
    AUTH: 'auth',             // 认证
  },

  // 权限级别
  permissionLevels: {
    SUPER_ADMIN: 'super_admin',
    ADMIN: 'admin',
    SITE: 'site',
  },
};

module.exports = config;
