import api from './index'

// 获取代理服务商列表
export function getProxyProviders() {
  return api.get('/proxy/providers')
}

// 获取代理池统计
export function getProxyPoolStats() {
  return api.get('/proxy/pool/stats')
}

// 添加代理
export function addProxy(data: {
  host: string;
  port: number;
  protocol?: string;
  username?: string;
  password?: string;
  country?: string;
  provider?: string;
}) {
  return api.post('/proxy/add', null, { params: data })
}

// 批量添加代理
export function batchAddProxies(proxies: any[]) {
  return api.post('/proxy/batch-add', proxies)
}

// 检测代理可用性
export function checkProxies() {
  return api.post('/proxy/check')
}

// 获取代理列表
export function listProxies(params?: {
  country?: string;
  protocol?: string;
  status?: string;
}) {
  return api.get('/proxy/list', { params })
}

// 移除代理
export function removeProxy(proxy_id: number) {
  return api.delete(`/proxy/${proxy_id}`)
}

// 获取代理选择策略
export function getProxyStrategies() {
  return api.get('/proxy/strategies')
}

// 获取支持的国家列表
export function getSupportedCountries() {
  return api.get('/proxy/countries')
}
