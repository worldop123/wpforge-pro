<template>
  <div class="seo-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>SEO工具</h2>
          <p class="subtitle">页面SEO分析、内容优化、速度优化</p>
        </div>
      </div>
    </el-card>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="SEO分析" name="analyze">
        <el-card class="tool-card">
          <el-form :model="analyzeForm" label-width="100px">
            <el-form-item label="页面URL">
              <el-input v-model="analyzeForm.url" placeholder="https://example.com/page" />
            </el-form-item>
            <el-form-item label="目标关键词">
              <el-input v-model="analyzeForm.keywords" placeholder="多个关键词用逗号分隔" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doAnalyze" :loading="analyzing">
                开始分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-if="analysisResult" class="result-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>分析结果</span>
              <el-tag :type="getScoreTag(analysisResult.overall_score)" size="large">
                综合得分: {{ analysisResult.overall_score }}
              </el-tag>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="score-item">
                <div class="score-label">内容分数</div>
                <div class="score-value" :class="getScoreClass(analysisResult.content_score)">
                  {{ analysisResult.content_score }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="score-item">
                <div class="score-label">技术分数</div>
                <div class="score-value" :class="getScoreClass(analysisResult.technical_score)">
                  {{ analysisResult.technical_score }}
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="score-item">
                <div class="score-label">性能分数</div>
                <div class="score-value" :class="getScoreClass(analysisResult.performance_score)">
                  {{ analysisResult.performance_score }}
                </div>
              </div>
            </el-col>
          </el-row>

          <el-divider />

          <h4>发现的问题</h4>
          <el-table :data="analysisResult.issues" style="width: 100%">
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="描述" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="内容生成" name="generate">
        <el-card class="tool-card">
          <el-form :model="generateForm" label-width="100px">
            <el-form-item label="内容摘要">
              <el-input v-model="generateForm.content" type="textarea" :rows="4" placeholder="输入内容摘要" />
            </el-form-item>
            <el-form-item label="关键词">
              <el-input v-model="generateForm.keywords" placeholder="多个关键词用逗号分隔" />
            </el-form-item>
            <el-form-item label="语言">
              <el-select v-model="generateForm.language" style="width: 200px">
                <el-option label="中文" value="zh-CN" />
                <el-option label="英语" value="en" />
                <el-option label="匈牙利语" value="hu" />
                <el-option label="罗马尼亚语" value="ro" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="generateTitle">生成标题</el-button>
              <el-button type="success" @click="generateDescription">生成描述</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-if="generatedResult" class="result-card" style="margin-top: 20px;">
          <template #header>
            <span>生成结果</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="SEO标题">
              {{ generatedResult.title }}
            </el-descriptions-item>
            <el-descriptions-item label="Meta描述">
              {{ generatedResult.description }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="速度优化" name="speed">
        <el-card class="tool-card">
          <template #header>
            <span>速度优化建议</span>
          </template>
          <div class="optimization-list">
            <div v-for="item in speedSuggestions" :key="item.title" class="optimization-item">
              <div class="opt-header">
                <el-tag :type="getPriorityTag(item.priority)" size="small">{{ item.priority }}</el-tag>
                <span class="opt-title">{{ item.title }}</span>
              </div>
              <p class="opt-desc">{{ item.description }}</p>
              <div class="opt-tools">
                推荐工具: {{ item.tools.join(', ') }}
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="检查清单" name="checklist">
        <el-card class="tool-card">
          <template #header>
            <span>SEO检查清单</span>
          </template>
          <el-collapse>
            <el-collapse-item title="页面SEO" name="on_page">
              <el-checkbox-group v-model="checkedOnPage">
                <div v-for="item in checklist.on_page" :key="item.item" class="check-item">
                  <el-checkbox :label="item.item" />
                  <span class="check-desc">{{ item.description }}</span>
                </div>
              </el-checkbox-group>
            </el-collapse-item>
            <el-collapse-item title="技术SEO" name="technical">
              <el-checkbox-group v-model="checkedTechnical">
                <div v-for="item in checklist.technical" :key="item.item" class="check-item">
                  <el-checkbox :label="item.item" />
                  <span class="check-desc">{{ item.description }}</span>
                </div>
              </el-checkbox-group>
            </el-collapse-item>
            <el-collapse-item title="性能优化" name="performance">
              <el-checkbox-group v-model="checkedPerformance">
                <div v-for="item in checklist.performance" :key="item.item" class="check-item">
                  <el-checkbox :label="item.item" />
                  <span class="check-desc">{{ item.description }}</span>
                </div>
              </el-checkbox-group>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('analyze')
const analyzing = ref(false)

const analyzeForm = reactive({
  url: '',
  keywords: ''
})

const analysisResult = ref<any>(null)

const generateForm = reactive({
  content: '',
  keywords: '',
  language: 'zh-CN'
})

const generatedResult = ref<any>(null)

const speedSuggestions = ref([
  { category: 'images', title: '图片压缩与WebP格式', description: '压缩图片并转换为WebP格式可以显著减少图片大小，加快加载速度', priority: 'high', tools: ['WPForge Image Optimizer', 'ShortPixel', 'Smush'] },
  { category: 'caching', title: '配置页面缓存', description: '启用页面缓存可以大幅减少服务器响应时间，提升访问速度', priority: 'high', tools: ['WP Rocket', 'W3 Total Cache', 'LiteSpeed Cache'] },
  { category: 'cdn', title: '配置CDN加速', description: '使用CDN分发静态资源，减少延迟，提升全球访问速度', priority: 'high', tools: ['Cloudflare', 'StackPath', 'KeyCDN'] },
  { category: 'lazyload', title: '图片懒加载', description: '延迟加载视窗外的图片，加快首屏加载速度', priority: 'medium', tools: ['原生loading属性', 'Lazy Load插件'] },
  { category: 'database', title: '数据库优化', description: '清理修订版本、垃圾评论、过期瞬态等，优化数据库性能', priority: 'medium', tools: ['WP-Optimize', 'WP-Sweep'] },
  { category: 'compression', title: '启用GZIP/Brotli压缩', description: '压缩文本资源可以减少传输大小，加快加载速度', priority: 'medium', tools: ['.htaccess配置', 'Nginx配置', 'CDN配置'] }
])

const checklist = reactive({
  on_page: [
    { item: '标题标签（Title Tag）', description: '每个页面有唯一的、包含关键词的标题，30-60字符', priority: 'high' },
    { item: 'Meta描述', description: '每个页面有吸引人的meta描述，70-160字符', priority: 'high' },
    { item: 'H1标题', description: '每个页面只有一个H1，包含主要关键词', priority: 'high' },
    { item: '标题层级', description: 'H1-H6层级清晰，不跳级', priority: 'medium' },
    { item: '图片Alt属性', description: '所有图片有描述性的alt属性', priority: 'medium' },
    { item: '内容质量', description: '内容有价值、全面，至少300字以上', priority: 'high' },
    { item: '关键词密度', description: '主要关键词密度1%-2%，自然融入', priority: 'medium' },
    { item: '内部链接', description: '有相关的内部链接，锚文本描述性', priority: 'medium' },
    { item: 'URL结构', description: 'URL简洁、包含关键词、静态化', priority: 'high' }
  ],
  technical: [
    { item: '页面加载速度', description: '页面加载时间<3秒，Core Web Vitals达标', priority: 'high' },
    { item: '移动端友好', description: '响应式设计，移动端体验良好', priority: 'high' },
    { item: 'HTTPS', description: '全站启用HTTPS', priority: 'high' },
    { item: 'XML Sitemap', description: '有XML网站地图并提交给搜索引擎', priority: 'medium' },
    { item: 'robots.txt', description: '正确配置robots.txt', priority: 'medium' },
    { item: 'Canonical标签', description: '避免重复内容问题', priority: 'medium' },
    { item: '结构化数据', description: '添加Schema.org结构化数据', priority: 'medium' }
  ],
  performance: [
    { item: '图片优化', description: '图片压缩、WebP格式、懒加载', priority: 'high' },
    { item: '缓存配置', description: '页面缓存、浏览器缓存', priority: 'high' },
    { item: 'CDN加速', description: '使用CDN分发静态资源', priority: 'high' },
    { item: 'GZIP/Brotli压缩', description: '启用文本资源压缩', priority: 'medium' },
    { item: '数据库优化', description: '清理冗余数据，优化查询', priority: 'medium' },
    { item: '字体优化', description: '字体预加载、子集化', priority: 'low' }
  ]
})

const checkedOnPage = ref<string[]>([])
const checkedTechnical = ref<string[]>([])
const checkedPerformance = ref<string[]>([])

const getScoreTag = (score: number) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const getScoreClass = (score: number) => {
  if (score >= 80) return 'score-good'
  if (score >= 60) return 'score-medium'
  return 'score-poor'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    'error': 'danger',
    'warning': 'warning',
    'info': 'info'
  }
  return map[severity] || ''
}

const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return map[priority] || ''
}

const doAnalyze = () => {
  if (!analyzeForm.url) {
    ElMessage.warning('请输入页面URL')
    return
  }
  
  analyzing.value = true
  
  // 模拟分析
  setTimeout(() => {
    analysisResult.value = {
      overall_score: 75,
      content_score: 80,
      technical_score: 70,
      performance_score: 72,
      title: '示例页面标题',
      description: '示例页面描述',
      issues: [
        { type: 'title', severity: 'warning', message: '标题过短: 25字符，建议30-60字符' },
        { type: 'description', severity: 'error', message: '缺少meta description' },
        { type: 'images', severity: 'warning', message: '有5张图片缺少alt属性' },
        { type: 'content', severity: 'info', message: '内容一般: 450字，建议1000字以上效果更好' },
        { type: 'canonical', severity: 'warning', message: '缺少canonical标签' }
      ]
    }
    analyzing.value = false
  }, 2000)
}

const generateTitle = () => {
  if (!generateForm.content || !generateForm.keywords) {
    ElMessage.warning('请输入内容摘要和关键词')
    return
  }
  
  generatedResult.value = {
    ...generatedResult.value,
    title: '最佳电子烟产品推荐 - 2024年专业评测 | BangVape'
  }
  ElMessage.success('标题生成成功')
}

const generateDescription = () => {
  if (!generateForm.content || !generateForm.keywords) {
    ElMessage.warning('请输入内容摘要和关键词')
    return
  }
  
  generatedResult.value = {
    ...generatedResult.value,
    description: 'BangVape提供精选电子烟产品，专业评测各类 vape 设备和烟油，为您推荐最适合的电子烟产品。'
  }
  ElMessage.success('描述生成成功')
}
</script>

<style scoped>
.seo-page {
  padding: 0;
}

.page-header-card {
  margin-bottom: 20px;
  border: none;
  border-radius: 8px;
}

.page-header h2 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #1f2937;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.tool-card,
.result-card {
  border: none;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-item {
  text-align: center;
  padding: 20px;
}

.score-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
}

.score-good {
  color: #10b981;
}

.score-medium {
  color: #f59e0b;
}

.score-poor {
  color: #ef4444;
}

.optimization-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.optimization-item {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.opt-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.opt-title {
  font-weight: 600;
  color: #1f2937;
}

.opt-desc {
  margin: 0 0 8px;
  color: #6b7280;
  font-size: 14px;
}

.opt-tools {
  font-size: 12px;
  color: #9ca3af;
}

.check-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
}

.check-desc {
  font-size: 13px;
  color: #6b7280;
}
</style>
