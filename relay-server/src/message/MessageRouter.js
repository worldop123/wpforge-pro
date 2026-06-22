/**
 * WPForge Relay Server - 消息路由引擎
 * 
 * 处理消息的路由、转发、确认等
 */

const config = require('../config');
const { createLogger } = require('../utils/logger');
const { getClientManager } = require('../server/ClientManager');
const { getMessageQueue } = require('../message/MessageQueue');
const { getAuthManager } = require('../auth/AuthManager');

const logger = createLogger('MessageRouter');

class MessageRouter {
  constructor() {
    this.clientManager = getClientManager();
    this.messageQueue = getMessageQueue();
    this.authManager = getAuthManager();
  }

  /**
   * 路由消息
   */
  async routeMessage(socket, message) {
    try {
      const { type, target, targetType, data, messageId } = message;
      
      // 验证消息类型
      if (!Object.values(config.messageTypes).includes(type)) {
        return this._sendError(socket, messageId, 'Invalid message type');
      }

      // 生成消息ID（如果没有）
      const msgId = messageId || this.messageQueue.generateMessageId();

      // 获取发送者信息
      const senderInfo = this._getSenderInfo(socket);

      // 根据消息类型处理
      switch (type) {
        case config.messageTypes.COMMAND:
          return await this._handleCommand(socket, msgId, target, targetType, data, senderInfo);
        
        case config.messageTypes.EVENT:
          return await this._handleEvent(socket, msgId, target, targetType, data, senderInfo);
        
        case config.messageTypes.RESPONSE:
          return await this._handleResponse(socket, msgId, target, data, senderInfo);
        
        case config.messageTypes.BROADCAST:
          return await this._handleBroadcast(socket, msgId, data, senderInfo);
        
        case config.messageTypes.HEARTBEAT:
          return this._handleHeartbeat(socket);
        
        default:
          return this._sendError(socket, msgId, 'Unsupported message type');
      }
    } catch (err) {
      logger.error('Error routing message:', err);
      return this._sendError(socket, message?.messageId, 'Internal server error');
    }
  }

  /**
   * 获取发送者信息
   */
  _getSenderInfo(socket) {
    const clientData = socket.clientData || {};
    return {
      type: clientData.type,
      role: clientData.role,
      siteId: clientData.siteId,
      username: clientData.username,
      socketId: socket.id,
    };
  }

  /**
   * 处理指令消息
   */
  async _handleCommand(socket, messageId, target, targetType, data, senderInfo) {
    // 检查权限 - 只有管理端和管理面板可以发送指令
    if (senderInfo.type === config.clientTypes.PLUGIN) {
      return this._sendError(socket, messageId, 'Permission denied: plugins cannot send commands');
    }

    if (!target) {
      return this._sendError(socket, messageId, 'Target required for command');
    }

    const commandMessage = {
      messageId,
      type: config.messageTypes.COMMAND,
      source: senderInfo.siteId || senderInfo.username || senderInfo.socketId,
      sourceType: senderInfo.type,
      command: data?.command,
      params: data?.params || {},
      timestamp: new Date().toISOString(),
    };

    let delivered = false;

    switch (targetType) {
      case 'site':
        // 发送到单个站点
        delivered = this.clientManager.sendToSite(target, 'command', commandMessage);
        if (!delivered) {
          // 站点离线，保存到离线消息
          await this.messageQueue.saveOfflineMessage({
            messageId,
            targetId: target,
            sourceId: senderInfo.siteId || senderInfo.username,
            messageType: config.messageTypes.COMMAND,
            content: commandMessage,
            priority: data?.priority || 'normal',
          });
        }
        break;
      
      case 'group':
        // 发送到分组
        const count = this.clientManager.sendToGroup(target, 'command', commandMessage);
        delivered = count > 0;
        // 注意：分组离线消息暂不支持
        break;
      
      case 'all':
        // 广播到所有站点
        const allCount = this.clientManager.broadcastToPlugins('command', commandMessage);
        delivered = allCount > 0;
        break;
      
      default:
        return this._sendError(socket, messageId, 'Invalid target type');
    }

    // 记录消息历史
    await this.messageQueue.recordMessageHistory({
      messageId,
      sourceId: senderInfo.siteId || senderInfo.username,
      targetId: target,
      messageType: config.messageTypes.COMMAND,
      content: data,
      status: delivered ? 'sent' : 'queued',
    });

    // 返回确认
    socket.emit('message_ack', {
      messageId,
      status: delivered ? 'delivered' : 'queued',
      timestamp: new Date().toISOString(),
    });

    return true;
  }

  /**
   * 处理事件消息
   */
  async _handleEvent(socket, messageId, target, targetType, data, senderInfo) {
    // 插件端发送事件到管理端
    const eventMessage = {
      messageId,
      type: config.messageTypes.EVENT,
      source: senderInfo.siteId,
      sourceType: senderInfo.type,
      event: data?.event,
      data: data?.data || {},
      timestamp: new Date().toISOString(),
    };

    // 发送到所有管理端
    const adminCount = this.clientManager.sendToAdmins('event', eventMessage);
    
    // 发送到所有管理面板
    const panelCount = this.clientManager.sendToAdminPanels('event', eventMessage);

    const delivered = adminCount > 0 || panelCount > 0;

    // 记录消息历史
    await this.messageQueue.recordMessageHistory({
      messageId,
      sourceId: senderInfo.siteId,
      messageType: config.messageTypes.EVENT,
      content: data,
      status: delivered ? 'sent' : 'failed',
    });

    // 返回确认
    socket.emit('message_ack', {
      messageId,
      status: delivered ? 'delivered' : 'no_recipients',
      recipients: adminCount + panelCount,
      timestamp: new Date().toISOString(),
    });

    return true;
  }

  /**
   * 处理响应消息
   */
  async _handleResponse(socket, messageId, target, data, senderInfo) {
    if (!target) {
      return this._sendError(socket, messageId, 'Target required for response');
    }

    const responseMessage = {
      messageId,
      type: config.messageTypes.RESPONSE,
      source: senderInfo.siteId,
      sourceType: senderInfo.type,
      responseTo: data?.responseTo,
      data: data?.data || {},
      success: data?.success !== false,
      error: data?.error || null,
      timestamp: new Date().toISOString(),
    };

    let delivered = false;

    // 尝试发送到目标管理端或管理面板
    // 这里简化处理，发送给所有管理端和管理面板
    const adminCount = this.clientManager.sendToAdmins('response', responseMessage);
    const panelCount = this.clientManager.sendToAdminPanels('response', responseMessage);
    delivered = adminCount > 0 || panelCount > 0;

    // 记录消息历史
    await this.messageQueue.recordMessageHistory({
      messageId,
      sourceId: senderInfo.siteId,
      targetId: target,
      messageType: config.messageTypes.RESPONSE,
      content: data,
      status: delivered ? 'sent' : 'failed',
    });

    return true;
  }

  /**
   * 处理广播消息
   */
  async _handleBroadcast(socket, messageId, data, senderInfo) {
    // 检查权限
    if (senderInfo.type === config.clientTypes.PLUGIN) {
      return this._sendError(socket, messageId, 'Permission denied: plugins cannot broadcast');
    }

    const broadcastMessage = {
      messageId,
      type: config.messageTypes.BROADCAST,
      source: senderInfo.username || senderInfo.socketId,
      sourceType: senderInfo.type,
      data: data || {},
      timestamp: new Date().toISOString(),
    };

    // 广播到所有插件端
    const count = this.clientManager.broadcastToPlugins('broadcast', broadcastMessage);

    // 记录消息历史
    await this.messageQueue.recordMessageHistory({
      messageId,
      sourceId: senderInfo.username,
      messageType: config.messageTypes.BROADCAST,
      content: data,
      status: 'sent',
    });

    // 返回确认
    socket.emit('message_ack', {
      messageId,
      status: 'broadcast',
      recipients: count,
      timestamp: new Date().toISOString(),
    });

    return true;
  }

  /**
   * 处理心跳
   */
  _handleHeartbeat(socket) {
    this.clientManager.handleHeartbeat(socket.id);
    
    // 返回心跳响应
    socket.emit('heartbeat_ack', {
      timestamp: new Date().toISOString(),
    });

    return true;
  }

  /**
   * 发送错误消息
   */
  _sendError(socket, messageId, error) {
    socket.emit('message_error', {
      messageId: messageId || null,
      error,
      timestamp: new Date().toISOString(),
    });
    return false;
  }

  /**
   * 发送离线消息给刚连接的站点
   */
  async deliverOfflineMessages(siteId) {
    try {
      const messages = await this.messageQueue.getOfflineMessages(siteId);
      
      if (messages.length === 0) {
        return 0;
      }

      const client = this.clientManager.getClientBySiteId(siteId);
      if (!client || !client.socket) {
        return 0;
      }

      let delivered = 0;
      for (const msg of messages) {
        const deliveredOk = client.socket.emit(msg.messageType || 'command', msg.content);
        if (deliveredOk) {
          await this.messageQueue.markAsDelivered(msg.messageId);
          delivered++;
        }
      }

      // 清除Redis缓存
      await this.messageQueue.clearOfflineCache(siteId);

      logger.info(`Delivered ${delivered} offline messages to ${siteId}`);
      return delivered;
    } catch (err) {
      logger.error('Error delivering offline messages:', err);
      return 0;
    }
  }
}

// 单例实例
let instance = null;

function getMessageRouter() {
  if (!instance) {
    instance = new MessageRouter();
  }
  return instance;
}

module.exports = {
  MessageRouter,
  getMessageRouter,
};
