import api from './index'

// 获取监控概览
export function getMonitoringOverview() {
  return api.get('/monitoring/overview')
}

// 获取采集趋势图表数据
export function getChartData(period: 'week' | 'month' | 'year' = 'week') {
  return api.get('/monitoring/chart-data', { params: { period } })
}

// 获取站点监控状态
export function getSiteMonitoringStatus(site_id: number) {
  return api.get(`/monitoring/sites/${site_id}/status`)
}

// 获取站点SSL状态
export function getSiteSSLStatus(site_id: number) {
  return api.get(`/monitoring/sites/${site_id}/ssl`)
}

// 获取告警列表
export function getAlerts(params?: {
  site_id?: number;
  severity?: string;
  limit?: number;
}) {
  return api.get('/monitoring/alerts', { params })
}

// 获取站点性能数据
export function getSitePerformance(site_id: number) {
  return api.get(`/monitoring/performance/${site_id}`)
}

// 获取监控设置
export function getMonitoringSettings() {
  return api.get('/monitoring/settings')
}

// 更新监控设置
export function updateMonitoringSettings(settings: any) {
  return api.post('/monitoring/settings', settings)
}

// 获取通知渠道
export function getNotificationChannels() {
  return api.get('/monitoring/notification-channels')
}
