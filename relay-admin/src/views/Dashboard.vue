<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.sites?.totalSites || 0 }}</div>
              <div class="stat-label">总站点数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.sites?.onlineSites || 0 }}</div>
              <div class="stat-label">在线站点</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon><Message /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.messages?.messagesToday || 0 }}</div>
              <div class="stat-label">今日消息</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c;">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.messages?.pendingMessages || 0 }}</div>
              <div class="stat-label">待处理消息</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 客户端连接统计 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>客户端连接</span>
          </template>
          <div class="client-stats">
            <div class="client-stat-item">
              <span class="label">管理端</span>
              <span class="value">{{ stats.clients?.admin || 0 }}</span>
            </div>
            <div class="client-stat-item">
              <span class="label">插件端</span>
              <span class="value">{{ stats.clients?.plugin || 0 }}</span>
            </div>
            <div class="client-stat-item">
              <span class="label">管理面板</span>
              <span class="value">{{ stats.clients?.adminPanel || 0 }}</span>
            </div>
            <div class="client-stat-item">
              <span class="label">总连接数</span>
              <span class="value">{{ stats.clients?.total || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>站点状态分布</span>
          </template>
          <div class="site-stats">
            <div class="site-stat-item">
              <span class="label">在线</span>
              <el-progress :percentage="onlinePercentage" :color="'#67c23a'" />
              <span class="count">{{ stats.sites?.onlineSites || 0 }}</span>
            </div>
            <div class="site-stat-item">
              <span class="label">离线</span>
              <el-progress :percentage="offlinePercentage" :color="'#909399'" />
              <span class="count">{{ stats.sites?.offlineSites || 0 }}</span>
            </div>
            <div class="site-stat-item">
              <span class="label">已禁用</span>
              <el-progress :percentage="disabledPercentage" :color="'#f56c6c'" />
              <span class="count">{{ stats.sites?.disabledSites || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近事件 -->
    <el-row :gutter="20" class="events-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实时事件流</span>
              <el-button type="primary" link @click="clearEvents">清空</el-button>
            </div>
          </template>
          
          <div class="event-list" ref="eventListRef">
            <div v-if="events.length === 0" class="empty-events">
              <el-empty description="暂无事件" />
            </div>
            <div
              v-for="(event, index) in events"
              :key="index"
              class="event-item"
            >
              <div class="event-time">{{ formatTime(event.timestamp) }}</div>
              <div class="event-content">
                <el-tag :type="getEventTypeTag(event.event)" size="small">
                  {{ event.event }}
                </el-tag>
                <span class="event-source">来自 {{ event.source }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { getStats } from '@/api/sites'
import { io } from 'socket.io-client'
import { useAuthStore } from '@/store/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()

const stats = reactive({
  clients: {},
  sites: {},
  messages: {}
})

const events = ref([])
const eventListRef = ref(null)

let socket = null
let statsInterval = null

const onlinePercentage = computed(() => {
  const total = stats.sites?.totalSites || 1
  const online = stats.sites?.onlineSites || 0
  return Math.round((online / total) * 100)
})

const offlinePercentage = computed(() => {
  const total = stats.sites?.totalSites || 1
  const offline = stats.sites?.offlineSites || 0
  return Math.round((offline / total) * 100)
})

const disabledPercentage = computed(() => {
  const total = stats.sites?.totalSites || 1
  const disabled = stats.sites?.disabledSites || 0
  return Math.round((disabled / total) * 100)
})

async function loadStats() {
  try {
    const result = await getStats()
    if (result.success) {
      Object.assign(stats.clients, result.stats.clients || {})
      Object.assign(stats.sites, result.stats.sites || {})
      Object.assign(stats.messages, result.stats.messages || {})
    }
  } catch (err) {
    console.error('Failed to load stats:', err)
  }
}

function formatTime(timestamp) {
  return dayjs(timestamp).format('HH:mm:ss')
}

function getEventTypeTag(eventType) {
  const typeMap = {
    'new_order': 'success',
    'order_status_changed': 'warning',
    'product_updated': 'info',
    'error': 'danger',
    'comment': 'success'
  }
  return typeMap[eventType] || 'info'
}

function addEvent(event) {
  events.value.unshift(event)
  if (events.value.length > 50) {
    events.value.pop()
  }
  
  nextTick(() => {
    if (eventListRef.value) {
      eventListRef.value.scrollTop = 0
    }
  })
}

function clearEvents() {
  events.value = []
}

function initSocket() {
  const token = authStore.getToken()
  socket = io({
    auth: {
      clientType: 'admin_panel',
      credentials: {
        jwtToken: token
      }
    }
  })

  socket.on('event', (data) => {
    addEvent(data)
  })

  socket.on('client_connected', (data) => {
    addEvent({
      event: 'client_connected',
      source: data.type,
      timestamp: new Date().toISOString()
    })
    loadStats()
  })

  socket.on('client_disconnected', (data) => {
    addEvent({
      event: 'client_disconnected',
      source: data.type,
      timestamp: new Date().toISOString()
    })
    loadStats()
  })
}

onMounted(() => {
  loadStats()
  initSocket()
  
  // 每30秒刷新一次统计
  statsInterval = setInterval(loadStats, 30000)
})

onUnmounted(() => {
  if (socket) {
    socket.disconnect()
  }
  if (statsInterval) {
    clearInterval(statsInterval)
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .stat-icon {
      width: 50px;
      height: 50px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 24px;
    }

    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        line-height: 1.2;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;
  }

  .client-stats {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .client-stat-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #ebeef5;

      &:last-child {
        border-bottom: none;
      }

      .label {
        color: #606266;
        font-size: 14px;
      }

      .value {
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
    }
  }

  .site-stats {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .site-stat-item {
      display: flex;
      align-items: center;
      gap: 16px;

      .label {
        width: 60px;
        color: #606266;
        font-size: 14px;
      }

      .count {
        width: 50px;
        text-align: right;
        color: #303133;
        font-weight: 500;
      }

      :deep(.el-progress) {
        flex: 1;
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .event-list {
    max-height: 400px;
    overflow-y: auto;

    .empty-events {
      padding: 40px 0;
    }

    .event-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 12px 0;
      border-bottom: 1px solid #f2f6fc;

      &:last-child {
        border-bottom: none;
      }

      .event-time {
        color: #909399;
        font-size: 12px;
        font-family: monospace;
        min-width: 70px;
      }

      .event-content {
        display: flex;
        align-items: center;
        gap: 12px;

        .event-source {
          color: #606266;
          font-size: 14px;
        }
      }
    }
  }
}
</style>
