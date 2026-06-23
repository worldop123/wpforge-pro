import api from './index'

// 获取SEO概览统计
export function getSEOOverview() {
  return api.get('/seo/overview')
}

// 获取页面收录数据
export function getIndexingData(params?: {
  site_id?: number;
  limit?: number;
}) {
  return api.get('/seo/indexing', { params })
}

// SEO审计
export function auditSEO(data: {
  url: string;
  html_content?: string;
  target_keywords?: string[];
}) {
  return api.post('/seo/audit', data)
}

// SEO优化
export function optimizeSEO(data: {
  content: string;
  target_keywords: string[];
  language?: string;
  optimize_type?: string;
}) {
  return api.post('/seo/optimize', data)
}

// 生成SEO标题
export function generateSEOTitle(
  content: string,
  keywords: string,
  language?: string,
  max_length?: number
) {
  return api.post('/seo/generate-title', null, {
    params: { content, keywords, language, max_length }
  })
}

// 生成Meta描述
export function generateMetaDescription(
  content: string,
  keywords: string,
  language?: string,
  max_length?: number
) {
  return api.post('/seo/generate-description', null, {
    params: { content, keywords, language, max_length }
  })
}

// 获取Schema类型
export function getSchemaTypes() {
  return api.get('/seo/schema-types')
}

// 生成Schema
export function generateSchema(schema_type: string, data: any) {
  return api.post('/seo/generate-schema', null, {
    params: { schema_type },
    data
  })
}

// 获取SEO检查清单
export function getSEOChecklist() {
  return api.get('/seo/checklist')
}
