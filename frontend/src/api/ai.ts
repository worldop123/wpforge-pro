import api from './index'

// AI对话
export function aiChat(data: {
  message: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  history?: Array<{ role: string; content: string }>;
}) {
  return api.post('/ai/chat', data)
}

// AI分析网站
export function aiAnalyzeSite(data: {
  url: string;
  analysis_type?: string;
}) {
  return api.post('/ai/analyze-site', data)
}

// 获取可用模型
export function getAvailableModels() {
  return api.get('/ai/models')
}

// AI生成内容
export function aiGenerateContent(
  prompt: string,
  content_type?: string,
  language?: string,
  length?: string
) {
  return api.post('/ai/generate-content', null, {
    params: { prompt, content_type, language, length }
  })
}

// AI改写内容
export function aiRewriteContent(
  content: string,
  style?: string,
  language?: string
) {
  return api.post('/ai/rewrite-content', null, {
    params: { content, style, language }
  })
}

// AI分析内容
export function aiAnalyzeContent(
  content: string,
  analysis_type?: string
) {
  return api.post('/ai/analyze-content', null, {
    params: { content, analysis_type }
  })
}

// 获取AI提供商
export function getAIProviders() {
  return api.get('/ai/providers')
}
