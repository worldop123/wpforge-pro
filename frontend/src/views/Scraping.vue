<template>
  <div class="scraping-page">
    <el-card class="page-header-card" shadow="hover">
      <div class="page-header">
        <div>
          <h2>采集任务</h2>
          <p class="subtitle">可视化采集产品数据，支持反检测和代理</p>
        </div>
        <div class="header-actions">
          <el-button type="success" @click="showAnalyzeDialog = true">
            <el-icon><Search /></el-icon>
            分析网站
          </el-button>
          <el-button type="primary" @click="openCreateWizard">
            <el-icon><Plus /></el-icon>
            新建采集任务
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ stats.total }}</div>
            <div class="mini-stat-label">任务总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value primary">{{ stats.running }}</div>
            <div class="mini-stat-label">进行中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value success">{{ stats.completed }}</div>
            <div class="mini-stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ stats.totalProducts }}</div>
            <div class="mini-stat-label">采集产品数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="tasks-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>采集任务列表</span>
          <div class="filter-bar">
            <el-select v-model="filterStatus" placeholder="状态筛选" clearable size="small" style="width: 130px;" @change="loadTasks">
              <el-option label="全部" value="" />
              <el-option label="进行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
              <el-option label="等待中" value="pending" />
            </el-select>
            <el-button size="small" @click="loadTasks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tasks" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="任务名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="source_url" label="来源网站" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link :href="row.source_url || row.start_url" target="_blank" type="primary" :underline="false">
              {{ row.source_url || row.start_url }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="row.status === 'failed' ? 'exception' : row.status === 'completed' ? 'success' : ''"
            />
          </template>
        </el-table-column>
        <el-table-column prop="products_count" label="产品数" width="100" align="center">
          <template #default="{ row }">{{ row.products_count || row.products || 0 }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewTask(row)">查看</el-button>
            <el-button
              v-if="row.status === 'running' || row.status === '进行中'"
              size="small"
              type="warning"
              link
              @click="stopTask(row)"
            >
              停止
            </el-button>
            <el-button
              v-if="row.status === 'failed' || row.status === '失败'"
              size="small"
              type="success"
              link
              @click="retryTask(row)"
            >
              重试
            </el-button>
            <el-button size="small" type="danger" link @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无采集任务，请点击右上角新建任务" />
        </template>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新建采集任务向导 -->
    <el-dialog v-model="showCreateDialog" title="新建采集任务" width="780px" :close-on-click-modal="false">
      <el-steps :active="wizardStep" finish-status="success" align-center class="wizard-steps">
        <el-step title="基本信息" />
        <el-step title="采集配置" />
        <el-step title="高级选项" />
      </el-steps>

      <div class="wizard-content">
        <!-- 步骤 1: 基本信息 -->
        <div v-show="wizardStep === 0">
          <el-form :model="taskForm" label-width="120px">
            <el-form-item label="任务名称" required>
              <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
            </el-form-item>
            <el-form-item label="起始URL" required>
              <el-input v-model="taskForm.start_url" placeholder="https://example.com/products">
                <template #append>
                  <el-button @click="analyzeUrl">分析</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="目标站点">
              <el-select v-model="taskForm.site_id" placeholder="选择目标站点（可选）" clearable style="width: 100%">
                <el-option v-for="site in sites" :key="site.id" :label="site.name" :value="site.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="采集模板">
              <el-select v-model="taskForm.preset" placeholder="选择采集模板">
                <el-option label="WooCommerce" value="woocommerce" />
                <el-option label="Shopify" value="shopify" />
                <el-option label="Magento" value="magento" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤 2: 采集配置 -->
        <div v-show="wizardStep === 1">
          <el-form :model="taskForm" label-width="120px">
            <el-form-item label="最大页数">
              <el-input-number v-model="taskForm.max_pages" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="最大产品数">
              <el-input-number v-model="taskForm.max_products" :min="1" :max="10000" />
            </el-form-item>
            <el-form-item label="下载图片">
              <el-switch v-model="taskForm.download_images" />
            </el-form-item>
            <el-form-item label="采集变体">
              <el-switch v-model="taskForm.scrape_variations" />
            </el-form-item>
            <el-form-item label="采集评论">
              <el-switch v-model="taskForm.scrape_reviews" />
            </el-form-item>
            <el-form-item label="自动翻译">
              <el-switch v-model="taskForm.auto_translate" />
            </el-form-item>
            <el-form-item v-if="taskForm.auto_translate" label="目标语言">
              <el-select v-model="taskForm.target_language" style="width: 200px">
                <el-option label="中文" value="zh-CN" />
                <el-option label="英语" value="en" />
                <el-option label="匈牙利语" value="hu" />
                <el-option label="罗马尼亚语" value="ro" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤 3: 高级选项 -->
        <div v-show="wizardStep === 2">
          <el-form :model="taskForm" label-width="120px">
            <el-form-item label="启用反检测">
              <el-switch v-model="taskForm.use_stealth" />
              <span class="form-tip">模拟真实浏览器行为，避免被识别为爬虫</span>
            </el-form-item>
            <el-form-item label="使用代理">
              <el-switch v-model="taskForm.use_proxy" />
              <span class="form-tip">使用代理池轮换IP，避免被封禁</span>
            </el-form-item>
            <el-form-item label="自动导入">
              <el-switch v-model="taskForm.auto_import" />
              <span class="form-tip">采集完成后自动导入到WordPress站点</span>
            </el-form-item>
            <el-form-item label="请求间隔">
              <el-input-number v-model="taskForm.request_delay" :min="0" :max="10" :step="0.5" />
              <span class="form-tip">秒，每个请求之间的延迟</span>
            </el-form-item>
          </el-form>

          <el-alert
            title="配置预览"
            type="info"
            :closable="false"
            show-icon
            class="preview-alert"
          >
            <template #default>
              <div>任务名称: {{ taskForm.name || '-' }}</div>
              <div>起始URL: {{ taskForm.start_url || '-' }}</div>
              <div>最大产品数: {{ taskForm.max_products }}</div>
              <div>反检测: {{ taskForm.use_stealth ? '启用' : '关闭' }} | 代理: {{ taskForm.use_proxy ? '启用' : '关闭' }}</div>
            </template>
          </el-alert>
        </div>
      </div>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button v-if="wizardStep > 0" @click="wizardStep--">上一步</el-button>
        <el-button v-if="wizardStep < 2" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-else type="primary" :loading="creating" @click="createTask">开始采集</el-button>
      </template>
    </el-dialog>

    <!-- 网站分析对话框 -->
    <el-dialog v-model="showAnalyzeDialog" title="网站分析" width="640px">
      <el-form label-width="100px">
        <el-form-item label="网站URL" required>
          <el-input v-model="analyzeUrlInput" placeholder="https://example.com" />
        </el-form-item>
      </el-form>
      <div v-if="analyzeResult" class="analyze-result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="网站类型">{{ analyzeResult.site_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="置信度">{{ ((analyzeResult.confidence || 0) * 100).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="分页类型">{{ analyzeResult.pagination_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="货币">{{ analyzeResult.currency || '-' }}</el-descriptions-item>
          <el-descriptions-item label="语言">{{ analyzeResult.language || '-' }}</el-descriptions-item>
          <el-descriptions-item label="反检测">
            <el-tag :type="analyzeResult.has_anti_detection ? 'danger' : 'success'" size="small">
              {{ analyzeResult.has_anti_detection ? '有' : '无' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="analyzeResult.detected_fields?.length" class="detected-fields">
          <h4>检测到的字段</h4>
          <el-tag v-for="field in analyzeResult.detected_fields" :key="field.name" style="margin: 4px;">
            {{ field.name }} ({{ (field.confidence * 100).toFixed(0) }}%)
          </el-tag>
        </div>
      </div>
      <template #footer>
        <el-button @click="showAnalyzeDialog = false">关闭</el-button>
        <el-button type="primary" :loading="analyzing" @click="doAnalyze">开始分析</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="采集任务详情" width="780px">
      <el-descriptions v-if="currentTask" :column="2" border>
        <el-descriptions-item label="任务名称">{{ currentTask.name }}</el-descriptions-item>
        <el-descriptions-item label="来源网站">{{ currentTask.source_url || currentTask.start_url }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentTask.status)" size="small">{{ getStatusText(currentTask.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="进度">{{ currentTask.progress || 0 }}%</el-descriptions-item>
        <el-descriptions-item label="产品数">{{ currentTask.products_count || currentTask.products || 0 }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentTask.created_at }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="currentTask?.result?.products?.length" class="task-products">
        <h4>采集结果预览</h4>
        <el-table :data="currentTask.result.products.slice(0, 10)" style="width: 100%">
          <el-table-column prop="name" label="产品名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="price" label="价格" width="120" />
          <el-table-column prop="sku" label="SKU" width="120" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  startScraping,
  analyzeSite,
  getScrapingHistory,
  stopScraping,
  getScrapingStatus
} from '@/api/scraping'
import { getSites } from '@/api/sites'

const loading = ref(false)
const creating = ref(false)
const analyzing = ref(false)
const showCreateDialog = ref(false)
const showAnalyzeDialog = ref(false)
const showDetailDialog = ref(false)
const wizardStep = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterStatus = ref('')
const currentTask = ref<any>(null)
const analyzeUrlInput = ref('')
const analyzeResult = ref<any>(null)

const tasks = ref<any[]>([])
const sites = ref<any[]>([])

const taskForm = reactive({
  name: '',
  start_url: '',
  site_id: undefined as number | undefined,
  preset: 'woocommerce',
  max_pages: 10,
  max_products: 100,
  use_stealth: true,
  use_proxy: true,
  download_images: true,
  scrape_variations: false,
  scrape_reviews: false,
  auto_translate: false,
  auto_import: false,
  target_language: 'zh-CN',
  request_delay: 1
})

const stats = computed(() => ({
  total: total.value,
  running: tasks.value.filter(t => t.status === 'running' || t.status === '进行中').length,
  completed: tasks.value.filter(t => t.status === 'completed' || t.status === '已完成').length,
  totalProducts: tasks.value.reduce((sum, t) => sum + (t.products_count || t.products || 0), 0)
}))

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    running: 'primary',
    '进行中': 'primary',
    completed: 'success',
    '已完成': 'success',
    failed: 'danger',
    '失败': 'danger',
    pending: 'info',
    '等待中': 'info',
    cancelled: 'warning'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    running: '进行中',
    completed: '已完成',
    failed: '失败',
    pending: '等待中',
    cancelled: '已取消'
  }
  return map[status] || status
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res: any = await getScrapingHistory({
      page: currentPage.value,
      page_size: pageSize.value
    })
    let items = res.data?.items || res.items || []
    if (filterStatus.value) {
      items = items.filter((t: any) => t.status === filterStatus.value)
    }
    tasks.value = items
    total.value = res.data?.total || res.total || items.length
  } catch (error: any) {
    ElMessage.error('加载采集任务列表失败')
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const loadSites = async () => {
  try {
    const res: any = await getSites({ page: 1, page_size: 100 })
    sites.value = res.data?.items || res.items || []
  } catch (error) {
    console.warn('加载站点列表失败')
  }
}

const openCreateWizard = () => {
  wizardStep.value = 0
  Object.assign(taskForm, {
    name: '',
    start_url: '',
    site_id: undefined,
    preset: 'woocommerce',
    max_pages: 10,
    max_products: 100,
    use_stealth: true,
    use_proxy: true,
    download_images: true,
    scrape_variations: false,
    scrape_reviews: false,
    auto_translate: false,
    auto_import: false,
    target_language: 'zh-CN',
    request_delay: 1
  })
  showCreateDialog.value = true
}

const nextStep = () => {
  if (wizardStep.value === 0) {
    if (!taskForm.name || !taskForm.start_url) {
      ElMessage.warning('请填写任务名称和起始URL')
      return
    }
  }
  wizardStep.value++
}

const createTask = async () => {
  if (!taskForm.name || !taskForm.start_url) {
    ElMessage.error('请填写任务名称和起始URL')
    return
  }
  creating.value = true
  try {
    await startScraping({
      url: taskForm.start_url,
      site_id: taskForm.site_id,
      max_products: taskForm.max_products,
      auto_translate: taskForm.auto_translate,
      auto_import: taskForm.auto_import,
      target_language: taskForm.target_language,
      proxy_enabled: taskForm.use_proxy,
      scrape_images: taskForm.download_images,
      scrape_variations: taskForm.scrape_variations,
      scrape_reviews: taskForm.scrape_reviews
    })
    ElMessage.success('采集任务已创建')
    showCreateDialog.value = false
    loadTasks()
  } catch (error: any) {
    ElMessage.error('创建任务失败：' + (error.message || ''))
  } finally {
    creating.value = false
  }
}

const analyzeUrl = async () => {
  if (!taskForm.start_url) {
    ElMessage.warning('请先输入起始URL')
    return
  }
  analyzeUrlInput.value = taskForm.start_url
  showAnalyzeDialog.value = true
}

const doAnalyze = async () => {
  if (!analyzeUrlInput.value) {
    ElMessage.warning('请输入网站URL')
    return
  }
  analyzing.value = true
  try {
    const res: any = await analyzeSite(analyzeUrlInput.value)
    analyzeResult.value = res.data || res
    ElMessage.success('分析完成')
  } catch (error: any) {
    ElMessage.error('分析失败：' + (error.message || ''))
  } finally {
    analyzing.value = false
  }
}

const viewTask = async (task: any) => {
  currentTask.value = task
  showDetailDialog.value = true
  // 如果任务进行中，获取最新状态
  if (task.status === 'running' || task.status === '进行中') {
    try {
      const res: any = await getScrapingStatus(task.id)
      const data = res.data || res
      currentTask.value = { ...task, ...data }
    } catch (error) {
      // 忽略错误
    }
  }
}

const stopTask = async (task: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要停止任务 "${task.name}" 吗？`,
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await stopScraping(task.id)
    ElMessage.success('任务已停止')
    loadTasks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('停止任务失败')
    }
  }
}

const retryTask = async (task: any) => {
  try {
    await startScraping({
      url: task.source_url || task.start_url,
      site_id: task.site_id,
      max_products: task.max_products
    })
    ElMessage.success('重试任务已创建')
    loadTasks()
  } catch (error: any) {
    ElMessage.error('重试失败：' + (error.message || ''))
  }
}

const deleteTask = (task: any) => {
  ElMessageBox.confirm(
    `确定要删除任务 "${task.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    tasks.value = tasks.value.filter(t => t.id !== task.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadTasks()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadTasks()
}

onMounted(() => {
  loadTasks()
  loadSites()
})
</script>

<style scoped>
.scraping-page {
  padding: 0;
}

.page-header-card {
  margin-bottom: 20px;
  border: none;
  border-radius: 8px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.header-actions {
  display: flex;
  gap: 12px;
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

.mini-stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.tasks-card {
  border: none;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.wizard-steps {
  margin-bottom: 24px;
}

.wizard-content {
  min-height: 280px;
}

.form-tip {
  margin-left: 12px;
  color: #9ca3af;
  font-size: 12px;
}

.preview-alert {
  margin-top: 16px;
}

.preview-alert div {
  line-height: 1.8;
}

.analyze-result {
  margin-top: 16px;
}

.detected-fields {
  margin-top: 16px;
}

.detected-fields h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #1f2937;
}

.task-products {
  margin-top: 20px;
}

.task-products h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #1f2937;
}
</style>
