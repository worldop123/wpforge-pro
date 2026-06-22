<template>
  <div class="sites-page">
    <el-card class="page-header-card" shadow="hover">
      <div class="page-header">
        <div>
          <h2>站点管理</h2>
          <p class="subtitle">管理您的WordPress站点，配置连接信息</p>
        </div>
        <div class="header-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索站点..."
            style="width: 220px; margin-right: 12px;"
            clearable
            @keyup.enter="loadSites"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="filterGroup"
            placeholder="分组筛选"
            clearable
            style="width: 160px; margin-right: 12px;"
            @change="loadSites"
          >
            <el-option label="全部" value="" />
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
          </el-select>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            添加站点
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ statsTotal }}</div>
            <div class="mini-stat-label">站点总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value online">{{ statsOnline }}</div>
            <div class="mini-stat-label">在线站点</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value offline">{{ statsOffline }}</div>
            <div class="mini-stat-label">离线站点</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ statsProducts }}</div>
            <div class="mini-stat-label">产品总数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="sites-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>站点列表</span>
          <div v-if="selectedRows.length > 0" class="batch-actions">
            <el-button type="danger" size="small" @click="batchDelete">
              批量删除 ({{ selectedRows.length }})
            </el-button>
            <el-button type="primary" size="small" @click="batchTestConnection">
              批量测试连接
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="sites"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="站点名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="site-name">
              <el-icon :class="getStatusClass(row)"><Connection /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="站点地址" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link :href="row.url || row.wp_url" target="_blank" type="primary" :underline="false">
              {{ row.url || row.wp_url }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="健康状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row)" size="small">
              {{ getStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="language" label="语言" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.language || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currency" label="货币" width="100">
          <template #default="{ row }">{{ row.currency || '-' }}</template>
        </el-table-column>
        <el-table-column prop="products_count" label="产品数" width="100" align="center">
          <template #default="{ row }">{{ row.products_count || row.products || 0 }}</template>
        </el-table-column>
        <el-table-column prop="updated_at" label="最后同步" width="180">
          <template #default="{ row }">{{ row.updated_at || row.last_sync || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="testConnection(row)" :loading="row._testing">
              测试
            </el-button>
            <el-button size="small" type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" type="warning" @click="editSite(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSite(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无站点，请点击右上角添加站点" />
        </template>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑站点对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEdit ? '编辑WordPress站点' : '添加WordPress站点'"
      width="640px"
    >
      <el-form ref="siteFormRef" :model="siteForm" :rules="siteRules" label-width="140px">
        <el-form-item label="站点名称" prop="name">
          <el-input v-model="siteForm.name" placeholder="请输入站点名称" />
        </el-form-item>
        <el-form-item label="站点地址" prop="wp_url">
          <el-input v-model="siteForm.wp_url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="WordPress用户名" prop="wp_username">
          <el-input v-model="siteForm.wp_username" placeholder="WordPress用户名" />
        </el-form-item>
        <el-form-item label="应用密码" prop="wp_password">
          <el-input v-model="siteForm.wp_password" type="password" placeholder="应用密码" show-password />
        </el-form-item>
        <el-form-item label="WooCommerce Key">
          <el-input v-model="siteForm.wc_consumer_key" placeholder="Consumer Key" />
        </el-form-item>
        <el-form-item label="WooCommerce Secret">
          <el-input v-model="siteForm.wc_consumer_secret" type="password" placeholder="Consumer Secret" show-password />
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="siteForm.language" style="width: 100%">
            <el-option label="中文" value="zh-CN" />
            <el-option label="英语" value="en" />
            <el-option label="匈牙利语" value="hu" />
            <el-option label="罗马尼亚语" value="ro" />
            <el-option label="德语" value="de" />
          </el-select>
        </el-form-item>
        <el-form-item label="货币">
          <el-select v-model="siteForm.currency" style="width: 100%">
            <el-option label="美元 USD" value="USD" />
            <el-option label="欧元 EUR" value="EUR" />
            <el-option label="人民币 CNY" value="CNY" />
            <el-option label="匈牙利福林 HUF" value="HUF" />
            <el-option label="罗马尼亚列伊 RON" value="RON" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveSite">保存</el-button>
      </template>
    </el-dialog>

    <!-- 站点详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="站点详情" width="640px">
      <el-descriptions v-if="currentSite" :column="2" border>
        <el-descriptions-item label="站点名称">{{ currentSite.name }}</el-descriptions-item>
        <el-descriptions-item label="站点地址">
          <el-link :href="currentSite.url || currentSite.wp_url" target="_blank" type="primary">
            {{ currentSite.url || currentSite.wp_url }}
          </el-link>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentSite)" size="small">{{ getStatusText(currentSite) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="语言">{{ currentSite.language || '-' }}</el-descriptions-item>
        <el-descriptions-item label="货币">{{ currentSite.currency || '-' }}</el-descriptions-item>
        <el-descriptions-item label="产品数">{{ currentSite.products_count || currentSite.products || 0 }}</el-descriptions-item>
        <el-descriptions-item label="WordPress用户名">{{ currentSite.wp_username || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentSite.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ currentSite.updated_at || currentSite.last_sync || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="syncSite(currentSite)">同步站点</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  getSites,
  createSite,
  updateSite,
  deleteSite as deleteSiteApi,
  testSiteConnection,
  syncSite as syncSiteApi
} from '@/api/sites'

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')
const filterGroup = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRows = ref<any[]>([])
const currentSite = ref<any>(null)
const siteFormRef = ref<FormInstance>()

const sites = ref<any[]>([])

const siteForm = reactive({
  id: undefined as number | undefined,
  name: '',
  wp_url: '',
  wp_username: '',
  wp_password: '',
  wc_consumer_key: '',
  wc_consumer_secret: '',
  language: 'zh-CN',
  currency: 'USD'
})

const siteRules: FormRules = {
  name: [{ required: true, message: '请输入站点名称', trigger: 'blur' }],
  wp_url: [
    { required: true, message: '请输入站点地址', trigger: 'blur' },
    { type: 'url', message: '请输入正确的URL', trigger: 'blur' }
  ],
  wp_username: [{ required: true, message: '请输入WordPress用户名', trigger: 'blur' }],
  wp_password: [{ required: true, message: '请输入应用密码', trigger: 'blur' }]
}

const statsTotal = computed(() => sites.value.length)
const statsOnline = computed(() => sites.value.filter(s => isSiteOnline(s)).length)
const statsOffline = computed(() => sites.value.length - statsOnline.value)
const statsProducts = computed(() => sites.value.reduce((sum, s) => sum + (s.products_count || s.products || 0), 0))

const isSiteOnline = (site: any) => {
  return site.status === 'connected' || site.status === 'active' || site.is_active === true
}

const getStatusTag = (site: any) => {
  return isSiteOnline(site) ? 'success' : 'danger'
}

const getStatusText = (site: any) => {
  return isSiteOnline(site) ? '在线' : '离线'
}

const getStatusClass = (site: any) => {
  return isSiteOnline(site) ? 'status-online' : 'status-offline'
}

const loadSites = async () => {
  loading.value = true
  try {
    const res: any = await getSites({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined
    })
    let items = res.data?.items || res.items || []
    // 应用分组筛选
    if (filterGroup.value === 'online') {
      items = items.filter((s: any) => isSiteOnline(s))
    } else if (filterGroup.value === 'offline') {
      items = items.filter((s: any) => !isSiteOnline(s))
    }
    sites.value = items
    total.value = res.data?.total || res.total || items.length
  } catch (error: any) {
    ElMessage.error('加载站点列表失败')
    sites.value = []
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadSites()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadSites()
}

const resetForm = () => {
  siteForm.id = undefined
  siteForm.name = ''
  siteForm.wp_url = ''
  siteForm.wp_username = ''
  siteForm.wp_password = ''
  siteForm.wc_consumer_key = ''
  siteForm.wc_consumer_secret = ''
  siteForm.language = 'zh-CN'
  siteForm.currency = 'USD'
}

const openAddDialog = () => {
  isEdit.value = false
  resetForm()
  showAddDialog.value = true
}

const editSite = (site: any) => {
  isEdit.value = true
  siteForm.id = site.id
  siteForm.name = site.name
  siteForm.wp_url = site.url || site.wp_url
  siteForm.wp_username = site.wp_username || ''
  siteForm.wp_password = site.wp_password || ''
  siteForm.wc_consumer_key = site.wc_consumer_key || ''
  siteForm.wc_consumer_secret = site.wc_consumer_secret || ''
  siteForm.language = site.language || 'zh-CN'
  siteForm.currency = site.currency || 'USD'
  showAddDialog.value = true
}

const saveSite = async () => {
  if (!siteFormRef.value) return
  await siteFormRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const payload = { ...siteForm } as any
      if (isEdit.value && siteForm.id) {
        await updateSite(siteForm.id, payload)
        ElMessage.success('站点更新成功')
      } else {
        await createSite(payload)
        ElMessage.success('站点添加成功')
      }
      showAddDialog.value = false
      loadSites()
    } catch (error: any) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const testConnection = async (site: any) => {
  site._testing = true
  try {
    await testSiteConnection(site.id)
    ElMessage.success(`${site.name} 连接成功`)
    site.status = 'connected'
  } catch (error: any) {
    ElMessage.error(`${site.name} 连接失败：${error.message || ''}`)
    site.status = 'disconnected'
  } finally {
    site._testing = false
  }
}

const viewDetail = (site: any) => {
  currentSite.value = site
  showDetailDialog.value = true
}

const syncSite = async (site: any) => {
  if (!site) return
  try {
    await syncSiteApi(site.id)
    ElMessage.success('同步任务已创建')
    showDetailDialog.value = false
  } catch (error: any) {
    ElMessage.error('同步失败：' + (error.message || ''))
  }
}

const deleteSite = (site: any) => {
  ElMessageBox.confirm(
    `确定要删除站点 "${site.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteSiteApi(site.id)
      ElMessage.success('删除成功')
      loadSites()
    } catch (error: any) {
      ElMessage.error('删除失败：' + (error.message || ''))
    }
  }).catch(() => {})
}

const batchDelete = () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.length} 个站点吗？`,
    '批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await Promise.all(selectedRows.value.map(s => deleteSiteApi(s.id)))
      ElMessage.success('批量删除成功')
      selectedRows.value = []
      loadSites()
    } catch (error: any) {
      ElMessage.error('批量删除失败：' + (error.message || ''))
    }
  }).catch(() => {})
}

const batchTestConnection = async () => {
  ElMessage.info(`正在测试 ${selectedRows.value.length} 个站点的连接...`)
  try {
    await Promise.allSettled(selectedRows.value.map(s => testSiteConnection(s.id)))
    ElMessage.success('批量测试完成')
    loadSites()
  } catch (error: any) {
    ElMessage.error('批量测试失败')
  }
}

onMounted(() => {
  loadSites()
})
</script>

<style scoped>
.sites-page {
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
  align-items: center;
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

.mini-stat-value.online {
  color: #10b981;
}

.mini-stat-value.offline {
  color: #ef4444;
}

.mini-stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.sites-list-card {
  border: none;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.site-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-online {
  color: #10b981;
}

.status-offline {
  color: #ef4444;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
