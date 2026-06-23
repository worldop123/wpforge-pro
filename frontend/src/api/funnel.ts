import api from './index'

// 漏斗概览数据
export function getFunnelOverview(params: {
  time_range?: string
  site_ids?: string
}) {
  return api.get('/funnel/overview', { params })
}

// 销售趋势
export function getFunnelSalesTrend(params: {
  time_range?: string
  period?: string
  site_ids?: string
}) {
  return api.get('/funnel/sales-trend', { params })
}

// 热销产品
export function getFunnelTopProducts(params: {
  time_range?: string
  order_by?: string
  limit?: number
  site_ids?: string
}) {
  return api.get('/funnel/top-products', { params })
}

// AI 洞察
export function getFunnelInsights(params: {
  time_range?: string
  site_ids?: string
}) {
  return api.get('/funnel/insights', { params })
}

// 站点对比
export function getFunnelComparison(params: {
  time_range?: string
  site_ids?: string
}) {
  return api.get('/funnel/comparison', { params })
}
