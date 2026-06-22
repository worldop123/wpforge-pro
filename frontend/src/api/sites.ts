import api from './index'

// 获取站点列表
export function getSites(params?: { page?: number; page_size?: number; keyword?: string }) {
  return api.get('/sites', { params })
}

// 获取站点详情
export function getSite(id: number) {
  return api.get(`/sites/${id}`)
}

// 创建站点
export function createSite(data: any) {
  return api.post('/sites', data)
}

// 更新站点
export function updateSite(id: number, data: any) {
  return api.put(`/sites/${id}`, data)
}

// 删除站点
export function deleteSite(id: number) {
  return api.delete(`/sites/${id}`)
}

// 测试连接
export function testSiteConnection(id: number) {
  return api.post(`/sites/${id}/test-connection`)
}

// 获取站点统计
export function getSiteStats(id: number) {
  return api.get(`/sites/${id}/stats`)
}

// 同步站点
export function syncSite(id: number) {
  return api.post(`/sites/${id}/sync`)
}
