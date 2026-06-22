/**
 * WPForge Relay Server - 客户端管理器
 * 
 * 管理所有连接的客户端，包括连接状态、心跳、分组等
 */

const config = require('../config');
const { createLogger } = require('../utils/logger');
const { getSiteManager } = require('../site/SiteManager');

const logger = createLogger('ClientManager');

class ClientManager {
  constructor() {
    // 存储所有连接的客户端
    // key: socket.id, value: client info
    this.clients = new Map();
    
    // 按siteId索引的客户端
    // key: siteId, value: socket.id
    this.siteClients = new Map();
    
    // 按类型索引的客户端
    this.adminClients = new Set();
    this.pluginClients = new Set();
    this.adminPanelClients = new Set();
    
    // 心跳追踪
    this.heartbeatTimers = new Map();
    
    this.siteManager = getSiteManager();
  }

  /**
   * 添加客户端
   */
  addClient(socket) {
    const clientData = socket.clientData;
    if (!clientData) {
      logger.warn('Client has no clientData');
      return false;
    }

    const clientInfo = {
      socketId: socket.id,
      type: clientData.type,
      role: clientData.role,
      siteId: clientData.siteId,
      username: clientData.username,
      connectedAt: new Date(),
      lastHeartbeat: new Date(),
      missedHeartbeats: 0,
      socket,
    };

    this.clients.set(socket.id, clientInfo);

    // 按类型分类
    switch (clientData.type) {
      case config.clientTypes.ADMIN:
        this.adminClients.add(socket.id);
        break;
      case config.clientTypes.PLUGIN:
        this.pluginClients.add(socket.id);
        if (clientData.siteId) {
          this.siteClients.set(clientData.siteId, socket.id);
          // 更新站点状态为在线
          this.siteManager.updateSiteStatus(clientData.siteId, 'online');
        }
        break;
      case config.clientTypes.ADMIN_PANEL:
        this.adminPanelClients.add(socket.id);
        break;
    }

    // 启动心跳检查
    this._startHeartbeatCheck(socket.id);

    logger.info(`Client added: ${socket.id}`, {
      type: clientData.type,
      siteId: clientData.siteId,
      username: clientData.username,
    });

    // 广播客户端连接事件
    this._broadcastClientEvent('client_connected', clientInfo);

    return true;
  }

  /**
   * 移除客户端
   */
  removeClient(socketId) {
    const clientInfo = this.clients.get(socketId);
    if (!clientInfo) {
      return false;
    }

    this.clients.delete(socketId);

    // 从分类中移除
    this.adminClients.delete(socketId);
    this.pluginClients.delete(socketId);
    this.adminPanelClients.delete(socketId);

    // 从site索引中移除
    if (clientInfo.siteId) {
      this.siteClients.delete(clientInfo.siteId);
      // 更新站点状态为离线
      this.siteManager.updateSiteStatus(clientInfo.siteId, 'offline');
    }

    // 清除心跳定时器
    this._stopHeartbeatCheck(socketId);

    logger.info(`Client removed: ${socketId}`, {
      type: clientInfo.type,
      siteId: clientInfo.siteId,
    });

    // 广播客户端断开事件
    this._broadcastClientEvent('client_disconnected', clientInfo);

    return true;
  }

  /**
   * 获取客户端信息
   */
  getClient(socketId) {
    return this.clients.get(socketId);
  }

  /**
   * 根据siteId获取客户端
   */
  getClientBySiteId(siteId) {
    const socketId = this.siteClients.get(siteId);
    if (!socketId) {
      return null;
    }
    return this.clients.get(socketId);
  }

  /**
   * 检查站点是否在线
   */
  isSiteOnline(siteId) {
    return this.siteClients.has(siteId);
  }

  /**
   * 获取所有在线站点
   */
  getOnlineSites() {
    const sites = [];
    for (const [siteId, socketId] of this.siteClients) {
      const client = this.clients.get(socketId);
      if (client) {
        sites.push({
          siteId,
          socketId,
          connectedAt: client.connectedAt,
          lastHeartbeat: client.lastHeartbeat,
        });
      }
    }
    return sites;
  }

  /**
   * 获取所有客户端
   */
  getAllClients() {
    return Array.from(this.clients.values());
  }

  /**
   * 获取客户端数量统计
   */
  getStats() {
    return {
      total: this.clients.size,
      admin: this.adminClients.size,
      plugin: this.pluginClients.size,
      adminPanel: this.adminPanelClients.size,
      onlineSites: this.siteClients.size,
    };
  }

  /**
   * 处理心跳
   */
  handleHeartbeat(socketId) {
    const client = this.clients.get(socketId);
    if (client) {
      client.lastHeartbeat = new Date();
      client.missedHeartbeats = 0;
      return true;
    }
    return false;
  }

  /**
   * 启动心跳检查
   */
  _startHeartbeatCheck(socketId) {
    const timer = setInterval(() => {
      const client = this.clients.get(socketId);
      if (!client) {
        this._stopHeartbeatCheck(socketId);
        return;
      }

      const now = new Date();
      const timeSinceLastHeartbeat = now - client.lastHeartbeat;

      if (timeSinceLastHeartbeat > config.heartbeat.timeout) {
        client.missedHeartbeats++;
        
        if (client.missedHeartbeats >= config.heartbeat.maxMissed) {
          logger.warn(`Client heartbeat timeout: ${socketId}`);
          // 断开连接
          if (client.socket) {
            client.socket.disconnect(true);
          }
        }
      }
    }, config.heartbeat.interval);

    this.heartbeatTimers.set(socketId, timer);
  }

  /**
   * 停止心跳检查
   */
  _stopHeartbeatCheck(socketId) {
    const timer = this.heartbeatTimers.get(socketId);
    if (timer) {
      clearInterval(timer);
      this.heartbeatTimers.delete(socketId);
    }
  }

  /**
   * 广播客户端事件到管理面板
   */
  _broadcastClientEvent(eventName, clientInfo) {
    // 通知所有管理面板客户端
    for (const socketId of this.adminPanelClients) {
      const client = this.clients.get(socketId);
      if (client && client.socket) {
        client.socket.emit(eventName, {
          socketId: clientInfo.socketId,
          type: clientInfo.type,
          siteId: clientInfo.siteId,
          username: clientInfo.username,
          connectedAt: clientInfo.connectedAt,
        });
      }
    }
  }

  /**
   * 向指定站点发送消息
   */
  sendToSite(siteId, event, data) {
    const client = this.getClientBySiteId(siteId);
    if (client && client.socket) {
      client.socket.emit(event, data);
      return true;
    }
    return false;
  }

  /**
   * 向所有管理端发送消息
   */
  sendToAdmins(event, data) {
    let count = 0;
    for (const socketId of this.adminClients) {
      const client = this.clients.get(socketId);
      if (client && client.socket) {
        client.socket.emit(event, data);
        count++;
      }
    }
    return count;
  }

  /**
   * 向所有管理面板发送消息
   */
  sendToAdminPanels(event, data) {
    let count = 0;
    for (const socketId of this.adminPanelClients) {
      const client = this.clients.get(socketId);
      if (client && client.socket) {
        client.socket.emit(event, data);
        count++;
      }
    }
    return count;
  }

  /**
   * 向所有插件端发送消息（广播）
   */
  broadcastToPlugins(event, data) {
    let count = 0;
    for (const socketId of this.pluginClients) {
      const client = this.clients.get(socketId);
      if (client && client.socket) {
        client.socket.emit(event, data);
        count++;
      }
    }
    return count;
  }

  /**
   * 向分组内的站点发送消息
   */
  sendToGroup(groupId, event, data) {
    // 需要先获取该分组的所有站点
    const sites = this.siteManager.listSites({ groupId, pageSize: 1000 });
    if (!sites.success) {
      return 0;
    }

    let count = 0;
    for (const site of sites.sites) {
      if (this.sendToSite(site.site_id, event, data)) {
        count++;
      }
    }
    return count;
  }
}

// 单例实例
let instance = null;

function getClientManager() {
  if (!instance) {
    instance = new ClientManager();
  }
  return instance;
}

module.exports = {
  ClientManager,
  getClientManager,
};
