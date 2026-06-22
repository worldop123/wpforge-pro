<template>
  <div class="sites-page">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="站点名称/URL/ID"
            clearable
            style="width: 250px"
            @keyup.enter="loadSites"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
            <el-option label="已禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="分组">
          <el-select v-model="searchForm.groupId" placeholder="全部分组" clearable style="width: 150px">
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadSites">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
        <el-form-item style="margin-left: auto">
          <el-button type="primary" @click="showRegisterDialog = true">
            <el-icon><Plus /></el-icon>
            注册站点
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 站点列表 -->
    <el-card class="list-card">
      <el-table :data="sites" v-loading="loading" stripe>
        <el-table-column prop="site_id" label="站点ID" width="180">
          <template #default="{ row }">
            <code class="site-id">{{ row.site_id }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="site_name" label="站点名称" min-width="150" />
        <el-table-column prop="site_url" label="站点URL" min-width="200">
          <template #default="{ row }">
            <a :href="row.site_url" target="_blank" class="site-url">
              {{ row.site_url }}
            </a>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_seen" label="最后在线" width="180">
          <template #default="{ row }">
            {{ row.last_seen ? formatTime(row.last_seen) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="warning" link @click="regenerateToken(row)">
              重置Token
            </el-button>
            <el-button type="danger" link @click="deleteSite(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadSites"
          @current-change="loadSites"
        />
      </div>
    </el-card>

    <!-- 注册站点对话框 -->
    <el-dialog
      v-model="showRegisterDialog"
      title="注册新站点"
      width="500px"
      @close="resetRegisterForm"
    >
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="100px">
        <el-form-item label="站点名称" prop="siteName">
          <el-input v-model="registerForm.siteName" placeholder="请输入站点名称" />
        </el-form-item>
        <el-form-item label="站点URL" prop="siteUrl">
          <el-input v-model="registerForm.siteUrl" placeholder="https://example.com" />
        </el-form-item>
        <el-form-item label="分组">
          <el-select v-model="registerForm.groupId" placeholder="选择分组" clearable style="width: 100%">
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegisterDialog = false">取消</el-button>
        <el-button type="primary" :loading="registering" @click="handleRegister">
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getSites, registerSite, deleteSite as apiDeleteSite, regenerateToken as apiRegenerateToken, getGroups } from '@/api/sites'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const sites = ref([])
const total = ref(0)
const groups = ref([])

const searchForm = reactive({
  search: '',
  status: '',
  groupId: '',
  page: 1,
  pageSize: 20
})

const showRegisterDialog = ref(false)
const registering = ref(false)
const registerFormRef = ref(null)
const registerForm = reactive({
  siteName: '',
  siteUrl: '',
  groupId: null
})

const registerRules = {
  siteName: [
    { required: true, message: '请输入站点名称', trigger: 'blur' }
  ],
  siteUrl: [
    { required: true, message: '请输入站点URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ]
}

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

async function loadSites() {
  loading.value = true
  try {
    const result = await getSites(searchForm)
    if (result.success) {
      sites.value = result.sites
      total.value = result.total
    }
  } catch (err) {
    console.error('Failed to load sites:', err)
  } finally {
    loading.value = false
  }
}

async function loadGroups() {
  try {
    const result = await getGroups()
    if (result.success) {
      groups.value = result.groups
    }
  } catch (err) {
    console.error('Failed to load groups:', err)
  }
}

function resetSearch() {
  searchForm.search = ''
  searchForm.status = ''
  searchForm.groupId = ''
  searchForm.page = 1
  loadSites()
}

function resetRegisterForm() {
  registerForm.siteName = ''
  registerForm.siteUrl = ''
  registerForm.groupId = null
  if (registerFormRef.value) {
    registerFormRef.value.resetFields()
  }
}

async function handleRegister() {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
  } catch (err) {
    return
  }
  
  registering.value = true
  
  try {
    const result = await registerSite(registerForm)
    if (result.success) {
      ElMessage.success(`站点注册成功！站点ID: ${result.siteId}`)
      showRegisterDialog.value = false
      loadSites()
    } else {
      ElMessage.error(result.error || '注册失败')
    }
  } catch (err) {
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    registering.value = false
  }
}

function viewDetail(row) {
  router.push(`/sites/${row.site_id}`)
}

async function regenerateToken(row) {
  try {
    await ElMessageBox.confirm(
      `确定要重置站点 "${row.site_name}" 的Token吗？重置后旧Token将失效。`,
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
    const result = await apiRegenerateToken(row.site_id)
    if (result.success) {
      ElMessage.success(`Token重置成功！新Token: ${result.token}`)
    }
  } catch (err) {
    ElMessage.error('重置失败')
  }
}

async function deleteSite(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除站点 "${row.site_name}" 吗？此操作不可恢复。`,
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
    const result = await apiDeleteSite(row.site_id)
    if (result.success) {
      ElMessage.success('删除成功')
      loadSites()
    }
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadSites()
  loadGroups()
})
</script>

<style scoped lang="scss">
.sites-page {
  .search-card {
    margin-bottom: 20px;
  }

  .list-card {
    .site-id {
      font-family: monospace;
      font-size: 12px;
      background: #f5f7fa;
      padding: 2px 6px;
      border-radius: 4px;
    }

    .site-url {
      color: #409eff;
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
