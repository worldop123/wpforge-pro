<template>
  <div class="sites-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>站点管理</h2>
          <p class="subtitle">管理您的WordPress站点，配置连接信息</p>
        </div>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加站点
        </el-button>
      </div>
    </el-card>

    <el-card class="sites-list-card">
      <el-table :data="sites" style="width: 100%">
        <el-table-column prop="name" label="站点名称" width="200" />
        <el-table-column prop="url" label="站点地址" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'connected' ? 'success' : 'danger'">
              {{ row.status === 'connected' ? '已连接' : '未连接' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="products" label="产品数" width="100" />
        <el-table-column prop="last_sync" label="最后同步" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="testConnection(row)">测试连接</el-button>
            <el-button size="small" type="primary" @click="editSite(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteSite(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑站点对话框 -->
    <el-dialog v-model="showAddDialog" title="添加WordPress站点" width="600px">
      <el-form :model="siteForm" label-width="120px">
        <el-form-item label="站点名称">
          <el-input v-model="siteForm.name" placeholder="请输入站点名称" />
        </el-form-item>
        <el-form-item label="站点地址">
          <el-input v-model="siteForm.url" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="siteForm.username" placeholder="WordPress用户名" />
        </el-form-item>
        <el-form-item label="应用密码">
          <el-input v-model="siteForm.app_password" type="password" placeholder="应用密码" show-password />
        </el-form-item>
        <el-form-item label="WooCommerce Key">
          <el-input v-model="siteForm.wc_consumer_key" placeholder="Consumer Key" />
        </el-form-item>
        <el-form-item label="WooCommerce Secret">
          <el-input v-model="siteForm.wc_consumer_secret" type="password" placeholder="Consumer Secret" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSite">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const showAddDialog = ref(false)

const siteForm = ref({
  name: '',
  url: '',
  username: '',
  app_password: '',
  wc_consumer_key: '',
  wc_consumer_secret: ''
})

const sites = ref([
  {
    id: 1,
    name: '主站 - BangVape',
    url: 'https://bangvape.com',
    status: 'connected',
    products: 1256,
    last_sync: '2024-01-15 10:30:00'
  },
  {
    id: 2,
    name: '匈牙利站点',
    url: 'https://bangvape.hu',
    status: 'connected',
    products: 856,
    last_sync: '2024-01-14 16:45:00'
  },
  {
    id: 3,
    name: '罗马尼亚站点',
    url: 'https://bangvape.ro',
    status: 'disconnected',
    products: 0,
    last_sync: '-'
  }
])

const testConnection = async (site: any) => {
  ElMessage.info(`正在测试 ${site.name} 的连接...`)
  // 模拟测试
  setTimeout(() => {
    ElMessage.success(`${site.name} 连接成功`)
  }, 1000)
}

const editSite = (site: any) => {
  siteForm.value = { ...site }
  showAddDialog.value = true
}

const deleteSite = (site: any) => {
  ElMessageBox.confirm(
    `确定要删除站点 "${site.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    sites.value = sites.value.filter(s => s.id !== site.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const saveSite = () => {
  if (!siteForm.value.name || !siteForm.value.url) {
    ElMessage.error('请填写站点名称和地址')
    return
  }
  
  // 模拟保存
  const newSite = {
    id: Date.now(),
    ...siteForm.value,
    status: 'connected',
    products: 0,
    last_sync: new Date().toLocaleString()
  }
  
  sites.value.push(newSite)
  showAddDialog.value = false
  ElMessage.success('站点添加成功')
  
  // 重置表单
  siteForm.value = {
    name: '',
    url: '',
    username: '',
    app_password: '',
    wc_consumer_key: '',
    wc_consumer_secret: ''
  }
}
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

.sites-list-card {
  border: none;
  border-radius: 8px;
}
</style>
