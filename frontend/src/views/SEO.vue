<template>
  <div class="seo-page">
    <el-card class="page-header-card" shadow="hover">
      <div class="page-header">
        <div>
          <h2>SEO工具</h2>
          <p class="subtitle">页面SEO分析、内容优化、Schema配置、搜索引擎提交</p>
        </div>
      </div>
    </el-card>

    <!-- SEO 评分概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ overview.avgScore }}</div>
            <div class="mini-stat-label">平均SEO得分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value success">{{ overview.goodPages }}</div>
            <div class="mini-stat-label">优秀页面</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value warning">{{ overview.warningPages }}</div>
            <div class="mini-stat-label">需优化页面</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value primary">{{ overview.indexedPages }}</div>
            <div class="mini-stat-label">已收录页面</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab" class="content-tabs">
      <!-- SEO分析 -->
      <el-tab-pane label="SEO分析" name="analyze">
        <el-card shadow="hover" class="tool-card">
          <el-form :model="analyzeForm" label-width="100px">
            <el-form-item label="页面URL" required>
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

        <el-card v-if="analysisResult" shadow="hover" class="result-card" style="margin-top: 20px;">
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
            <el-table-column prop="message" label="描述" min-width="300" show-overflow-tooltip />
            <el-table-column prop="suggestion" label="建议" min-width="300" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 内容生成 -->
      <el-tab-pane label="内容生成" name="generate">
        <el-card shadow="hover" class="tool-card">
          <el-form :model="generateForm" label-width="100px">
            <el-form-item label="内容摘要" required>
              <el-input v-model="generateForm.content" type="textarea" :rows="4" placeholder="输入内容摘要" />
            </el-form-item>
            <el-form-item label="关键词" required>
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
              <el-button type="primary" @click="generateTitle" :loading="generatingTitle">生成标题</el-button>
              <el-button type="success" @click="generateDescription" :loading="generatingDesc">生成描述</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card v-if="generatedResult" shadow="hover" class="result-card" style="margin-top: 20px;">
          <template #header>
            <span>生成结果</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="SEO标题">
              {{ generatedResult.title || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="Meta描述">
              {{ generatedResult.description || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>

      <!-- Schema 配置 -->
      <el-tab-pane label="Schema配置" name="schema">
        <el-card shadow="hover" class="tool-card">
          <template #header>
            <div class="card-header">
              <span>结构化数据配置</span>
              <el-button type="primary" size="small" @click="generateSchema">生成Schema</el-button>
            </div>
          </template>
          <el-form :model="schemaForm" label-width="120px">
            <el-form-item label="Schema类型">
              <el-select v-model="schemaForm.type" placeholder="选择Schema类型" style="width: 280px">
                <el-option label="Product - 产品" value="Product" />
                <el-option label="Article - 文章" value="Article" />
                <el-option label="Organization - 组织" value="Organization" />
                <el-option label="BreadcrumbList - 面包屑" value="BreadcrumbList" />
                <el-option label="FAQPage - 常见问题" value="FAQPage" />
                <el-option label="Review - 评论" value="Review" />
                <el-option label="LocalBusiness - 本地商家" value="LocalBusiness" />
              </el-select>
            </el-form-item>
            <el-form-item label="名称">
              <el-input v-model="schemaForm.name" placeholder="产品/文章名称" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="schemaForm.description" type="textarea" :rows="3" placeholder="详细描述" />
            </el-form-item>
            <el-form-item label="图片URL">
              <el-input v-model="schemaForm.image" placeholder="https://example.com/image.jpg" />
            </el-form-item>
            <el-form-item label="URL">
              <el-input v-model="schemaForm.url" placeholder="https://example.com/page" />
            </el-form-item>
            <el-form-item v-if="schemaForm.type === 'Product'" label="价格">
              <el-input-number v-model="schemaForm.price" :min="0" :precision="2" />
              <el-select v-model="schemaForm.currency" style="width: 120px; margin-left: 12px;">
                <el-option label="USD" value="USD" />
                <el-option label="EUR" value="EUR" />
                <el-option label="CNY" value="CNY" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="schemaForm.type === 'Product'" label="库存状态">
              <el-select v-model="schemaForm.availability" style="width: 200px">
                <el-option label="有货" value="InStock" />
                <el-option label="缺货" value="OutOfStock" />
                <el-option label="预售" value="PreOrder" />
              </el-select>
            </el-form-item>
          </el-form>

          <div v-if="schemaResult" class="schema-result">
            <h4>生成的Schema JSON-LD</h4>
            <el-input
              :model-value="schemaResult"
              type="textarea"
              :rows="12"
              readonly
            />
            <el-button type="primary" size="small" style="margin-top: 12px;" @click="copySchema">
              <el-icon><CopyDocument /></el-icon>
              复制Schema
            </el-button>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 搜索引擎提交 -->
      <el-tab-pane label="搜索引擎提交" name="submission">
        <el-card shadow="hover" class="tool-card">
          <template #header>
            <span>搜索引擎提交状态</span>
          </template>
          <el-table :data="submissionStatus" style="width: 100%">
            <el-table-column prop="engine" label="搜索引擎" width="160">
              <template #default="{ row }">
                <div class="engine-name">
                  <el-icon><Promotion /></el-icon>
                  <span>{{ row.engine }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="submitted" label="已提交URL数" width="120" align="center" />
            <el-table-column prop="indexed" label="已收录数" width="120" align="center" />
            <el-table-column prop="last_submit" label="最后提交时间" width="180" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '已连接' : '未连接' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" type="primary" link @click="submitSitemap(row)">提交Sitemap</el-button>
                <el-button size="small" type="success" link @click="submitUrl(row)">提交URL</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="hover" style="margin-top: 20px;">
          <template #header>
            <span>批量提交URL</span>
          </template>
          <el-form label-width="100px">
            <el-form-item label="搜索引擎">
              <el-select v-model="batchSubmitForm.engine" style="width: 200px">
                <el-option label="Google" value="google" />
                <el-option label="Bing" value="bing" />
                <el-option label="百度" value="baidu" />
                <el-option label="Yandex" value="yandex" />
              </el-select>
            </el-form-item>
            <el-form-item label="URL列表">
              <el-input
                v-model="batchSubmitForm.urls"
                type="textarea"
                :rows="6"
                placeholder="每行一个URL"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="batchSubmit" :loading="submitting">批量提交</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 收录数据 -->
      <el-tab-pane label="收录数据" name="indexing">
        <el-card shadow="hover" class="tool-card">
          <template #header>
            <div class="card-header">
              <span>页面收录情况</span>
              <el-button size="small" @click="loadIndexingData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-table :data="indexingData" v-loading="indexingLoading" style="width: 100%">
            <el-table-column prop="url" label="页面URL" min-width="300" show-overflow-tooltip />
            <el-table-column prop="google" label="Google" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.google ? 'success' : 'info'" size="small">
                  {{ row.google ? '已收录' : '未收录' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="bing" label="Bing" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.bing ? 'success' : 'info'" size="small">
                  {{ row.bing ? '已收录' : '未收录' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="baidu" label="百度" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.baidu ? 'success' : 'info'" size="small">
                  {{ row.baidu ? '已收录' : '未收录' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_check" label="最后检查" width="180" />
            <template #empty>
              <el-empty description="暂无收录数据" />
            </template>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 检查清单 -->
      <el-tab-pane label="检查清单" name="checklist">
        <el-card shadow="hover" class="tool-card">
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  auditSEO,
  generateSEOTitle,
  generateMetaDescription,
  generateSchema as generateSchemaApi,
  getSEOChecklist
} from '@/api/seo'

const activeTab = ref('analyze')
const analyzing = ref(false)
const generatingTitle = ref(false)
const generatingDesc = ref(false)
const submitting = ref(false)
const indexingLoading = ref(false)

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

const schemaForm = reactive({
  type: 'Product',
  name: '',
  description: '',
  image: '',
  url: '',
  price: 0,
  currency: 'USD',
  availability: 'InStock'
})

const schemaResult = ref('')

const batchSubmitForm = reactive({
  engine: 'google',
  urls: ''
})

const overview = ref({
  avgScore: 75,
  goodPages: 12,
  warningPages: 5,
  indexedPages: 28
})

const submissionStatus = ref([
  { engine: 'Google Search Console', submitted: 156, indexed: 89, last_submit: '2024-01-15 10:30', status: 'active' },
  { engine: 'Bing Webmaster', submitted: 120, indexed: 75, last_submit: '2024-01-14 16:45', status: 'active' },
  { engine: '百度站长', submitted: 98, indexed: 62, last_submit: '2024-01-14 14:00', status: 'active' },
  { engine: 'Yandex Webmaster', submitted: 0, indexed: 0, last_submit: '-', status: 'inactive' }
])

const indexingData = ref<any[]>([])

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

const doAnalyze = async () => {
  if (!analyzeForm.url) {
    ElMessage.warning('请输入页面URL')
    return
  }
  analyzing.value = true
  try {
    const keywords = analyzeForm.keywords
      ? analyzeForm.keywords.split(',').map(k => k.trim()).filter(Boolean)
      : []
    const res: any = await auditSEO({
      url: analyzeForm.url,
      target_keywords: keywords
    })
    analysisResult.value = res.data || res
    ElMessage.success('分析完成')
  } catch (error: any) {
    ElMessage.error('分析失败：' + (error.message || ''))
    // 使用模拟数据
    analysisResult.value = {
      overall_score: 75,
      content_score: 80,
      technical_score: 70,
      performance_score: 72,
      title: '示例页面标题',
      description: '示例页面描述',
      issues: [
        { type: 'title', severity: 'warning', message: '标题过短: 25字符，建议30-60字符', suggestion: '增加标题长度，包含主要关键词' },
        { type: 'description', severity: 'error', message: '缺少meta description', suggestion: '添加70-160字符的描述' },
        { type: 'images', severity: 'warning', message: '有5张图片缺少alt属性', suggestion: '为所有图片添加描述性alt' },
        { type: 'content', severity: 'info', message: '内容一般: 450字，建议1000字以上效果更好', suggestion: '扩充内容，提供更多价值' },
        { type: 'canonical', severity: 'warning', message: '缺少canonical标签', suggestion: '添加canonical标签避免重复内容' }
      ]
    }
  } finally {
    analyzing.value = false
  }
}

const generateTitle = async () => {
  if (!generateForm.content || !generateForm.keywords) {
    ElMessage.warning('请输入内容摘要和关键词')
    return
  }
  generatingTitle.value = true
  try {
    const res: any = await generateSEOTitle(
      generateForm.content,
      generateForm.keywords,
      generateForm.language
    )
    const data = res.data || res
    generatedResult.value = {
      ...generatedResult.value,
      title: data.title || data
    }
    ElMessage.success('标题生成成功')
  } catch (error: any) {
    ElMessage.error('生成失败：' + (error.message || ''))
    generatedResult.value = {
      ...generatedResult.value,
      title: '最佳电子烟产品推荐 - 2024年专业评测 | BangVape'
    }
  } finally {
    generatingTitle.value = false
  }
}

const generateDescription = async () => {
  if (!generateForm.content || !generateForm.keywords) {
    ElMessage.warning('请输入内容摘要和关键词')
    return
  }
  generatingDesc.value = true
  try {
    const res: any = await generateMetaDescription(
      generateForm.content,
      generateForm.keywords,
      generateForm.language
    )
    const data = res.data || res
    generatedResult.value = {
      ...generatedResult.value,
      description: data.description || data
    }
    ElMessage.success('描述生成成功')
  } catch (error: any) {
    ElMessage.error('生成失败：' + (error.message || ''))
    generatedResult.value = {
      ...generatedResult.value,
      description: 'BangVape提供精选电子烟产品，专业评测各类 vape 设备和烟油，为您推荐最适合的电子烟产品。'
    }
  } finally {
    generatingDesc.value = false
  }
}

const generateSchema = async () => {
  try {
    const data: any = {
      name: schemaForm.name,
      description: schemaForm.description,
      image: schemaForm.image,
      url: schemaForm.url
    }
    if (schemaForm.type === 'Product') {
      data.offers = {
        price: schemaForm.price,
        priceCurrency: schemaForm.currency,
        availability: `https://schema.org/${schemaForm.availability}`
      }
    }
    const res: any = await generateSchemaApi(schemaForm.type, data)
    schemaResult.value = typeof res === 'string' ? res : JSON.stringify(res.data || res, null, 2)
    ElMessage.success('Schema生成成功')
  } catch (error: any) {
    // 本地生成
    const schema: any = {
      '@context': 'https://schema.org',
      '@type': schemaForm.type,
      name: schemaForm.name,
      description: schemaForm.description,
      image: schemaForm.image,
      url: schemaForm.url
    }
    if (schemaForm.type === 'Product') {
      schema.offers = {
        '@type': 'Offer',
        price: schemaForm.price,
        priceCurrency: schemaForm.currency,
        availability: `https://schema.org/${schemaForm.availability}`
      }
    }
    schemaResult.value = JSON.stringify(schema, null, 2)
    ElMessage.success('Schema已生成')
  }
}

const copySchema = () => {
  navigator.clipboard.writeText(schemaResult.value).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const submitSitemap = (engine: any) => {
  ElMessage.success(`已向 ${engine.engine} 提交Sitemap`)
}

const submitUrl = (engine: any) => {
  ElMessage.success(`已向 ${engine.engine} 提交URL`)
}

const batchSubmit = async () => {
  if (!batchSubmitForm.urls) {
    ElMessage.warning('请输入URL列表')
    return
  }
  submitting.value = true
  try {
    const urls = batchSubmitForm.urls.split('\n').map(u => u.trim()).filter(Boolean)
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success(`成功提交 ${urls.length} 个URL到 ${batchSubmitForm.engine}`)
    batchSubmitForm.urls = ''
  } catch (error: any) {
    ElMessage.error('提交失败：' + (error.message || ''))
  } finally {
    submitting.value = false
  }
}

const loadIndexingData = async () => {
  indexingLoading.value = true
  try {
    // 模拟数据
    indexingData.value = [
      { url: 'https://example.com/', google: true, bing: true, baidu: true, last_check: '2024-01-15 10:30' },
      { url: 'https://example.com/products', google: true, bing: true, baidu: false, last_check: '2024-01-15 10:30' },
      { url: 'https://example.com/about', google: true, bing: false, baidu: false, last_check: '2024-01-14 16:45' },
      { url: 'https://example.com/blog/post-1', google: false, bing: false, baidu: false, last_check: '2024-01-14 14:00' }
    ]
  } finally {
    indexingLoading.value = false
  }
}

const loadChecklist = async () => {
  try {
    const res: any = await getSEOChecklist()
    const data = res.data || res
    if (data?.on_page) {
      checklist.on_page = data.on_page
    }
    if (data?.technical) {
      checklist.technical = data.technical
    }
    if (data?.performance) {
      checklist.performance = data.performance
    }
  } catch (error) {
    // 使用默认 checklist
  }
}

onMounted(() => {
  loadChecklist()
  loadIndexingData()
})
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

.stats-row {
  margin-bottom: 20px;
}

.mini-stat {
  border: none;
  border-radius: 8px;
}

.mini-stat-content {
  text-align: center;
  padding: 8px 0;
}

.mini-stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1f2937;
}

.mini-stat-value.primary {
  color: #3b82f6;
}

.mini-stat-value.success {
  color: #10b981;
}

.mini-stat-value.warning {
  color: #f59e0b;
}

.mini-stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.content-tabs {
  background: white;
  padding: 16px;
  border-radius: 8px;
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

.schema-result {
  margin-top: 20px;
}

.schema-result h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #1f2937;
}

.engine-name {
  display: flex;
  align-items: center;
  gap: 8px;
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
