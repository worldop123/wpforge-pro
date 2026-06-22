import api from './index'

// 翻译文本
export function translateText(data: {
  text: string;
  source_language?: string;
  target_language: string;
  engine?: string;
  polish?: boolean;
}) {
  return api.post('/translation/translate', data)
}

// 批量翻译
export function batchTranslate(data: {
  texts: string[];
  source_language?: string;
  target_language: string;
  engine?: string;
  polish?: boolean;
}) {
  return api.post('/translation/batch-translate', data)
}

// 翻译产品
export function translateProducts(data: {
  product_ids: number[];
  source_language?: string;
  target_language: string;
  engine?: string;
  polish?: boolean;
  fields?: string[];
}) {
  return api.post('/translation/translate-products', data)
}

// 获取翻译引擎列表
export function getTranslationEngines() {
  return api.get('/translation/engines')
}

// 获取支持的语言
export function getSupportedLanguages() {
  return api.get('/translation/languages')
}

// 获取术语库
export function getTerminology(params?: { page?: number; page_size?: number; keyword?: string }) {
  return api.get('/translation/terminology', { params })
}

// 添加术语
export function addTerminology(data: {
  source_term: string;
  target_term: string;
  source_language: string;
  target_language: string;
  category?: string;
}) {
  return api.post('/translation/terminology', data)
}

// 获取翻译历史
export function getTranslationHistory(params?: { page?: number; page_size?: number }) {
  return api.get('/translation/history', { params })
}

// 获取翻译统计
export function getTranslationStats() {
  return api.get('/translation/stats')
}
