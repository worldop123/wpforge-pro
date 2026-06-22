<template>
  <div class="messages-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>消息历史</span>
          <el-button type="primary" @click="loadMessages">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="消息类型">
          <el-select v-model="filterForm.messageType" placeholder="全部类型" clearable style="width: 150px">
            <el-option label="指令" value="command" />
            <el-option label="事件" value="event" />
            <el-option label="响应" value="response" />
            <el-option label="广播" value="broadcast" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="filterForm.sourceId" placeholder="来源ID" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadMessages">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 消息列表 -->
      <el-table :data="messages" v-loading="loading" stripe>
        <el-table-column prop="messageId" label="消息ID" width="200">
          <template #default="{ row }">
            <code class="msg-id">{{ row.messageId }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="messageType" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.messageType)" size="small">
              {{ getTypeText(row.messageType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sourceId" label="来源" width="150" />
        <el-table-column prop="targetId" label="目标" width="150">
          <template #default="{ row }">
            {{ row.targetId || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createdAt) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="filterForm.page"
          v-model:page-size="filterForm.pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadMessages"
          @current-change="loadMessages"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { getMessageHistory } from '@/api/sites'
import dayjs from 'dayjs'

const loading = ref(false)
const messages = ref([])
const total = ref(0)

const filterForm = reactive({
  messageType: '',
  sourceId: '',
  page: 1,
  pageSize: 20
})

function getTypeTag(type) {
  const tagMap = {
    command: 'primary',
    event: 'success',
    response: 'warning',
    broadcast: 'info'
  }
  return tagMap[type] || 'info'
}

function getTypeText(type) {
  const textMap = {
    command: '指令',
    event: '事件',
    response: '响应',
    broadcast: '广播'
  }
  return textMap[type] || type
}

function getStatusTag(status) {
  const tagMap = {
    sent: 'success',
    queued: 'warning',
    failed: 'danger'
  }
  return tagMap[status] || 'info'
}

function getStatusText(status) {
  const textMap = {
    sent: '已发送',
    queued: '队列中',
    failed: '失败'
  }
  return textMap[status] || status
}

function formatTime(time) {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

async function loadMessages() {
  loading.value = true
  try {
    const result = await getMessageHistory(filterForm)
    if (result.success) {
      messages.value = result.messages
      total.value = result.total
    }
  } catch (err) {
    console.error('Failed to load messages:', err)
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  filterForm.messageType = ''
  filterForm.sourceId = ''
  filterForm.page = 1
  loadMessages()
}

onMounted(() => {
  loadMessages()
})
</script>

<style scoped lang="scss">
.messages-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-form {
    margin-bottom: 20px;
  }

  .msg-id {
    font-family: monospace;
    font-size: 12px;
    background: #f5f7fa;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
