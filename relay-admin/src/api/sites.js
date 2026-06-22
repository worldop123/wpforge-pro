import request from './request'

// 获取站点列表
export function getSites(params = {}) {
  return request.get('/sites', { params })
}

// 获取站点详情
export function getSite(siteId) {
  return request.get(`/sites/${siteId}`)
}

// 注册站点
export function registerSite(data) {
  return request.post('/sites/register', data)
}

// 更新站点
export function updateSite(siteId, data) {
  return request.put(`/sites/${siteId}`, data)
}

// 删除站点
export function deleteSite(siteId) {
  return request.delete(`/sites/${siteId}`)
}

// 重新生成Token
export function regenerateToken(siteId) {
  return request.post(`/sites/${siteId}/regenerate-token`)
}

// 获取分组列表
export function getGroups() {
  return request.get('/groups')
}

// 创建分组
export function createGroup(data) {
  return request.post('/groups', data)
}

// 获取标签列表
export function getTags() {
  return request.get('/tags')
}

// 创建标签
export function createTag(data) {
  return request.post('/tags', data)
}

// 获取统计信息
export function getStats() {
  return request.get('/stats')
}

// 获取消息历史
export function getMessageHistory(params = {}) {
  return request.get('/messages/history', { params })
}

export default {
  getSites,
  getSite,
  registerSite,
  updateSite,
  deleteSite,
  regenerateToken,
  getGroups,
  createGroup,
  getTags,
  createTag,
  getStats,
  getMessageHistory
}
