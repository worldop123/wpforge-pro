/**
 * WPForge Relay Server - 认证管理器
 * 
 * 处理客户端认证、JWT验证、API Key验证、权限检查等
 */

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const config = require('../config');
const { createLogger } = require('../utils/logger');
const { getSQLiteDB } = require('../storage/SQLiteDB');

const logger = createLogger('AuthManager');

class AuthManager {
  constructor() {
    this.db = getSQLiteDB();
    this._initDefaultAdmin();
  }

  /**
   * 初始化默认管理员
   */
  _initDefaultAdmin() {
    try {
      const existingAdmin = this.db.queryOne('SELECT id FROM admins WHERE username = ?', ['admin']);
      if (!existingAdmin) {
        const passwordHash = bcrypt.hashSync('admin123', 10);
        this.db.execute(
          'INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)',
          ['admin', passwordHash, 'super_admin']
        );
        logger.info('Default admin user created');
      }
    } catch (err) {
      logger.error('Error initializing default admin:', err);
    }
  }

  /**
   * 生成站点Token
   */
  generateSiteToken() {
    return crypto.randomBytes(config.auth.tokenLength).toString('hex');
  }

  /**
   * 验证站点Token
   */
  verifySiteToken(siteId, token) {
    try {
      const site = this.db.queryOne(
        'SELECT id, site_id, token, status FROM sites WHERE site_id = ?',
        [siteId]
      );
      
      if (!site) {
        return { valid: false, error: 'Site not found' };
      }
      
      if (site.status === 'disabled') {
        return { valid: false, error: 'Site is disabled' };
      }
      
      if (site.token !== token) {
        return { valid: false, error: 'Invalid token' };
      }
      
      return { valid: true, site };
    } catch (err) {
      logger.error('Error verifying site token:', err);
      return { valid: false, error: 'Verification failed' };
    }
  }

  /**
   * 验证管理员API Key
   */
  verifyAdminApiKey(apiKey) {
    if (apiKey === config.auth.superAdminApiKey) {
      return {
        valid: true,
        role: config.permissionLevels.SUPER_ADMIN,
        username: 'super_admin',
      };
    }
    
    if (apiKey === config.auth.adminApiKey) {
      return {
        valid: true,
        role: config.permissionLevels.ADMIN,
        username: 'admin',
      };
    }
    
    return { valid: false, error: 'Invalid API key' };
  }

  /**
   * 管理员登录
   */
  adminLogin(username, password) {
    try {
      const admin = this.db.queryOne(
        'SELECT id, username, password_hash, role FROM admins WHERE username = ?',
        [username]
      );
      
      if (!admin) {
        return { success: false, error: 'Invalid credentials' };
      }
      
      const valid = bcrypt.compareSync(password, admin.password_hash);
      if (!valid) {
        return { success: false, error: 'Invalid credentials' };
      }
      
      const token = this.generateJwt({
        id: admin.id,
        username: admin.username,
        role: admin.role,
      });
      
      return {
        success: true,
        token,
        user: {
          id: admin.id,
          username: admin.username,
          role: admin.role,
        },
      };
    } catch (err) {
      logger.error('Error during admin login:', err);
      return { success: false, error: 'Login failed' };
    }
  }

  /**
   * 生成JWT
   */
  generateJwt(payload) {
    return jwt.sign(payload, config.jwt.secret, {
      expiresIn: config.jwt.expiresIn,
      issuer: config.jwt.issuer,
    });
  }

  /**
   * 验证JWT
   */
  verifyJwt(token) {
    try {
      const decoded = jwt.verify(token, config.jwt.secret, {
        issuer: config.jwt.issuer,
      });
      return { valid: true, payload: decoded };
    } catch (err) {
      if (err.name === 'TokenExpiredError') {
        return { valid: false, error: 'Token expired' };
      }
      return { valid: false, error: 'Invalid token' };
    }
  }

  /**
   * 检查权限
   */
  checkPermission(userRole, requiredRole) {
    const roleHierarchy = {
      [config.permissionLevels.SUPER_ADMIN]: 3,
      [config.permissionLevels.ADMIN]: 2,
      [config.permissionLevels.SITE]: 1,
    };
    
    const userLevel = roleHierarchy[userRole] || 0;
    const requiredLevel = roleHierarchy[requiredRole] || 0;
    
    return userLevel >= requiredLevel;
  }

  /**
   * 验证WebSocket连接
   */
  authenticateSocket(socket, next) {
    const { clientType, credentials } = socket.handshake.auth || {};
    
    if (!clientType) {
      return next(new Error('Client type required'));
    }
    
    let authResult;
    
    switch (clientType) {
      case config.clientTypes.PLUGIN:
        // 插件端使用siteId + token
        const { siteId, token } = credentials || {};
        if (!siteId || !token) {
          return next(new Error('Site ID and token required'));
        }
        authResult = this.verifySiteToken(siteId, token);
        if (!authResult.valid) {
          return next(new Error(authResult.error));
        }
        socket.clientData = {
          type: clientType,
          siteId: siteId,
          role: config.permissionLevels.SITE,
        };
        break;
      
      case config.clientTypes.ADMIN:
        // 管理端使用API Key
        const { apiKey } = credentials || {};
        if (!apiKey) {
          return next(new Error('API key required'));
        }
        authResult = this.verifyAdminApiKey(apiKey);
        if (!authResult.valid) {
          return next(new Error(authResult.error));
        }
        socket.clientData = {
          type: clientType,
          role: authResult.role,
          username: authResult.username,
        };
        break;
      
      case config.clientTypes.ADMIN_PANEL:
        // 管理面板使用JWT
        const { jwtToken } = credentials || {};
        if (!jwtToken) {
          return next(new Error('JWT token required'));
        }
        authResult = this.verifyJwt(jwtToken);
        if (!authResult.valid) {
          return next(new Error(authResult.error));
        }
        socket.clientData = {
          type: clientType,
          role: authResult.payload.role,
          userId: authResult.payload.id,
          username: authResult.payload.username,
        };
        break;
      
      default:
        return next(new Error('Invalid client type'));
    }
    
    logger.info(`Client authenticated: ${clientType}`, {
      siteId: socket.clientData.siteId,
      username: socket.clientData.username,
    });
    
    next();
  }

  /**
   * 检查IP是否在黑名单中
   */
  isIpBlacklisted(ip) {
    try {
      const result = this.db.queryOne(
        'SELECT id, expires_at FROM ip_blacklist WHERE ip_address = ?',
        [ip]
      );
      
      if (!result) {
        return false;
      }
      
      // 检查是否过期
      if (result.expires_at) {
        const expiresAt = new Date(result.expires_at);
        if (expiresAt < new Date()) {
          // 过期了，删除记录
          this.db.execute('DELETE FROM ip_blacklist WHERE id = ?', [result.id]);
          return false;
        }
      }
      
      return true;
    } catch (err) {
      logger.error('Error checking IP blacklist:', err);
      return false;
    }
  }

  /**
   * 添加IP到黑名单
   */
  addToBlacklist(ip, reason = '', duration = null) {
    try {
      const expiresAt = duration ? 
        new Date(Date.now() + duration * 1000).toISOString() : null;
      
      this.db.execute(
        'INSERT OR REPLACE INTO ip_blacklist (ip_address, reason, expires_at) VALUES (?, ?, ?)',
        [ip, reason, expiresAt]
      );
      
      logger.info(`IP ${ip} added to blacklist`, { reason, duration });
      return true;
    } catch (err) {
      logger.error('Error adding IP to blacklist:', err);
      return false;
    }
  }

  /**
   * 从黑名单移除IP
   */
  removeFromBlacklist(ip) {
    try {
      this.db.execute('DELETE FROM ip_blacklist WHERE ip_address = ?', [ip]);
      logger.info(`IP ${ip} removed from blacklist`);
      return true;
    } catch (err) {
      logger.error('Error removing IP from blacklist:', err);
      return false;
    }
  }

  /**
   * 哈希密码
   */
  hashPassword(password) {
    return bcrypt.hashSync(password, 10);
  }
}

// 单例实例
let instance = null;

function getAuthManager() {
  if (!instance) {
    instance = new AuthManager();
  }
  return instance;
}

module.exports = {
  AuthManager,
  getAuthManager,
};
