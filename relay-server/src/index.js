/**
 * WPForge Relay Server - 中转服务器入口文件
 * 
 * 提供WebSocket双向通信、消息转发、站点管理等功能
 */

const express = require('express');
const http = require('http');
const cors = require('cors');
const helmet = require('helmet');

const config = require('./config');
const logger = require('./utils/logger');
const { getRedisClient } = require('./storage/RedisClient');
const { getSQLiteDB } = require('./storage/SQLiteDB');
const { getAuthManager } = require('./auth/AuthManager');

// 创建Express应用
const app = express();

// 安全中间件
app.use(helmet());
app.use(cors({
  origin: config.server.corsOrigin,
  credentials: true,
}));

// 解析中间件
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// 创建HTTP服务器
const server = http.createServer(app);

// 初始化Socket.IO
const { Server } = require('socket.io');
const io = new Server(server, {
  cors: {
    origin: config.server.corsOrigin,
    methods: ['GET', 'POST'],
    credentials: true,
  },
  pingInterval: config.socket.pingInterval,
  pingTimeout: config.socket.pingTimeout,
  maxHttpBufferSize: config.socket.maxHttpBufferSize,
  transports: config.socket.transports,
});

// 全局变量
let redisClient = null;
let sqliteDB = null;
let authManager = null;

// 客户端连接管理
const clients = new Map(); // socketId -> client info
const siteClients = new Map(); // siteId -> socketId

/**
 * 初始化服务
 */
async function initialize() {
  try {
    logger.info('Initializing WPForge Relay Server...');

    // 初始化Redis
    redisClient = getRedisClient();
    await redisClient.connect();
    logger.info('Redis connected');

    // 初始化SQLite
    sqliteDB = getSQLiteDB();
    await sqliteDB.init();
    logger.info('SQLite initialized');

    // 初始化认证管理器
    authManager = getAuthManager();
    logger.info('Auth manager initialized');

    // 设置Socket.IO认证中间件
    io.use((socket, next) => {
      authManager.authenticateSocket(socket, next);
    });

    // 处理连接
    io.on('connection', handleConnection);

    // 健康检查接口
    app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        connections: clients.size,
        sites: siteClients.size,
      });
    });

    // API路由
    app.use('/api/v1', require('./routes/api'));

    // 启动服务器
    server.listen(config.server.port, config.server.host, () => {
      logger.info(`WPForge Relay Server listening on ${config.server.host}:${config.server.port}`);
      logger.info(`Environment: ${config.nodeEnv}`);
    });

  } catch (error) {
    logger.error('Failed to initialize server:', error);
    process.exit(1);
  }
}

/**
 * 处理客户端连接
 */
function handleConnection(socket) {
  const clientInfo = socket.auth;
  const clientId = socket.id;

  logger.info(`Client connected: ${clientInfo.clientType} (${clientId})`);

  // 存储客户端信息
  clients.set(clientId, {
    id: clientId,
    type: clientInfo.clientType,
    siteId: clientInfo.siteId || null,
    userId: clientInfo.userId || null,
    role: clientInfo.role || null,
    connectedAt: new Date().toISOString(),
    lastHeartbeat: new Date().toISOString(),
    socket: socket,
  });

  // 如果是插件端，记录站点连接
  if (clientInfo.clientType === 'plugin' && clientInfo.siteId) {
    siteClients.set(clientInfo.siteId, clientId);
    
    // 更新站点最后在线时间
    sqliteDB.execute(
      'UPDATE sites SET last_seen = ?, status = ? WHERE site_id = ?',
      [new Date().toISOString(), 'online', clientInfo.siteId]
    );

    // 广播站点上线事件
    io.emit('client_connected', {
      clientId: clientId,
      type: 'plugin',
      siteId: clientInfo.siteId,
      timestamp: new Date().toISOString(),
    });
  }

  // 注册事件处理
  registerEventHandlers(socket, clientInfo);

  // 处理断开连接
  socket.on('disconnect', () => {
    handleDisconnection(socket, clientInfo);
  });

  // 发送连接确认
  socket.emit('connected', {
    clientId: clientId,
    serverTime: new Date().toISOString(),
  });
}

/**
 * 注册事件处理器
 */
function registerEventHandlers(socket, clientInfo) {
  // 心跳
  socket.on('heartbeat', (data) => {
    const client = clients.get(socket.id);
    if (client) {
      client.lastHeartbeat = new Date().toISOString();
    }
    socket.emit('heartbeat_ack', { timestamp: new Date().toISOString() });
  });

  // 事件消息
  socket.on('event', (data) => {
    handleEventMessage(socket, data, clientInfo);
  });

  // 指令消息
  socket.on('command', (data) => {
    handleCommandMessage(socket, data, clientInfo);
  });

  // 响应消息
  socket.on('response', (data) => {
    handleResponseMessage(socket, data, clientInfo);
  });

  // 广播消息
  socket.on('broadcast', (data) => {
    handleBroadcastMessage(socket, data, clientInfo);
  });
}

/**
 * 处理事件消息
 */
function handleEventMessage(socket, data, clientInfo) {
  const eventType = data.event || 'unknown';
  const sourceId = clientInfo.siteId || clientInfo.userId || socket.id;

  logger.debug(`Event received: ${eventType} from ${sourceId}`);

  // 存储消息到历史
  saveMessageHistory('event', sourceId, null, data);

  // 广播给所有管理端
  const adminSockets = Array.from(clients.values())
    .filter(c => c.type === 'admin' || c.type === 'admin_panel')
    .map(c => c.socket);

  adminSockets.forEach(adminSocket => {
    adminSocket.emit('event', {
      ...data,
      sourceId: sourceId,
      sourceType: clientInfo.clientType,
      receivedAt: new Date().toISOString(),
    });
  });
}

/**
 * 处理指令消息
 */
function handleCommandMessage(socket, data, clientInfo) {
  const command = data.command || 'unknown';
  const targetId = data.targetId;
  const messageId = data.messageId;

  logger.debug(`Command received: ${command} to ${targetId}`);

  // 权限检查
  if (clientInfo.role !== 'super_admin' && clientInfo.role !== 'admin') {
    socket.emit('error', { message: 'Permission denied' });
    return;
  }

  // 查找目标站点
  const targetSocketId = siteClients.get(targetId);
  if (!targetSocketId) {
    // 站点离线，存储离线消息
    saveOfflineMessage(targetId, messageId, 'command', data);
    socket.emit('response', {
      responseTo: messageId,
      success: false,
      error: 'Site offline, message queued',
    });
    return;
  }

  const targetClient = clients.get(targetSocketId);
  if (!targetClient) {
    socket.emit('error', { message: 'Target client not found' });
    return;
  }

  // 转发指令到目标站点
  targetClient.socket.emit('command', {
    ...data,
    sourceId: clientInfo.siteId || clientInfo.userId || socket.id,
    receivedAt: new Date().toISOString(),
  });

  // 存储消息历史
  saveMessageHistory('command', clientInfo.siteId || socket.id, targetId, data);
}

/**
 * 处理响应消息
 */
function handleResponseMessage(socket, data, clientInfo) {
  const responseTo = data.responseTo;
  const sourceId = clientInfo.siteId || socket.id;

  logger.debug(`Response received for: ${responseTo}`);

  // 存储消息历史
  saveMessageHistory('response', sourceId, null, data);

  // 查找原始发送者并转发响应
  // 这里简化处理，广播给所有管理端
  const adminSockets = Array.from(clients.values())
    .filter(c => c.type === 'admin' || c.type === 'admin_panel')
    .map(c => c.socket);

  adminSockets.forEach(adminSocket => {
    adminSocket.emit('response', {
      ...data,
      sourceId: sourceId,
      receivedAt: new Date().toISOString(),
    });
  });
}

/**
 * 处理广播消息
 */
function handleBroadcastMessage(socket, data, clientInfo) {
  const eventType = data.event || 'unknown';

  logger.debug(`Broadcast received: ${eventType}`);

  // 权限检查
  if (clientInfo.role !== 'super_admin' && clientInfo.role !== 'admin') {
    socket.emit('error', { message: 'Permission denied' });
    return;
  }

  // 广播给所有插件端
  const pluginSockets = Array.from(clients.values())
    .filter(c => c.type === 'plugin')
    .map(c => c.socket);

  pluginSockets.forEach(pluginSocket => {
    pluginSocket.emit('broadcast', {
      ...data,
      sourceId: clientInfo.userId || socket.id,
      receivedAt: new Date().toISOString(),
    });
  });

  // 存储消息历史
  saveMessageHistory('broadcast', socket.id, null, data);
}

/**
 * 处理断开连接
 */
function handleDisconnection(socket, clientInfo) {
  const clientId = socket.id;

  logger.info(`Client disconnected: ${clientInfo.clientType} (${clientId})`);

  // 移除客户端
  clients.delete(clientId);

  // 如果是插件端，更新站点状态
  if (clientInfo.clientType === 'plugin' && clientInfo.siteId) {
    siteClients.delete(clientInfo.siteId);

    // 更新站点状态
    sqliteDB.execute(
      'UPDATE sites SET last_seen = ?, status = ? WHERE site_id = ?',
      [new Date().toISOString(), 'offline', clientInfo.siteId]
    );

    // 广播站点下线事件
    io.emit('client_disconnected', {
      clientId: clientId,
      type: 'plugin',
      siteId: clientInfo.siteId,
      timestamp: new Date().toISOString(),
    });
  }
}

/**
 * 保存消息历史
 */
function saveMessageHistory(type, sourceId, targetId, data) {
  try {
    sqliteDB.execute(
      `INSERT INTO message_history (message_id, message_type, source_id, target_id, content, created_at)
       VALUES (?, ?, ?, ?, ?, ?)`,
      [
        data.messageId || Date.now().toString(),
        type,
        sourceId,
        targetId,
        JSON.stringify(data),
        new Date().toISOString(),
      ]
    );
  } catch (error) {
    logger.error('Failed to save message history:', error);
  }
}

/**
 * 保存离线消息
 */
function saveOfflineMessage(targetId, messageId, type, data) {
  try {
    sqliteDB.execute(
      `INSERT INTO offline_messages (message_id, target_id, message_type, content, priority, status, expires_at, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        messageId,
        targetId,
        type,
        JSON.stringify(data),
        data.priority || 0,
        'pending',
        new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7天后过期
        new Date().toISOString(),
      ]
    );
  } catch (error) {
    logger.error('Failed to save offline message:', error);
  }
}

// 优雅关闭
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');
  
  server.close(() => {
    logger.info('HTTP server closed');
  });

  if (redisClient) {
    await redisClient.disconnect();
    logger.info('Redis disconnected');
  }

  if (sqliteDB) {
    sqliteDB.close();
    logger.info('SQLite closed');
  }

  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully...');
  
  server.close(() => {
    logger.info('HTTP server closed');
  });

  if (redisClient) {
    await redisClient.disconnect();
    logger.info('Redis disconnected');
  }

  if (sqliteDB) {
    sqliteDB.close();
    logger.info('SQLite closed');
  }

  process.exit(0);
});

// 未捕获的异常
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// 启动服务
initialize();

module.exports = { app, server, io, clients, siteClients };
