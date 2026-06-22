/**
 * API路由
 * 
 * 提供REST API接口供管理面板使用
 */

const express = require('express');
const router = express.Router();

const { getAuthManager } = require('../auth/AuthManager');
const { getSQLiteDB } = require('../storage/SQLiteDB');

const authManager = getAuthManager();
const sqliteDB = getSQLiteDB();

// 认证中间件
function authenticateAPI(req, res, next) {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' });
  }

  try {
    const admin = authManager.verifyAdminApiKey(apiKey);
    if (!admin) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
    req.admin = admin;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Authentication failed' });
  }
}

// 管理员登录
router.post('/auth/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password required' });
    }

    const result = await authManager.adminLogin(username, password);
    
    if (!result.success) {
      return res.status(401).json({ error: result.message || 'Invalid credentials' });
    }

    res.json({
      success: true,
      token: result.token,
      user: result.user,
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 获取站点列表
router.get('/sites', authenticateAPI, async (req, res) => {
  try {
    const { status, group_id, search, page = 1, page_size = 20 } = req.query;
    
    let query = 'SELECT * FROM sites WHERE 1=1';
    const params = [];

    if (status) {
      query += ' AND status = ?';
      params.push(status);
    }

    if (group_id) {
      query += ' AND group_id = ?';
      params.push(group_id);
    }

    if (search) {
      query += ' AND (site_name LIKE ? OR site_url LIKE ? OR site_id LIKE ?)';
      const searchPattern = `%${search}%`;
      params.push(searchPattern, searchPattern, searchPattern);
    }

    // 总数
    const countResult = await sqliteDB.queryOne(
      `SELECT COUNT(*) as total FROM (${query})`,
      params
    );

    // 分页
    const offset = (page - 1) * page_size;
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(parseInt(page_size), offset);

    const sites = await sqliteDB.query(query, params);

    res.json({
      sites,
      total: countResult.total,
      page: parseInt(page),
      page_size: parseInt(page_size),
      total_pages: Math.ceil(countResult.total / page_size),
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 获取站点详情
router.get('/sites/:siteId', authenticateAPI, async (req, res) => {
  try {
    const { siteId } = req.params;
    
    const site = await sqliteDB.queryOne(
      'SELECT * FROM sites WHERE site_id = ?',
      [siteId]
    );

    if (!site) {
      return res.status(404).json({ error: 'Site not found' });
    }

    res.json(site);
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 注册站点
router.post('/sites', authenticateAPI, async (req, res) => {
  try {
    const { site_name, site_url, group_id, metadata } = req.body;
    
    if (!site_name) {
      return res.status(400).json({ error: 'Site name required' });
    }

    // 生成站点ID和Token
    const siteId = `site_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const token = authManager.generateSiteToken();

    await sqliteDB.execute(
      `INSERT INTO sites (site_id, site_name, site_url, token, group_id, status, metadata, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        siteId,
        site_name,
        site_url || '',
        token,
        group_id || null,
        'offline',
        JSON.stringify(metadata || {}),
        new Date().toISOString(),
        new Date().toISOString(),
      ]
    );

    res.status(201).json({
      site_id: siteId,
      site_name,
      site_url,
      token,
      group_id,
      status: 'offline',
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 更新站点
router.put('/sites/:siteId', authenticateAPI, async (req, res) => {
  try {
    const { siteId } = req.params;
    const { site_name, site_url, group_id, status, metadata } = req.body;

    const site = await sqliteDB.queryOne(
      'SELECT * FROM sites WHERE site_id = ?',
      [siteId]
    );

    if (!site) {
      return res.status(404).json({ error: 'Site not found' });
    }

    const updates = [];
    const params = [];

    if (site_name !== undefined) {
      updates.push('site_name = ?');
      params.push(site_name);
    }
    if (site_url !== undefined) {
      updates.push('site_url = ?');
      params.push(site_url);
    }
    if (group_id !== undefined) {
      updates.push('group_id = ?');
      params.push(group_id);
    }
    if (status !== undefined) {
      updates.push('status = ?');
      params.push(status);
    }
    if (metadata !== undefined) {
      updates.push('metadata = ?');
      params.push(JSON.stringify(metadata));
    }

    if (updates.length > 0) {
      updates.push('updated_at = ?');
      params.push(new Date().toISOString());
      params.push(siteId);

      await sqliteDB.execute(
        `UPDATE sites SET ${updates.join(', ')} WHERE site_id = ?`,
        params
      );
    }

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 删除站点
router.delete('/sites/:siteId', authenticateAPI, async (req, res) => {
  try {
    const { siteId } = req.params;

    const result = await sqliteDB.execute(
      'DELETE FROM sites WHERE site_id = ?',
      [siteId]
    );

    if (result.changes === 0) {
      return res.status(404).json({ error: 'Site not found' });
    }

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 重新生成站点Token
router.post('/sites/:siteId/regenerate-token', authenticateAPI, async (req, res) => {
  try {
    const { siteId } = req.params;

    const site = await sqliteDB.queryOne(
      'SELECT * FROM sites WHERE site_id = ?',
      [siteId]
    );

    if (!site) {
      return res.status(404).json({ error: 'Site not found' });
    }

    const newToken = authManager.generateSiteToken();

    await sqliteDB.execute(
      'UPDATE sites SET token = ?, updated_at = ? WHERE site_id = ?',
      [newToken, new Date().toISOString(), siteId]
    );

    res.json({
      site_id: siteId,
      token: newToken,
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 获取统计数据
router.get('/stats', authenticateAPI, async (req, res) => {
  try {
    // 站点统计
    const siteStats = await sqliteDB.queryOne(
      `SELECT 
        COUNT(*) as total_sites,
        SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online_sites,
        SUM(CASE WHEN status = 'offline' THEN 1 ELSE 0 END) as offline_sites,
        SUM(CASE WHEN status = 'disabled' THEN 1 ELSE 0 END) as disabled_sites
       FROM sites`
    );

    // 消息统计（最近24小时）
    const messageStats = await sqliteDB.queryOne(
      `SELECT 
        COUNT(*) as total_messages,
        SUM(CASE WHEN message_type = 'event' THEN 1 ELSE 0 END) as event_messages,
        SUM(CASE WHEN message_type = 'command' THEN 1 ELSE 0 END) as command_messages,
        SUM(CASE WHEN message_type = 'response' THEN 1 ELSE 0 END) as response_messages
       FROM message_history 
       WHERE created_at > datetime('now', '-24 hours')`
    );

    // 离线消息统计
    const offlineStats = await sqliteDB.queryOne(
      `SELECT 
        COUNT(*) as total_offline,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_offline
       FROM offline_messages`
    );

    res.json({
      sites: siteStats,
      messages: messageStats,
      offline: offlineStats,
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 获取消息历史
router.get('/messages', authenticateAPI, async (req, res) => {
  try {
    const { type, source_id, target_id, page = 1, page_size = 50 } = req.query;
    
    let query = 'SELECT * FROM message_history WHERE 1=1';
    const params = [];

    if (type) {
      query += ' AND message_type = ?';
      params.push(type);
    }

    if (source_id) {
      query += ' AND source_id = ?';
      params.push(source_id);
    }

    if (target_id) {
      query += ' AND target_id = ?';
      params.push(target_id);
    }

    // 总数
    const countResult = await sqliteDB.queryOne(
      `SELECT COUNT(*) as total FROM (${query})`,
      params
    );

    // 分页
    const offset = (page - 1) * page_size;
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(parseInt(page_size), offset);

    const messages = await sqliteDB.query(query, params);

    res.json({
      messages,
      total: countResult.total,
      page: parseInt(page),
      page_size: parseInt(page_size),
      total_pages: Math.ceil(countResult.total / page_size),
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 获取分组列表
router.get('/groups', authenticateAPI, async (req, res) => {
  try {
    const groups = await sqliteDB.query(
      'SELECT * FROM site_groups ORDER BY name ASC'
    );

    res.json({ groups });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 创建分组
router.post('/groups', authenticateAPI, async (req, res) => {
  try {
    const { name, description } = req.body;
    
    if (!name) {
      return res.status(400).json({ error: 'Group name required' });
    }

    const groupId = `group_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    await sqliteDB.execute(
      `INSERT INTO site_groups (group_id, name, description, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?)`,
      [groupId, name, description || '', new Date().toISOString(), new Date().toISOString()]
    );

    res.status(201).json({
      group_id: groupId,
      name,
      description,
    });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

// 健康检查（公开）
router.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
});

module.exports = router;
