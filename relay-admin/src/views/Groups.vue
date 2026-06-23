<template>
  <div class="groups-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分组管理</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建分组
          </el-button>
        </div>
      </template>

      <el-table :data="groups" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="分组名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="siteCount" label="站点数量" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.siteCount || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="editGroup(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteGroup(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑分组对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingGroup ? '编辑分组' : '新建分组'"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="groupForm" :rules="groupRules" ref="groupFormRef" label-width="100px">
        <el-form-item label="分组名称" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="groupForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分组描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getGroups, createGroup, deleteGroup as deleteGroupApi } from '@/api/sites'
import dayjs from 'dayjs'

const loading = ref(false)
const groups = ref([])
const showCreateDialog = ref(false)
const saving = ref(false)
const editingGroup = ref(null)
const groupFormRef = ref(null)

const groupForm = reactive({
  name: '',
  description: ''
})

const groupRules = {
  name: [
    { required: true, message: '请输入分组名称', trigger: 'blur' }
  ]
}

function formatTime(time) {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

async function loadGroups() {
  loading.value = true
  try {
    const result = await getGroups()
    if (result.success) {
      groups.value = result.groups
    }
  } catch (err) {
    console.error('Failed to load groups:', err)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  groupForm.name = ''
  groupForm.description = ''
  editingGroup.value = null
  if (groupFormRef.value) {
    groupFormRef.value.resetFields()
  }
}

function editGroup(row) {
  editingGroup.value = row
  groupForm.name = row.name
  groupForm.description = row.description || ''
  showCreateDialog.value = true
}

async function handleSave() {
  if (!groupFormRef.value) return
  
  try {
    await groupFormRef.value.validate()
  } catch (err) {
    return
  }
  
  saving.value = true
  
  try {
    const result = await createGroup(groupForm)
    if (result.success) {
      ElMessage.success(editingGroup.value ? '更新成功' : '创建成功')
      showCreateDialog.value = false
      loadGroups()
    } else {
      ElMessage.error(result.error || '操作失败')
    }
  } catch (err) {
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

async function deleteGroup(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除分组 "${row.name}" 吗？该分组下的站点将变为未分组状态。`,
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

  // 调用真实删除 API
  const groupId = row.group_id || row.id
  if (!groupId) {
    ElMessage.error('无法获取分组ID')
    return
  }

  try {
    const result = await deleteGroupApi(groupId)
    if (result.success) {
      ElMessage.success('删除成功')
      loadGroups()
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (err) {
    ElMessage.error('删除失败，请稍后重试')
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<style scoped lang="scss">
.groups-page {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
