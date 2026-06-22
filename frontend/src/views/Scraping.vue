<template>
  <div class="scraping-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>采集任务</h2>
          <p class="subtitle">可视化采集产品数据，支持反检测和代理</p>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建采集任务
        </el-button>
      </div>
    </el-card>

    <el-card class="tasks-card">
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" width="200" />
        <el-table-column prop="source_url" label="来源网站" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="row.status === '失败' ? 'exception' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="products" label="产品数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="viewTask(row)">查看</el-button>
            <el-button size="small" type="danger" @click="deleteTask(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建采集任务对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建采集任务" width="700px">
      <el-form :model="taskForm" label-width="120px">
        <el-form-item label="任务名称">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="起始URL">
          <el-input v-model="taskForm.start_url" placeholder="https://example.com/products" />
        </el-form-item>
        <el-form-item label="采集模板">
          <el-select v-model="taskForm.preset" placeholder="选择采集模板">
            <el-option label="WooCommerce" value="woocommerce" />
            <el-option label="Shopify" value="shopify" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大页数">
          <el-input-number v-model="taskForm.max_pages" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="最大产品数">
          <el-input-number v-model="taskForm.max_products" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="启用反检测">
          <el-switch v-model="taskForm.use_stealth" />
        </el-form-item>
        <el-form-item label="使用代理">
          <el-switch v-model="taskForm.use_proxy" />
        </el-form-item>
        <el-form-item label="下载图片">
          <el-switch v-model="taskForm.download_images" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask">开始采集</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const showCreateDialog = ref(false)

const taskForm = ref({
  name: '',
  start_url: '',
  preset: 'woocommerce',
  max_pages: 10,
  max_products: 100,
  use_stealth: true,
  use_proxy: true,
  download_images: true
})

const tasks = ref([
  {
    id: 1,
    name: '电子产品采集',
    source_url: 'https://example.com/electronics',
    status: '进行中',
    progress: 65,
    products: 65,
    created_at: '2024-01-15 10:30:00'
  },
  {
    id: 2,
    name: '服装产品采集',
    source_url: 'https://example.com/clothing',
    status: '已完成',
    progress: 100,
    products: 256,
    created_at: '2024-01-14 14:00:00'
  },
  {
    id: 3,
    name: '家居用品采集',
    source_url: 'https://example.com/home',
    status: '失败',
    progress: 45,
    products: 45,
    created_at: '2024-01-13 09:00:00'
  }
])

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

const createTask = () => {
  if (!taskForm.value.name || !taskForm.value.start_url) {
    ElMessage.error('请填写任务名称和起始URL')
    return
  }
  
  const newTask = {
    id: Date.now(),
    ...taskForm.value,
    source_url: taskForm.value.start_url,
    status: '进行中',
    progress: 0,
    products: 0,
    created_at: new Date().toLocaleString()
  }
  
  tasks.value.unshift(newTask)
  showCreateDialog.value = false
  ElMessage.success('采集任务已创建')
  
  // 重置表单
  taskForm.value = {
    name: '',
    start_url: '',
    preset: 'woocommerce',
    max_pages: 10,
    max_products: 100,
    use_stealth: true,
    use_proxy: true,
    download_images: true
  }
}
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

.tasks-card {
  border: none;
  border-radius: 8px;
}
</style>
