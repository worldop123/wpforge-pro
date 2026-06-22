<template>
  <div class="site-detail-page">
    <el-page-header @back="goBack" content="站点详情" />
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button type="primary" link @click="editing = true">编辑</el-button>
            </div>
          </template>
          
          <el-descriptions :column="2" border v-if="site">
            <el-descriptions-item label="站点ID">
              <code>{{ site.site_id }}</code>
            </el-descriptions-item>
            <el-descriptions-item label="站点名称">
              {{ site.site_name }}
            </el-descriptions-item>
            <el-descriptions-item label="站点URL" :span="2">
              <a :href="site.site_url" target="_blank">{{ site.site_url }}</a>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(site.status)" size="small">
                {{ getStatusText(site.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="分组">
              {{ site.group_id || '未分组' }}
            </el-descriptions-item>
            <el-descriptions-item label="最后在线">
              {{ site.last_seen ? formatTime(site.last_seen) : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatTime(site.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>最近事件</span>
          </template>
          <el-empty description="暂无事件数据" />
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>连接信息</span>
          </template>
          <div class="connection-info">
            <div class="info-item">
              <span class="label">连接状态</span>
              <el-tag :type="isOnline ? 'success' : 'info'" size="small">
                {{ isOnline ? '在线' : '离线' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">站点Token</span>
              <div class="token-display">
                <code>{{ maskedToken }}</code>
                <el-button type="primary" link size="small" @click="showToken = !showToken">
                  {{ showToken ? '隐藏' : '显示' }}
                </el-button>
              </div>
            </div>
            <div class="info-item">
              <el-button type="warning" style="width: 100%" @click="handleRegenerateToken">
                重新生成Token
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top: 20px;">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" style="width: 100%; margin-bottom: 10px;">
              发送指令
            </el-button>
            <el-button type="success" style="width: 100%; margin-bottom: 10px;">
              查看消息历史
            </el-button>
            <el-button type="danger" style="width: 100%;" @click="handleDelete">
              删除站点
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSite, regenerateToken, deleteSite as apiDeleteSite } from '@/api/sites'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const site = ref(null)
const editing = ref(false)
const showToken = ref(false)

const isOnline = computed(() => site.value?.status === 'online')

const maskedToken = computed(() => {
  if (!site.value?.token) return ''
  if (showToken.value) return site.value.token
  const token = site.value.token
  return token.substring(0, 8) + '...' + token.substring(token.length - 8)
})

function getStatusType(status) {
  const typeMap = {
    online: 'success',
    offline: 'info',
    disabled: 'danger'
  }
  return typeMap[status] || 'info'
}

function getStatusText(status) {
  const textMap = {
    online: '在线',
    offline: '离线',
    disabled: '已禁用'
  }
  return textMap[status] || status
}

function formatTime(time) {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

function goBack() {
  router.push('/sites')
}

async function loadSite() {
  try {
    const result = await getSite(route.params.siteId)
    if (result.success) {
      site.value = result.site
    }
  } catch (err) {
    console.error('Failed to load site:', err)
  }
}

async function handleRegenerateToken() {
  try {
    await ElMessageBox.confirm(
      '确定要重新生成Token吗？旧Token将立即失效。',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch (err) {
    return
  }

  try {
    const result = await regenerateToken(route.params.siteId)
    if (result.success) {
      ElMessage.success('Token已重新生成')
      site.value.token = result.token
    }
  } catch (err) {
    ElMessage.error('重置失败')
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      '确定要删除此站点吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch (err) {
    return
  }

  try {
    const result = await apiDeleteSite(route.params.siteId)
    if (result.success) {
      ElMessage.success('删除成功')
      router.push('/sites')
    }
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadSite()
})
</script>

<style scoped lang="scss">
.site-detail-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .connection-info {
    .info-item {
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

      .token-display {
        display: flex;
        align-items: center;
        gap: 8px;

        code {
          font-size: 12px;
          background: #f5f7fa;
          padding: 2px 6px;
          border-radius: 4px;
        }
      }
    }
  }

  .quick-actions {
    display: flex;
    flex-direction: column;
  }
}
</style>
