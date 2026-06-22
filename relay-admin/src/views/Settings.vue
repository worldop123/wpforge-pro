<template>
  <div class="settings-page">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本设置" name="basic">
          <el-form label-width="150px" class="settings-form">
            <el-form-item label="服务器地址">
              <el-input v-model="settings.serverUrl" placeholder="wss://relay.example.com" />
            </el-form-item>
            <el-form-item label="心跳间隔(秒)">
              <el-input-number v-model="settings.heartbeatInterval" :min="10" :max="300" />
            </el-form-item>
            <el-form-item label="消息最大大小(MB)">
              <el-input-number v-model="settings.maxMessageSize" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="离线消息保留(天)">
              <el-input-number v-model="settings.offlineMessageTtl" :min="1" :max="30" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="安全设置" name="security">
          <el-form label-width="150px" class="settings-form">
            <el-form-item label="启用限流">
              <el-switch v-model="settings.rateLimitEnabled" />
            </el-form-item>
            <el-form-item label="每秒消息数限制">
              <el-input-number v-model="settings.rateLimitPoints" :min="10" :max="1000" />
            </el-form-item>
            <el-form-item label="封禁时长(秒)">
              <el-input-number v-model="settings.rateLimitBlockDuration" :min="10" :max="3600" />
            </el-form-item>
            <el-form-item label="JWT有效期">
              <el-input v-model="settings.jwtExpiresIn" placeholder="7d" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="管理员" name="admins">
          <el-button type="primary" style="margin-bottom: 20px">
            <el-icon><Plus /></el-icon>
            添加管理员
          </el-button>
          <el-table :data="admins" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="200" />
            <el-table-column prop="role" label="角色" width="150">
              <template #default="{ row }">
                <el-tag :type="row.role === 'super_admin' ? 'danger' : 'primary'" size="small">
                  {{ row.role === 'super_admin' ? '超级管理员' : '管理员' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link size="small">编辑</el-button>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="IP黑名单" name="blacklist">
          <el-button type="primary" style="margin-bottom: 20px">
            <el-icon><Plus /></el-icon>
            添加IP
          </el-button>
          <el-table :data="blacklist" stripe>
            <el-table-column prop="ip_address" label="IP地址" width="200" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="expires_at" label="过期时间" width="200">
              <template #default="{ row }">
                {{ row.expires_at || '永久' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="添加时间" width="200" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="danger" link size="small">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('basic')

const settings = reactive({
  serverUrl: '',
  heartbeatInterval: 30,
  maxMessageSize: 1,
  offlineMessageTtl: 7,
  rateLimitEnabled: true,
  rateLimitPoints: 100,
  rateLimitBlockDuration: 60,
  jwtExpiresIn: '7d'
})

const admins = ref([
  { id: 1, username: 'admin', role: 'super_admin', created_at: '2024-01-01 00:00:00' }
])

const blacklist = ref([])

function saveSettings() {
  ElMessage.success('设置保存成功')
}
</script>

<style scoped lang="scss">
.settings-page {
  .settings-form {
    max-width: 600px;
  }
}
</style>
