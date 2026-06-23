<template>
  <div class="one-click-site">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>一键建站</h2>
      <p>输入目标网站URL，AI自动分析并生成完整网站</p>
    </div>

    <!-- 步骤1：输入URL -->
    <div v-if="currentStep === 1" class="step-card">
      <div class="step-number">1</div>
      <h3>输入目标网站</h3>
      <p class="step-desc">输入您想要参考的网站URL，AI将自动分析其结构、设计和内容</p>

      <el-form :model="form" label-width="100px">
        <el-form-item label="目标URL" prop="targetUrl">
          <el-input
            v-model="form.targetUrl"
            placeholder="https://example.com"
            size="large"
          >
            <template #append>
              <el-button type="primary" @click="analyzeSite" :loading="analyzing">
                开始分析
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="站点名称">
          <el-input v-model="form.siteName" placeholder="我的新网站" />
        </el-form-item>

        <el-form-item label="行业类型">
          <el-select v-model="form.industry" placeholder="选择行业类型">
            <el-option label="电商" value="ecommerce" />
            <el-option label="博客" value="blog" />
            <el-option label="企业官网" value="corporate" />
            <el-option label="作品集" value="portfolio" />
            <el-option label="落地页" value="landing" />
            <el-option label="电子烟" value="vape" />
          </el-select>
        </el-form-item>

        <el-form-item label="目标语言">
          <el-select v-model="form.targetLanguage" placeholder="选择目标语言">
            <el-option label="中文" value="zh-CN" />
            <el-option label="英语" value="en" />
            <el-option label="德语" value="de" />
            <el-option label="匈牙利语" value="hu" />
            <el-option label="罗马尼亚语" value="ro" />
          </el-select>
        </el-form-item>
      </el-form>

      <div class="quick-templates">
        <h4>快速模板</h4>
        <div class="template-grid">
          <div
            v-for="template in quickTemplates"
            :key="template.id"
            class="template-card"
            @click="selectTemplate(template)"
          >
            <div class="template-preview">
              <el-icon :size="40"><component :is="template.icon" /></el-icon>
            </div>
            <div class="template-name">{{ template.name }}</div>
            <div class="template-desc">{{ template.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 步骤2：AI分析预览 -->
    <div v-if="currentStep === 2" class="step-card">
      <div class="step-number">2</div>
      <h3>AI分析结果</h3>
      <p class="step-desc">AI已分析目标网站，以下是识别到的配置信息</p>

      <div v-if="analyzing" class="analyzing-progress">
        <el-progress :percentage="analysisProgress" status="success" />
        <p>{{ analysisStatus }}</p>
      </div>

      <div v-else class="analysis-result">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="info-card">
              <template #header>
                <span><el-icon><Monitor /></el-icon> 网站信息</span>
              </template>
              <div class="info-item">
                <span class="label">平台：</span>
                <span class="value">{{ analysisResult.platform }}</span>
              </div>
              <div class="info-item">
                <span class="label">页面数量：</span>
                <span class="value">{{ analysisResult.pageCount }}</span>
              </div>
              <div class="info-item">
                <span class="label">产品数量：</span>
                <span class="value">{{ analysisResult.productCount }}</span>
              </div>
              <div class="info-item">
                <span class="label">语言：</span>
                <span class="value">{{ analysisResult.language }}</span>
              </div>
              <div class="info-item">
                <span class="label">页面构建器：</span>
                <span class="value">{{ analysisResult.builder }}</span>
              </div>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card class="info-card">
              <template #header>
                <span><el-icon><Picture /></el-icon> 设计风格</span>
              </template>
              <div class="color-palette">
                <div
                  v-for="(color, index) in analysisResult.colors"
                  :key="index"
                  class="color-swatch"
                  :style="{ backgroundColor: color }"
                  :title="color"
                ></div>
              </div>
              <div class="info-item">
                <span class="label">主字体：</span>
                <span class="value">{{ analysisResult.primaryFont }}</span>
              </div>
              <div class="info-item">
                <span class="label">布局风格：</span>
                <span class="value">{{ analysisResult.layoutStyle }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <div class="action-buttons">
          <el-button @click="currentStep = 1">返回修改</el-button>
          <el-button type="primary" @click="startCloning" :loading="cloning">
            开始建站
          </el-button>
        </div>
      </div>
    </div>

    <!-- 步骤3：建站进度 -->
    <div v-if="currentStep === 3" class="step-card">
      <div class="step-number">3</div>
      <h3>正在建站</h3>
      <p class="step-desc">AI正在自动生成网站，请稍候...</p>

      <div class="progress-section">
        <el-progress :percentage="cloneProgress" :status="cloneProgress === 100 ? 'success' : ''" />
        <p class="current-task">{{ currentTask }}</p>
      </div>

      <div class="steps-timeline">
        <div
          v-for="(step, index) in cloneSteps"
          :key="index"
          class="timeline-item"
          :class="{ active: step.status === 'active', done: step.status === 'done' }"
        >
          <div class="timeline-icon">
            <el-icon v-if="step.status === 'done'"><Check /></el-icon>
            <el-icon v-else-if="step.status === 'active'" class="loading"><Loading /></el-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="timeline-content">
            <div class="timeline-title">{{ step.title }}</div>
            <div class="timeline-desc">{{ step.desc }}</div>
          </div>
        </div>
      </div>

      <div class="log-section">
        <h4>详细日志</h4>
        <div class="log-output" ref="logOutput">
          <div v-for="(log, index) in buildLogs" :key="index" :class="['log-line', log.type]">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 步骤4：完成 -->
    <div v-if="currentStep === 4" class="step-card">
      <div class="step-number success">
        <el-icon><Check /></el-icon>
      </div>
      <h3>建站完成！</h3>
      <p class="step-desc">您的网站已成功创建，以下是详细信息</p>

      <el-result icon="success" title="网站创建成功" sub-title="您可以查看预览或进入管理后台">
        <template #extra>
          <el-button type="primary" @click="viewSite">查看网站</el-button>
          <el-button @click="goToAdmin">进入后台</el-button>
          <el-button @click="startNew">再建一个</el-button>
        </template>
      </el-result>

      <el-row :gutter="20" class="result-stats">
        <el-col :span="6">
          <el-statistic title="页面数量" :value="siteResult.pages" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="产品数量" :value="siteResult.products" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="图片数量" :value="siteResult.images" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="用时" :value="siteResult.duration" suffix="秒" />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  Picture,
  Check,
  Loading,
  Shop,
  Document,
  Briefcase,
  DataLine,
  MagicStick
} from '@element-plus/icons-vue'
import { aiAnalyzeSite } from '@/api/ai'
import { createTask, getTask } from '@/api/tasks'

const currentStep = ref(1)
const analyzing = ref(false)
const cloning = ref(false)
const analysisProgress = ref(0)
const analysisStatus = ref('')
const cloneProgress = ref(0)
const currentTask = ref('')
const logOutput = ref<HTMLElement | null>(null)

// 当前建站任务ID（用于轮询进度）
let currentTaskId: number | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

const form = reactive({
  targetUrl: '',
  siteName: '',
  industry: 'ecommerce',
  targetLanguage: 'zh-CN'
})

const quickTemplates = [
  { id: 'ecommerce', name: '电商站', desc: 'WooCommerce完整电商', icon: 'Shop' },
  { id: 'blog', name: '博客站', desc: '内容博客+SEO优化', icon: 'Document' },
  { id: 'corporate', name: '企业站', desc: '企业官网+产品展示', icon: 'Briefcase' },
  { id: 'portfolio', name: '作品集', desc: '作品展示+创意设计', icon: 'Image' },
  { id: 'landing', name: '落地页', desc: '营销落地+转化优化', icon: 'DataLine' },
  { id: 'vape', name: '电子烟', desc: '跨境电子烟专用', icon: 'MagicStick' }
]

// 分析结果（字段来自 /ai/analyze-site 真实接口）
const analysisResult = reactive<any>({
  site_type: '',
  confidence: 0,
  language: '',
  currency: '',
  pagination_type: '',
  product_list_selector: '',
  detected_fields: [] as any[],
  recommendations: [] as any[],
  has_anti_detection: false,
})

const cloneSteps = ref([
  { title: '爬取网站内容', desc: '抓取所有页面和产品数据', status: 'pending' },
  { title: '内容原创化', desc: 'AI改写文本，重绘图片', status: 'pending' },
  { title: '生成主题配置', desc: '提取配色、字体、布局', status: 'pending' },
  { title: '创建WordPress站点', desc: '安装主题和插件', status: 'pending' },
  { title: '导入内容', desc: '导入页面、产品、图片', status: 'pending' },
  { title: 'SEO优化', desc: '自动优化SEO设置', status: 'pending' },
  { title: '性能优化', desc: '缓存、压缩、CDN配置', status: 'pending' }
])

const buildLogs = ref<Array<{ time: string; message: string; type: string }>>([])

const siteResult = reactive({
  pages: 0,
  products: 0,
  images: 0,
  duration: 0
})

// 调用真实网站分析 API
const analyzeSite = async () => {
  if (!form.targetUrl) {
    ElMessage.warning('请输入目标网站URL')
    return
  }

  analyzing.value = true
  analysisProgress.value = 0
  analysisStatus.value = '正在连接目标网站...'

  // 分析进度模拟（接口为单次请求，用进度提示用户体验）
  const steps = [
    { progress: 30, status: '正在分析网站结构...' },
    { progress: 60, status: '正在识别页面元素...' },
    { progress: 90, status: '正在生成分析报告...' },
  ]
  for (const step of steps) {
    await new Promise(resolve => setTimeout(resolve, 400))
    analysisProgress.value = step.progress
    analysisStatus.value = step.status
  }

  try {
    const res: any = await aiAnalyzeSite({ url: form.targetUrl })
    const data = res.data || res
    analysisResult.site_type = data.site_type || 'unknown'
    analysisResult.confidence = data.confidence || 0
    analysisResult.language = data.language || form.targetLanguage
    analysisResult.currency = data.currency || ''
    analysisResult.pagination_type = data.pagination_type || ''
    analysisResult.product_list_selector = data.product_list_selector || ''
    analysisResult.detected_fields = data.detected_fields || []
    analysisResult.recommendations = data.recommendations || []
    analysisResult.has_anti_detection = !!data.has_anti_detection
    analysisProgress.value = 100
    analysisStatus.value = '分析完成！'
    await new Promise(resolve => setTimeout(resolve, 300))
    analyzing.value = false
    currentStep.value = 2
  } catch (error: any) {
    analyzing.value = false
    ElMessage.error('网站分析失败：' + (error?.message || '请检查URL或稍后重试'))
  }
}

const selectTemplate = (template: any) => {
  form.industry = template.id
  ElMessage.info(`已选择 ${template.name} 模板`)
}

const addLog = (message: string, type = 'info') => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  buildLogs.value.push({ time, message, type })
  nextTick(() => {
    if (logOutput.value) {
      logOutput.value.scrollTop = logOutput.value.scrollHeight
    }
  })
}

// 根据任务进度更新步骤状态
const updateStepsByProgress = (progress: number) => {
  const stepCount = cloneSteps.value.length
  const activeIndex = Math.min(Math.floor(progress / (100 / stepCount)), stepCount - 1)
  cloneSteps.value.forEach((step, idx) => {
    if (idx < activeIndex) step.status = 'done'
    else if (idx === activeIndex && progress < 100) step.status = 'active'
    else if (progress >= 100) step.status = 'done'
    else step.status = 'pending'
  })
}

// 轮询任务进度
const pollTaskProgress = () => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    if (!currentTaskId) return
    try {
      const res: any = await getTask(currentTaskId)
      const task = res.data || res
      const progress = task.progress || 0
      cloneProgress.value = progress
      updateStepsByProgress(progress)

      if (task.status === 'completed') {
        stopPolling()
        cloneProgress.value = 100
        updateStepsByProgress(100)
        addLog('✓ 建站任务完成', 'success')
        // 填充结果统计
        const params = task.params || {}
        siteResult.pages = params.pages || 0
        siteResult.products = params.products || 0
        siteResult.images = params.images || 0
        siteResult.duration = params.duration || 0
        cloning.value = false
        currentStep.value = 4
        ElMessage.success('网站创建成功！')
      } else if (task.status === 'failed') {
        stopPolling()
        cloning.value = false
        addLog('✗ 建站任务失败: ' + (task.error_message || '未知错误'), 'error')
        ElMessage.error('建站任务失败')
      } else {
        currentTask.value = task.status === 'pending' ? '任务排队中...' : '正在建站...'
      }
    } catch (error) {
      // 轮询失败时静默，等待下一次
    }
  }, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 创建真实建站任务并轮询进度
const startCloning = async () => {
  cloning.value = true
  cloneProgress.value = 0
  currentTask.value = '正在创建建站任务...'
  buildLogs.value = []
  cloneSteps.value.forEach(s => (s.status = 'pending'))

  addLog('开始建站流程', 'success')
  addLog('目标网站: ' + form.targetUrl)

  try {
    const res: any = await createTask({
      name: form.siteName || `一键建站: ${form.targetUrl}`,
      task_type: 'cloning',
      priority: 1,
      params: {
        target_url: form.targetUrl,
        site_name: form.siteName,
        industry: form.industry,
        target_language: form.targetLanguage,
        analysis: { ...analysisResult },
      },
    })
    const task = res.data || res
    currentTaskId = task.id
    addLog(`建站任务已创建（ID: ${task.id}）`, 'success')
    currentTask.value = '任务已提交，等待执行...'
    pollTaskProgress()
  } catch (error: any) {
    cloning.value = false
    addLog('✗ 创建建站任务失败: ' + (error?.message || ''), 'error')
    ElMessage.error('创建建站任务失败：' + (error?.message || ''))
  }
}

const viewSite = () => {
  ElMessage.info('正在打开网站预览...')
}

const goToAdmin = () => {
  ElMessage.info('正在进入管理后台...')
}

const startNew = () => {
  stopPolling()
  currentTaskId = null
  currentStep.value = 1
  form.targetUrl = ''
  form.siteName = ''
  cloneProgress.value = 0
  buildLogs.value = []
  cloneSteps.value.forEach(s => (s.status = 'pending'))
}

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.one-click-site {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.step-card {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.step-number.success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.step-card h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
}

.step-desc {
  color: #6b7280;
  margin-bottom: 24px;
}

.quick-templates {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #e5e7eb;
}

.quick-templates h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.template-card {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.template-preview {
  width: 60px;
  height: 60px;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
}

.template-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: #6b7280;
}

.analyzing-progress {
  text-align: center;
  padding: 40px 0;
}

.analyzing-progress p {
  margin-top: 16px;
  color: #6b7280;
}

.info-card {
  height: 100%;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #6b7280;
}

.info-item .value {
  font-weight: 500;
}

.color-palette {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.color-swatch {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.action-buttons {
  margin-top: 30px;
  text-align: right;
}

.action-buttons .el-button {
  margin-left: 12px;
}

.progress-section {
  text-align: center;
  padding: 20px 0;
}

.current-task {
  margin-top: 12px;
  color: #6b7280;
  font-size: 14px;
}

.steps-timeline {
  margin: 30px 0;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 0;
  opacity: 0.5;
}

.timeline-item.active {
  opacity: 1;
}

.timeline-item.done {
  opacity: 1;
}

.timeline-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.timeline-item.active .timeline-icon {
  background: #667eea;
  color: #fff;
}

.timeline-item.done .timeline-icon {
  background: #10b981;
  color: #fff;
}

.timeline-icon .loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.timeline-title {
  font-weight: 500;
  margin-bottom: 2px;
}

.timeline-desc {
  font-size: 12px;
  color: #6b7280;
}

.log-section {
  margin-top: 30px;
}

.log-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.log-output {
  background: #1f2937;
  color: #d1d5db;
  padding: 16px;
  border-radius: 8px;
  height: 200px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 12px;
}

.log-line {
  padding: 2px 0;
}

.log-line.success {
  color: #34d399;
}

.log-line.error {
  color: #f87171;
}

.log-time {
  color: #6b7280;
  margin-right: 8px;
}

.result-stats {
  margin-top: 30px;
}
</style>
