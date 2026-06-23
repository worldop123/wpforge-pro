/**
 * WPForge Relay Server - WebSocket服务主类
 * 
 * 管理WebSocket连接、消息处理、事件分发等
 */

const http = require('http');
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { Server } = require('socket.io');
const config = require('../config');
const { createLogger } = require('../utils/logger');
const { getAuthManager } = require('../auth/AuthManager');
const { getClientManager } = require('./ClientManager');
const { getMessageRouter } = require('../message/MessageRouter');
const { getSiteManager } = require('../site/SiteManager');
const { getMessageQueue } = require('../message/MessageQueue');
const { getRedisClient } = require('../storage/RedisClient');

const logger = createLogger('SocketServer');

class SocketServer {
  constructor() {
    this.app = null;
    this.server = null;
    this.io = null;
    this.authManager = getAuthManager();
    this.clientManager = getClientManager();
    this.messageRouter = getMessageRouter();
    this.siteManager = getSiteManager();
    this.messageQueue = getMessageQueue();
    this.redis = getRedisClient();
  }

  /**
   * 启动服务器
   */
  async start() {
    try {
      // 连接Redis
      await this.redis.connect();

      // 创建Express应用
      this.app = express();
      
      // 中间件
      this.app.use(helmet());
      this.app.use(cors({
        origin: config.server.corsOrigin,
        credentials: true,
      }));
      this.app.use(express.json());
      this.app.use(express.urlencoded({ extended: true }));

      // 健康检查端点
      this._setupHealthEndpoints();

      // REST API端点
      this._setupApiEndpoints();

      // 创建HTTP服务器
      this.server = http.createServer(this.app);

      // 创建Socket.io服务器
      this.io = new Server(this.server, {
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

      // 设置认证中间件
      this.io.use((socket, next) => {
        this.authManager.authenticateSocket(socket, next);
      });

      // 设置连接处理
      this.io.on('connection', (socket) => {
        this._handleConnection(socket);
      });

      // 启动监听
      this.server.listen(config.server.port, config.server.host, () => {
        logger.info(`Relay server listening on ${config.server.host}:${config.server.port}`);
        logger.info(`WebSocket endpoint: ws://${config.server.host}:${config.server.port}`);
      });

      return true;
    } catch (err) {
      logger.error('Failed to start server:', err);
      throw err;
    }
  }

  /**
   * 设置健康检查端点
   */
  _setupHealthEndpoints() {
    this.app.get('/health', (req, res) => {
      const stats = this.clientManager.getStats();
      const siteStats = this.siteManager.getStats();
      const queueStats = this.messageQueue.getQueueStats();

      res.json({
        status: 'ok',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        clients: stats,
        sites: siteStats.success ? siteStats.stats : {},
        messages: queueStats.success ? queueStats.stats : {},
        redis: this.redis.isConnected() ? 'connected' : 'disconnected',
      });
    });

    this.app.get('/health/live', (req, res) => {
      res.json({ status: 'alive' });
    });

    this.app.get('/health/ready', (req, res) => {
      const redisOk = this.redis.isConnected();
      if (redisOk) {
        res.json({ status: 'ready' });
      } else {
        res.status(503).json({ status: 'not ready', reason: 'Redis not connected' });
      }
    });
  }

  /**
   * 设置REST API端点
   */
  _setupApiEndpoints() {
    // 管理员登录
    this.app.post('/api/auth/login', (req, res) => {
      const { username, password } = req.body;
      const result = this.authManager.adminLogin(username, password);
      
      if (result.success) {
        res.json(result);
      } else {
        res.status(401).json(result);
      }
    });

    // 站点注册（需要管理员权限）
    this.app.post('/api/sites/register', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.registerSite(req.body);
      res.json(result);
    });

    // 获取站点列表
    this.app.get('/api/sites', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.listSites(req.query);
      res.json(result);
    });

    // 获取站点详情
    this.app.get('/api/sites/:siteId', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const site = this.siteManager.getSite(req.params.siteId);
      if (site) {
        res.json({ success: true, site });
      } else {
        res.status(404).json({ success: false, error: 'Site not found' });
      }
    });

    // 更新站点
    this.app.put('/api/sites/:siteId', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.updateSite(req.params.siteId, req.body);
      res.json(result);
    });

    // 删除站点
    this.app.delete('/api/sites/:siteId', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.deleteSite(req.params.siteId);
      res.json(result);
    });

    // 重新生成Token
    this.app.post('/api/sites/:siteId/regenerate-token', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.regenerateToken(req.params.siteId);
      res.json(result);
    });

    // 分组管理
    this.app.get('/api/groups', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.listGroups();
      res.json(result);
    });

    this.app.post('/api/groups', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);

      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.createGroup(req.body.name, req.body.description);
      res.json(result);
    });

    // 删除分组
    this.app.delete('/api/groups/:groupId', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);

      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.deleteGroup(req.params.groupId);
      if (!result.success && result.error === 'Group not found') {
        return res.status(404).json(result);
      }
      res.json(result);
    });

    // 标签管理
    this.app.get('/api/tags', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.listTags();
      res.json(result);
    });

    this.app.post('/api/tags', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.siteManager.createTag(req.body.name, req.body.color);
      res.json(result);
    });

    // 消息历史
    this.app.get('/api/messages/history', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const result = this.messageQueue.getMessageHistory(req.query);
      res.json(result);
    });

    // 统计信息
    this.app.get('/api/stats', (req, res) => {
      const apiKey = req.headers['x-api-key'];
      const authResult = this.authManager.verifyAdminApiKey(apiKey);
      
      if (!authResult.valid) {
        return res.status(401).json({ success: false, error: 'Unauthorized' });
      }

      const clientStats = this.clientManager.getStats();
      const siteStats = this.siteManager.getStats();
      const queueStats = this.messageQueue.getQueueStats();

      res.json({
        success: true,
        stats: {
          clients: clientStats,
          sites: siteStats.success ? siteStats.stats : {},
          messages: queueStats.success ? queueStats.stats : {},
        },
      });
    });
  }

  /**
   * 处理新连接
   */
  _handleConnection(socket) {
    const clientData = socket.clientData;
    
    logger.info(`New connection: ${socket.id}`, {
      type: clientData.type,
      siteId: clientData.siteId,
      username: clientData.username,
    });

    // 添加到客户端管理器
    this.clientManager.addClient(socket);

    // 如果是插件端，发送离线消息
    if (clientData.type === config.clientTypes.PLUGIN && clientData.siteId) {
      setTimeout(() => {
        this.messageRouter.deliverOfflineMessages(clientData.siteId);
      }, 1000);
    }

    // 设置消息处理
    socket.on('message', (message) => {
      this.messageRouter.routeMessage(socket, message);
    });

    // 设置心跳
    socket.on('heartbeat', () => {
      this.clientManager.handleHeartbeat(socket.id);
      socket.emit('heartbeat_ack', { timestamp: new Date().toISOString() });
    });

    // 设置断开连接处理
    socket.on('disconnect', (reason) => {
      this._handleDisconnect(socket, reason);
    });

    // 设置错误处理
    socket.on('error', (error) => {
      logger.error(`Socket error: ${socket.id}`, { error: error.message });
    });

    // 发送欢迎消息
    socket.emit('connected', {
      message: 'Welcome to WPForge Relay Server',
      serverTime: new Date().toISOString(),
      clientType: clientData.type,
      siteId: clientData.siteId,
    });
  }

  /**
   * 处理断开连接
   */
  _handleDisconnect(socket, reason) {
    const clientData = socket.clientData;
    
    logger.info(`Client disconnected: ${socket.id}`, {
      reason,
      type: clientData?.type,
      siteId: clientData?.siteId,
    });

    this.clientManager.removeClient(socket.id);
  }

  /**
   * 停止服务器
   */
  async stop() {
    try {
      if (this.io) {
        this.io.close();
      }
      
      if (this.server) {
        this.server.close();
      }
      
      await this.redis.disconnect();
      
      logger.info('Server stopped');
      return true;
    } catch (err) {
      logger.error('Error stopping server:', err);
      return false;
    }
  }

  /**
   * 获取IO实例
   */
  getIO() {
    return this.io;
  }

  /**
   * 获取Express应用
   */
  getApp() {
    return this.app;
  }
}

// 单例实例
let instance = null;

function getSocketServer() {
  if (!instance) {
    instance = new SocketServer();
  }
  return instance;
}

module.exports = {
  SocketServer,
  getSocketServer,
};
