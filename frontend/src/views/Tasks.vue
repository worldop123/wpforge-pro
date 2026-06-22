<template>
  <div class="tasks-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>任务中心</h2>
          <p class="subtitle">查看和管理所有任务</p>
        </div>
      </div>
    </el-card>

    <el-card class="tasks-card">
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" width="200" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === '失败' ? 'exception' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" text @click="viewTask(row)">详情</el-button>
            <el-button size="small" type="danger" text @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const tasks = ref([
  { id: 1, name: '电子产品采集', type: '采集', status: '进行中', progress: 65, created_at: '2024-01-15 10:30:00', duration: '5m 30s' },
  { id: 2, name: '英文产品翻译', type: '翻译', status: '已完成', progress: 100, created_at: '2024-01-15 09:00:00', duration: '12m 15s' },
  { id: 3, name: 'WooCommerce批量导入', type: '导入', status: '已完成', progress: 100, created_at: '2024-01-14 16:45:00', duration: '8m 45s' },
  { id: 4, name: 'SEO批量优化', type: 'SEO', status: '失败', progress: 45, created_at: '2024-01-14 14:20:00', duration: '3m 20s' },
  { id: 5, name: '价格批量计算', type: '价格', status: '已完成', progress: 100, created_at: '2024-01-14 11:00:00', duration: '1m 30s' },
  { id: 6, name: '服装产品采集', type: '采集', status: '已完成', progress: 100, created_at: '2024-01-13 15:00:00', duration: '25m 00s' },
  { id: 7, name: '匈牙利语翻译', type: '翻译', status: '进行中', progress: 30, created_at: '2024-01-15 11:00:00', duration: '2m 15s' },
  { id: 8, name: '图片批量压缩', type: '优化', status: '等待中', progress: 0, created_at: '2024-01-15 10:45:00', duration: '-' }
])

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    '采集': 'primary',
    '翻译': 'success',
    '导入': 'warning',
    'SEO': 'info',
    '价格': '',
    '优化': 'danger'
  }
  return map[type] || ''
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '失败': 'danger',
    '等待中': 'info'
  }
  return map[status] || ''
}

const viewTask = (task: any) => {
  ElMessage.info(`查看任务: ${task.name}`)
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

.tasks-card {
  border: none;
  border-radius: 8px;
}
</style>
