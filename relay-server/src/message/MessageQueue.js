/**
 * WPForge Relay Server - 消息队列
 * 
 * 管理离线消息、消息持久化、过期清理等
 */

const { v4: uuidv4 } = require('uuid');
const config = require('../config');
const { createLogger } = require('../utils/logger');
const { getSQLiteDB } = require('../storage/SQLiteDB');
const { getRedisClient } = require('../storage/RedisClient');

const logger = createLogger('MessageQueue');

class MessageQueue {
  constructor() {
    this.db = getSQLiteDB();
    this.redis = getRedisClient();
    this._startCleanupJob();
  }

  /**
   * 生成消息ID
   */
  generateMessageId() {
    return `msg_${uuidv4().replace(/-/g, '')}`;
  }

  /**
   * 保存离线消息
   */
  async saveOfflineMessage(message) {
    try {
      const {
        messageId,
        targetId,
        sourceId,
        messageType,
        content,
        priority = 'normal',
      } = message;

      const expiresAt = new Date(Date.now() + config.message.ttl * 1000).toISOString();
      const contentStr = typeof content === 'string' ? content : JSON.stringify(content);

      // 保存到SQLite
      this.db.execute(
        `INSERT INTO offline_messages 
         (message_id, target_id, source_id, message_type, content, priority, status, expires_at)
         VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)`,
        [messageId, targetId, sourceId, messageType, contentStr, priority, expiresAt]
      );

      // 同时保存到Redis（用于快速访问）
      const redisKey = `offline:${targetId}`;
      await this.redis.lPush(redisKey, JSON.stringify({
        messageId,
        sourceId,
        messageType,
        content,
        priority,
        createdAt: new Date().toISOString(),
      }));
      await this.redis.expire(redisKey, config.message.ttl);

      logger.debug(`Offline message saved: ${messageId} -> ${targetId}`);
      return true;
    } catch (err) {
      logger.error('Error saving offline message:', err);
      return false;
    }
  }

  /**
   * 获取目标的离线消息
   */
  async getOfflineMessages(targetId, limit = 100) {
    try {
      // 先尝试从Redis获取
      const redisKey = `offline:${targetId}`;
      const redisMessages = await this.redis.lRange(redisKey, 0, limit - 1);
      
      if (redisMessages && redisMessages.length > 0) {
        return redisMessages.map(msg => JSON.parse(msg));
      }

      // Redis中没有，从SQLite获取
      const messages = this.db.query(
        `SELECT message_id as messageId, source_id as sourceId, 
                message_type as messageType, content, priority, created_at as createdAt
         FROM offline_messages 
         WHERE target_id = ? AND status = 'pending'
         ORDER BY 
           CASE priority 
             WHEN 'urgent' THEN 1 
             WHEN 'high' THEN 2 
             WHEN 'normal' THEN 3 
             WHEN 'low' THEN 4 
           END,
           created_at ASC
         LIMIT ?`,
        [targetId, limit]
      );

      // 解析content
      for (const msg of messages) {
        try {
          msg.content = JSON.parse(msg.content);
        } catch (e) {
          // content可能已经是字符串
        }
      }

      return messages;
    } catch (err) {
      logger.error('Error getting offline messages:', err);
      return [];
    }
  }

  /**
   * 标记消息为已送达
   */
  async markAsDelivered(messageId) {
    try {
      this.db.execute(
        "UPDATE offline_messages SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP WHERE message_id = ?",
        [messageId]
      );
      return true;
    } catch (err) {
      logger.error('Error marking message as delivered:', err);
      return false;
    }
  }

  /**
   * 清除目标的离线消息（Redis）
   */
  async clearOfflineCache(targetId) {
    try {
      const redisKey = `offline:${targetId}`;
      await this.redis.del(redisKey);
      return true;
    } catch (err) {
      logger.error('Error clearing offline cache:', err);
      return false;
    }
  }

  /**
   * 记录消息历史
   */
  async recordMessageHistory(message) {
    try {
      const {
        messageId,
        sourceId,
        targetId = null,
        messageType,
        content,
        status = 'sent',
      } = message;

      const contentStr = content ? 
        (typeof content === 'string' ? content : JSON.stringify(content)) : 
        null;

      this.db.execute(
        `INSERT INTO message_history 
         (message_id, source_id, target_id, message_type, content, status)
         VALUES (?, ?, ?, ?, ?, ?)`,
        [messageId, sourceId, targetId, messageType, contentStr, status]
      );

      return true;
    } catch (err) {
      logger.error('Error recording message history:', err);
      return false;
    }
  }

  /**
   * 查询消息历史
   */
  getMessageHistory(options = {}) {
    try {
      const {
        sourceId,
        targetId,
        messageType,
        page = 1,
        pageSize = 50,
        startDate,
        endDate,
      } = options;

      let whereClause = [];
      let params = [];

      if (sourceId) {
        whereClause.push('source_id = ?');
        params.push(sourceId);
      }

      if (targetId) {
        whereClause.push('target_id = ?');
        params.push(targetId);
      }

      if (messageType) {
        whereClause.push('message_type = ?');
        params.push(messageType);
      }

      if (startDate) {
        whereClause.push('created_at >= ?');
        params.push(startDate);
      }

      if (endDate) {
        whereClause.push('created_at <= ?');
        params.push(endDate);
      }

      const whereSql = whereClause.length > 0 ? `WHERE ${whereClause.join(' AND ')}` : '';

      // 获取总数
      const countResult = this.db.queryOne(
        `SELECT COUNT(*) as total FROM message_history ${whereSql}`,
        params
      );

      // 获取分页数据
      const offset = (page - 1) * pageSize;
      const messages = this.db.query(
        `SELECT message_id as messageId, source_id as sourceId, 
                target_id as targetId, message_type as messageType, 
                status, created_at as createdAt
         FROM message_history 
         ${whereSql}
         ORDER BY created_at DESC
         LIMIT ? OFFSET ?`,
        [...params, pageSize, offset]
      );

      return {
        success: true,
        messages,
        total: countResult.total,
        page,
        pageSize,
        totalPages: Math.ceil(countResult.total / pageSize),
      };
    } catch (err) {
      logger.error('Error getting message history:', err);
      return { success: false, error: err.message, messages: [], total: 0 };
    }
  }

  /**
   * 清理过期消息
   */
  _cleanupExpiredMessages() {
    try {
      const now = new Date().toISOString();
      
      // 删除过期的离线消息
      const result = this.db.execute(
        'DELETE FROM offline_messages WHERE expires_at < ?',
        [now]
      );
      
      if (result.changes > 0) {
        logger.info(`Cleaned up ${result.changes} expired offline messages`);
      }

      // 删除超过30天的历史消息
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
      const historyResult = this.db.execute(
        'DELETE FROM message_history WHERE created_at < ?',
        [thirtyDaysAgo]
      );
      
      if (historyResult.changes > 0) {
        logger.info(`Cleaned up ${historyResult.changes} old history messages`);
      }
    } catch (err) {
      logger.error('Error cleaning up expired messages:', err);
    }
  }

  /**
   * 启动清理任务
   */
  _startCleanupJob() {
    // 每小时清理一次
    setInterval(() => {
      this._cleanupExpiredMessages();
    }, 60 * 60 * 1000);

    logger.info('Message cleanup job started');
  }

  /**
   * 获取队列统计
   */
  getQueueStats() {
    try {
      const pendingCount = this.db.queryOne(
        "SELECT COUNT(*) as count FROM offline_messages WHERE status = 'pending'"
      ).count;
      
      const deliveredCount = this.db.queryOne(
        "SELECT COUNT(*) as count FROM offline_messages WHERE status = 'delivered'"
      ).count;
      
      const totalToday = this.db.queryOne(
        "SELECT COUNT(*) as count FROM message_history WHERE DATE(created_at) = DATE('now')"
      ).count;

      return {
        success: true,
        stats: {
          pendingMessages: pendingCount,
          deliveredMessages: deliveredCount,
          messagesToday: totalToday,
        },
      };
    } catch (err) {
      logger.error('Error getting queue stats:', err);
      return { success: false, error: err.message, stats: {} };
    }
  }
}

// 单例实例
let instance = null;

function getMessageQueue() {
  if (!instance) {
    instance = new MessageQueue();
  }
  return instance;
}

module.exports = {
  MessageQueue,
  getMessageQueue,
};
