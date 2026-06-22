<template>
  <div class="tasks-page">
    <el-card class="page-header-card" shadow="hover">
      <div class="page-header">
        <div>
          <h2>任务中心</h2>
          <p class="subtitle">查看和管理所有任务，实时跟踪进度、查看日志、重试失败任务</p>
        </div>
        <div class="header-actions">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索任务名称..."
            style="width: 220px; margin-right: 12px;"
            clearable
            @keyup.enter="loadTasks"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="filterStatus"
            placeholder="状态筛选"
            clearable
            style="width: 150px; margin-right: 12px;"
            @change="loadTasks"
          >
            <el-option label="全部" value="" />
            <el-option label="等待中" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-select
            v-model="filterType"
            placeholder="类型筛选"
            clearable
            style="width: 150px; margin-right: 12px;"
            @change="loadTasks"
          >
            <el-option label="全部" value="" />
            <el-option label="采集" value="scrape" />
            <el-option label="翻译" value="translate" />
            <el-option label="导入" value="import" />
            <el-option label="SEO" value="seo" />
            <el-option label="价格" value="price" />
            <el-option label="优化" value="optimize" />
          </el-select>
          <el-button type="primary" @click="loadTasks">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 任务统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ stats.total || 0 }}</div>
            <div class="mini-stat-label">任务总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value running">{{ stats.running || 0 }}</div>
            <div class="mini-stat-label">运行中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value pending">{{ stats.pending || 0 }}</div>
            <div class="mini-stat-label">等待中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value success">{{ stats.completed || 0 }}</div>
            <div class="mini-stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value danger">{{ stats.failed || 0 }}</div>
            <div class="mini-stat-label">失败</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="mini-stat">
          <div class="mini-stat-content">
            <div class="mini-stat-value">{{ stats.cancelled || 0 }}</div>
            <div class="mini-stat-label">已取消</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任务列表 -->
    <el-card class="tasks-list-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <div v-if="selectedRows.length > 0" class="batch-actions">
            <el-button type="danger" size="small" @click="batchDelete">
              批量删除 ({{ selectedRows.length }})
            </el-button>
            <el-button type="warning" size="small" @click="batchRetry">
              批量重试
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="tasks"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="任务名称" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" @click="viewTask(row)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="task_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.task_type)" size="small">{{ getTypeText(row.task_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="240">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                :percentage="row.progress || 0"
                :status="getProgressStatus(row.status)"
                :stroke-width="14"
                :text-inside="true"
              />
              <span class="progress-detail" v-if="row.total_items">
                {{ row.processed_items || 0 }}/{{ row.total_items }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="处理情况" width="140">
          <template #default="{ row }">
            <div class="items-info">
              <span class="processed">成功: {{ row.processed_items || 0 }}</span>
              <span class="failed" v-if="row.failed_items">失败: {{ row.failed_items }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ calcDuration(row) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="viewTask(row)">详情</el-button>
            <el-button size="small" type="info" text @click="viewLogs(row)">日志</el-button>
            <el-button
              v-if="row.status === 'running' || row.status === 'pending'"
              size="small"
              type="warning"
              text
              @click="cancelTask(row)"
            >
              取消
            </el-button>
            <el-button
              v-if="row.status === 'failed' || row.status === 'cancelled'"
              size="small"
              type="success"
              text
              @click="retryTask(row)"
            >
              重试
            </el-button>
            <el-button size="small" type="danger" text @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无任务数据" />
        </template>
      </el-table>

      <div class="pagination-wrapper">
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

    <!-- 任务详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="任务详情" width="720px">
      <div v-loading="detailLoading">
        <el-descriptions v-if="currentTask" :column="2" border>
          <el-descriptions-item label="任务名称">{{ currentTask.name }}</el-descriptions-item>
          <el-descriptions-item label="任务ID">{{ currentTask.id }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            <el-tag :type="getTypeTag(currentTask.task_type)" size="small">{{ getTypeText(currentTask.task_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(currentTask.status)" size="small">{{ getStatusText(currentTask.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="进度">
            <el-progress
              :percentage="currentTask.progress || 0"
              :status="getProgressStatus(currentTask.status)"
              :stroke-width="14"
              :text-inside="true"
              style="width: 200px;"
            />
          </el-descriptions-item>
          <el-descriptions-item label="状态消息">{{ currentTask.status_message || '-' }}</el-descriptions-item>
          <el-descriptions-item label="总项目数">{{ currentTask.total_items || 0 }}</el-descriptions-item>
          <el-descriptions-item label="已处理">{{ currentTask.processed_items || 0 }}</el-descriptions-item>
          <el-descriptions-item label="失败数">{{ currentTask.failed_items || 0 }}</el-descriptions-item>
          <el-descriptions-item label="站点ID">{{ currentTask.site_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Celery任务ID">{{ currentTask.celery_task_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ currentTask.user_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(currentTask.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(currentTask.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatTime(currentTask.completed_at) }}</el-descriptions-item>
          <el-descriptions-item label="耗时" :span="2">{{ calcDuration(currentTask) }}</el-descriptions-item>
          <el-descriptions-item v-if="currentTask.error_message" label="错误信息" :span="2">
            <span class="error-text">{{ currentTask.error_message }}</span>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentTask.params" label="任务参数" :span="2">
            <pre class="json-block">{{ JSON.stringify(currentTask.params, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentTask.result" label="任务结果" :span="2">
            <pre class="json-block">{{ JSON.stringify(currentTask.result, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
        <el-empty v-else description="无任务详情" />
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button v-if="currentTask && (currentTask.status === 'failed' || currentTask.status === 'cancelled')" type="success" @click="retryTask(currentTask)">
          重试任务
        </el-button>
        <el-button v-if="currentTask && (currentTask.status === 'running' || currentTask.status === 'pending')" type="warning" @click="cancelTask(currentTask)">
          取消任务
        </el-button>
      </template>
    </el-dialog>

    <!-- 任务日志对话框 -->
    <el-dialog v-model="showLogsDialog" title="任务日志" width="800px" @open="loadLogs">
      <div v-loading="logsLoading">
        <div class="logs-header" v-if="currentTask">
          <span class="log-task-name">{{ currentTask.name }}</span>
          <el-tag :type="getStatusTag(currentTask.status)" size="small">{{ getStatusText(currentTask.status) }}</el-tag>
          <el-button size="small" type="primary" text style="margin-left: auto;" @click="loadLogs">
            <el-icon><Refresh /></el-icon>
            刷新日志
          </el-button>
        </div>
        <div class="logs-container" v-if="taskLogs.length > 0">
          <div
            v-for="log in taskLogs"
            :key="log.id"
            class="log-item"
            :class="`log-${log.level.toLowerCase()}`"
          >
            <span class="log-time">{{ formatTime(log.created_at) }}</span>
            <el-tag :type="getLogLevelTag(log.level)" size="small" class="log-level">{{ log.level }}</el-tag>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
        <el-empty v-else description="暂无日志数据" />
      </div>
      <template #footer>
        <el-button @click="showLogsDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTasks,
  getTask,
  getTaskLogs,
  getTaskStats,
  cancelTask as cancelTaskApi,
  retryTask as retryTaskApi,
  deleteTask as deleteTaskApi,
  batchDeleteTasks
} from '@/api/tasks'

const loading = ref(false)
const detailLoading = ref(false)
const logsLoading = ref(false)
const showDetailDialog = ref(false)
const showLogsDialog = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedRows = ref<any[]>([])
const currentTask = ref<any>(null)
const taskLogs = ref<any[]>([])

const tasks = ref<any[]>([])

const stats = reactive({
  total: 0,
  pending: 0,
  running: 0,
  completed: 0,
  failed: 0,
  cancelled: 0
})

let refreshTimer: ReturnType<typeof setInterval> | null = null

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    scrape: 'primary',
    translate: 'success',
    import: 'warning',
    seo: 'info',
    price: '',
    optimize: 'danger'
  }
  return map[type] || ''
}

const getTypeText = (type: string) => {
  const map: Record<string, string> = {
    scrape: '采集',
    translate: '翻译',
    import: '导入',
    seo: 'SEO',
    price: '价格',
    optimize: '优化'
  }
  return map[type] || type || '-'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status || '-'
}

const getProgressStatus = (status: string) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return ''
}

const getLogLevelTag = (level: string) => {
  const map: Record<string, string> = {
    DEBUG: 'info',
    INFO: '',
    WARNING: 'warning',
    ERROR: 'danger',
    CRITICAL: 'danger'
  }
  return map[level] || ''
}

const formatTime = (time: string) => {
  if (!time) return '-'
  try {
    return new Date(time).toLocaleString('zh-CN', { hour12: false })
  } catch {
    return time
  }
}

const calcDuration = (task: any) => {
  if (!task.started_at) return '-'
  const start = new Date(task.started_at).getTime()
  const end = task.completed_at ? new Date(task.completed_at).getTime() : Date.now()
  const diff = Math.floor((end - start) / 1000)
  if (diff < 60) return `${diff}s`
  if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`
  return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`
}

const loadTasks = async () => {
  loading.value = true
  try {
    const res: any = await getTasks({
      page: currentPage.value,
      page_size: pageSize.value,
      status: filterStatus.value || undefined,
      task_type: filterType.value || undefined
    })
    let items = res.data?.items || res.items || []
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      items = items.filter((t: any) => (t.name || '').toLowerCase().includes(kw))
    }
    tasks.value = items
    total.value = res.data?.total || res.total || items.length
  } catch (error: any) {
    ElMessage.error('加载任务列表失败')
    tasks.value = []
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const res: any = await getTaskStats()
    const data = res.data || res
    stats.total = data.total || 0
    stats.pending = data.pending || 0
    stats.running = data.running || 0
    stats.completed = data.completed || 0
    stats.failed = data.failed || 0
    stats.cancelled = data.cancelled || 0
  } catch (error: any) {
    // 静默失败，统计为辅助信息
  }
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
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

const viewTask = async (task: any) => {
  showDetailDialog.value = true
  detailLoading.value = true
  currentTask.value = task
  try {
    const res: any = await getTask(task.id)
    currentTask.value = res.data || res
  } catch (error: any) {
    ElMessage.error('加载任务详情失败')
  } finally {
    detailLoading.value = false
  }
}

const viewLogs = (task: any) => {
  currentTask.value = task
  taskLogs.value = []
  showLogsDialog.value = true
}

const loadLogs = async () => {
  if (!currentTask.value) return
  logsLoading.value = true
  try {
    const res: any = await getTaskLogs(currentTask.value.id, { page: 1, page_size: 100 })
    taskLogs.value = res.data?.items || res.items || res.data || []
  } catch (error: any) {
    ElMessage.error('加载任务日志失败')
    taskLogs.value = []
  } finally {
    logsLoading.value = false
  }
}

const cancelTask = (task: any) => {
  ElMessageBox.confirm(
    `确定要取消任务 "${task.name}" 吗？`,
    '确认取消',
    {
      confirmButtonText: '确定',
      cancelButtonText: '返回',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await cancelTaskApi(task.id)
      ElMessage.success('任务已取消')
      loadTasks()
      loadStats()
    } catch (error: any) {
      ElMessage.error(error.message || '取消任务失败')
    }
  }).catch(() => {})
}

const retryTask = (task: any) => {
  ElMessageBox.confirm(
    `确定要重试任务 "${task.name}" 吗？`,
    '确认重试',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    try {
      await retryTaskApi(task.id)
      ElMessage.success('任务已重新加入队列')
      loadTasks()
      loadStats()
    } catch (error: any) {
      ElMessage.error(error.message || '重试任务失败')
    }
  }).catch(() => {})
}

const deleteTask = (task: any) => {
  ElMessageBox.confirm(
    `确定要删除任务 "${task.name}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteTaskApi(task.id)
      ElMessage.success('删除成功')
      loadTasks()
      loadStats()
    } catch (error: any) {
      ElMessage.error(error.message || '删除失败')
    }
  }).catch(() => {})
}

const batchDelete = () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.length} 个任务吗？此操作不可恢复。`,
    '批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const ids = selectedRows.value.map((t: any) => t.id)
      await batchDeleteTasks(ids)
      ElMessage.success('批量删除成功')
      selectedRows.value = []
      loadTasks()
      loadStats()
    } catch (error: any) {
      ElMessage.error(error.message || '批量删除失败')
    }
  }).catch(() => {})
}

const batchRetry = async () => {
  const failedTasks = selectedRows.value.filter((t: any) => t.status === 'failed' || t.status === 'cancelled')
  if (failedTasks.length === 0) {
    ElMessage.warning('选中的任务中没有可重试的失败/取消任务')
    return
  }
  ElMessageBox.confirm(
    `确定要重试选中的 ${failedTasks.length} 个失败/取消任务吗？`,
    '批量重试',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    let successCount = 0
    let failCount = 0
    for (const task of failedTasks) {
      try {
        await retryTaskApi(task.id)
        successCount++
      } catch {
        failCount++
      }
    }
    ElMessage.success(`批量重试完成：成功 ${successCount} 个，失败 ${failCount} 个`)
    loadTasks()
    loadStats()
  }).catch(() => {})
}

const startAutoRefresh = () => {
  if (refreshTimer) return
  refreshTimer = setInterval(() => {
    const hasRunning = tasks.value.some((t: any) => t.status === 'running' || t.status === 'pending')
    if (hasRunning) {
      loadTasks()
      loadStats()
    }
  }, 5000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  loadTasks()
  loadStats()
  startAutoRefresh()
})

onBeforeUnmount(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.tasks-page {
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
  font-weight: 600;
  color: #1f2937;
}

.mini-stat-value.running {
  color: #409eff;
}

.mini-stat-value.pending {
  color: #909399;
}

.mini-stat-value.success {
  color: #67c23a;
}

.mini-stat-value.danger {
  color: #f56c6c;
}

.mini-stat-label {
  margin-top: 4px;
  font-size: 13px;
  color: #6b7280;
}

.tasks-list-card {
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

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-detail {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.items-info {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  line-height: 1.6;
}

.items-info .processed {
  color: #67c23a;
}

.items-info .failed {
  color: #f56c6c;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.error-text {
  color: #f56c6c;
  word-break: break-all;
}

.json-block {
  background: #f3f4f6;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 240px;
  overflow: auto;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.logs-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.log-task-name {
  font-weight: 600;
  margin-right: 12px;
  color: #1f2937;
}

.logs-container {
  max-height: 480px;
  overflow-y: auto;
  background: #1f2937;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Courier New', monospace;
}

.log-item {
  display: flex;
  align-items: flex-start;
  padding: 6px 0;
  border-bottom: 1px solid #374151;
  color: #d1d5db;
  font-size: 12px;
  line-height: 1.6;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #9ca3af;
  margin-right: 8px;
  white-space: nowrap;
  flex-shrink: 0;
}

.log-level {
  margin-right: 8px;
  flex-shrink: 0;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

.log-debug .log-message {
  color: #9ca3af;
}

.log-info .log-message {
  color: #d1d5db;
}

.log-warning .log-message {
  color: #fbbf24;
}

.log-error .log-message,
.log-critical .log-message {
  color: #f87171;
}
</style>
