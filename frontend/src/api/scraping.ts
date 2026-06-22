import api from './index'

// 开始采集
export function startScraping(data: {
  url: string;
  site_id?: number;
  max_products?: number;
  auto_translate?: boolean;
  auto_import?: boolean;
  target_language?: string;
  proxy_enabled?: boolean;
  scrape_images?: boolean;
  scrape_variations?: boolean;
  scrape_reviews?: boolean;
}) {
  return api.post('/scraping/start', data)
}

// 分析网站
export function analyzeSite(url: string) {
  return api.post('/scraping/analyze', { url })
}

// 获取采集状态
export function getScrapingStatus(taskId: number) {
  return api.get(`/scraping/status/${taskId}`)
}

// 快速采集
export function quickScrape(url: string) {
  return api.post('/scraping/quick', { url })
}

// 停止采集
export function stopScraping(taskId: number) {
  return api.post(`/scraping/stop/${taskId}`)
}

// 获取采集历史
export function getScrapingHistory(params?: { page?: number; page_size?: number }) {
  return api.get('/scraping/history', { params })
}

// 获取采集配置
export function getScrapingConfig() {
  return api.get('/scraping/config')
}

// 更新采集配置
export function updateScrapingConfig(data: any) {
  return api.put('/scraping/config', data)
}
