<template>
  <div class="settings-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>系统设置</h2>
          <p class="subtitle">配置系统参数和第三方服务</p>
        </div>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" tab-position="left">
      <el-tab-pane label="AI配置" name="ai">
        <el-card class="setting-card">
          <h3>AI提供商配置</h3>
          <el-table :data="aiProviders" style="width: 100%; margin-bottom: 20px;">
            <el-table-column prop="name" label="提供商" width="150" />
            <el-table-column prop="base_url" label="API地址" />
            <el-table-column prop="models" label="模型数量" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '已启用' : '未启用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="primary" text @click="editProvider(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" @click="showProviderDialog = true">
            <el-icon><Plus /></el-icon>
            添加AI提供商
          </el-button>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="代理配置" name="proxy">
        <el-card class="setting-card">
          <h3>代理池配置</h3>
          <el-form :model="proxySettings" label-width="120px">
            <el-form-item label="启用代理">
              <el-switch v-model="proxySettings.enabled" />
            </el-form-item>
            <el-form-item label="代理类型">
              <el-select v-model="proxySettings.type" style="width: 200px">
                <el-option label="HTTP/HTTPS" value="http" />
                <el-option label="SOCKS5" value="socks5" />
                <el-option label="BrightData" value="brightdata" />
                <el-option label="Oxylabs" value="oxylabs" />
                <el-option label="Smartproxy" value="smartproxy" />
              </el-select>
            </el-form-item>
            <el-form-item label="代理地址">
              <el-input v-model="proxySettings.host" placeholder="代理主机地址" style="width: 300px; margin-right: 10px;" />
              <el-input v-model="proxySettings.port" placeholder="端口" style="width: 100px;" />
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="proxySettings.username" placeholder="代理用户名" style="width: 300px;" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="proxySettings.password" type="password" placeholder="代理密码" style="width: 300px;" show-password />
            </el-form-item>
            <el-form-item label="默认国家">
              <el-select v-model="proxySettings.default_country" style="width: 200px">
                <el-option label="美国" value="US" />
                <el-option label="英国" value="UK" />
                <el-option label="德国" value="DE" />
                <el-option label="法国" value="FR" />
                <el-option label="匈牙利" value="HU" />
                <el-option label="罗马尼亚" value="RO" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveProxySettings">保存设置</el-button>
              <el-button @click="testProxy">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="翻译配置" name="translation">
        <el-card class="setting-card">
          <h3>翻译服务配置</h3>
          <el-form :model="translationSettings" label-width="120px">
            <el-form-item label="默认引擎">
              <el-select v-model="translationSettings.default_engine" style="width: 200px">
                <el-option label="AI翻译" value="ai" />
                <el-option label="Google翻译" value="google" />
                <el-option label="DeepL翻译" value="deepl" />
                <el-option label="百度翻译" value="baidu" />
                <el-option label="有道翻译" value="youdao" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认源语言">
              <el-select v-model="translationSettings.source_lang" style="width: 200px">
                <el-option label="自动检测" value="auto" />
                <el-option label="英语" value="en" />
                <el-option label="中文" value="zh-CN" />
                <el-option label="匈牙利语" value="hu" />
                <el-option label="罗马尼亚语" value="ro" />
                <el-option label="德语" value="de" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认目标语言">
              <el-select v-model="translationSettings.target_lang" style="width: 200px">
                <el-option label="中文" value="zh-CN" />
                <el-option label="英语" value="en" />
                <el-option label="匈牙利语" value="hu" />
                <el-option label="罗马尼亚语" value="ro" />
                <el-option label="德语" value="de" />
              </el-select>
            </el-form-item>
            <el-form-item label="启用术语库">
              <el-switch v-model="translationSettings.use_terms" />
            </el-form-item>
            <el-form-item label="启用翻译缓存">
              <el-switch v-model="translationSettings.use_cache" />
            </el-form-item>
            <el-form-item label="AI润色">
              <el-switch v-model="translationSettings.auto_polish" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveTranslationSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="价格配置" name="price">
        <el-card class="setting-card">
          <h3>价格与汇率配置</h3>
          <el-form :model="priceSettings" label-width="140px">
            <el-form-item label="默认定价策略">
              <el-select v-model="priceSettings.strategy" style="width: 200px">
                <el-option label="百分比加价" value="percentage_markup" />
                <el-option label="固定加价" value="fixed_markup" />
                <el-option label="阶梯定价" value="tiered_pricing" />
                <el-option label="竞争定价" value="competitive_pricing" />
                <el-option label="心理定价" value="psychological_pricing" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认加价比例">
              <el-input-number v-model="priceSettings.markup_percentage" :min="0" :max="200" :step="5" />
              <span style="margin-left: 10px;">%</span>
            </el-form-item>
            <el-form-item label="启用心理定价">
              <el-switch v-model="priceSettings.psychological_pricing" />
            </el-form-item>
            <el-form-item label="基础货币">
              <el-select v-model="priceSettings.base_currency" style="width: 200px">
                <el-option label="美元 USD" value="USD" />
                <el-option label="欧元 EUR" value="EUR" />
                <el-option label="英镑 GBP" value="GBP" />
                <el-option label="人民币 CNY" value="CNY" />
                <el-option label="匈牙利福林 HUF" value="HUF" />
                <el-option label="罗马尼亚列伊 RON" value="RON" />
              </el-select>
            </el-form-item>
            <el-form-item label="汇率缓存时间">
              <el-input-number v-model="priceSettings.cache_ttl" :min="60" :max="86400" :step="300" />
              <span style="margin-left: 10px;">秒</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="savePriceSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统设置" name="system">
        <el-card class="setting-card">
          <h3>系统设置</h3>
          <el-form :model="systemSettings" label-width="140px">
            <el-form-item label="调试模式">
              <el-switch v-model="systemSettings.debug" />
            </el-form-item>
            <el-form-item label="日志级别">
              <el-select v-model="systemSettings.log_level" style="width: 200px">
                <el-option label="DEBUG" value="DEBUG" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </el-form-item>
            <el-form-item label="最大并发任务">
              <el-input-number v-model="systemSettings.max_concurrent_tasks" :min="1" :max="20" />
            </el-form-item>
            <el-form-item label="任务超时时间">
              <el-input-number v-model="systemSettings.task_timeout" :min="60" :max="86400" :step="300" />
              <span style="margin-left: 10px;">秒</span>
            </el-form-item>
            <el-form-item label="上传文件大小限制">
              <el-input-number v-model="systemSettings.max_upload_size" :min="1" :max="1000" />
              <span style="margin-left: 10px;">MB</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSystemSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加AI提供商对话框 -->
    <el-dialog v-model="showProviderDialog" title="添加AI提供商" width="500px">
      <el-form :model="providerForm" label-width="100px">
        <el-form-item label="提供商名称">
          <el-input v-model="providerForm.name" placeholder="如：OpenAI" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="providerForm.api_key" type="password" placeholder="API密钥" show-password />
        </el-form-item>
        <el-form-item label="API地址">
          <el-input v-model="providerForm.base_url" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="默认模型">
          <el-input v-model="providerForm.default_model" placeholder="gpt-3.5-turbo" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProviderDialog = false">取消</el-button>
        <el-button type="primary" @click="addProvider">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('ai')
const showProviderDialog = ref(false)

const aiProviders = ref([
  { id: 1, name: 'OpenAI', base_url: 'https://api.openai.com/v1', models: 5, status: 'active' },
  { id: 2, name: 'Anthropic', base_url: 'https://api.anthropic.com/v1', models: 3, status: 'active' }
])

const providerForm = reactive({
  name: '',
  api_key: '',
  base_url: '',
  default_model: ''
})

const proxySettings = reactive({
  enabled: true,
  type: 'http',
  host: '',
  port: '',
  username: '',
  password: '',
  default_country: 'US'
})

const translationSettings = reactive({
  default_engine: 'ai',
  source_lang: 'auto',
  target_lang: 'zh-CN',
  use_terms: true,
  use_cache: true,
  auto_polish: false
})

const priceSettings = reactive({
  strategy: 'percentage_markup',
  markup_percentage: 30,
  psychological_pricing: true,
  base_currency: 'USD',
  cache_ttl: 3600
})

const systemSettings = reactive({
  debug: false,
  log_level: 'INFO',
  max_concurrent_tasks: 5,
  task_timeout: 3600,
  max_upload_size: 100
})

const editProvider = (provider: any) => {
  providerForm.name = provider.name
  providerForm.base_url = provider.base_url
  showProviderDialog.value = true
}

const addProvider = () => {
  if (!providerForm.name || !providerForm.api_key) {
    ElMessage.error('请填写提供商名称和API Key')
    return
  }
  
  aiProviders.value.push({
    id: Date.now(),
    name: providerForm.name,
    base_url: providerForm.base_url,
    models: 1,
    status: 'active'
  })
  
  showProviderDialog.value = false
  ElMessage.success('AI提供商添加成功')
  
  providerForm.name = ''
  providerForm.api_key = ''
  providerForm.base_url = ''
  providerForm.default_model = ''
}

const saveProxySettings = () => {
  ElMessage.success('代理设置已保存')
}

const testProxy = () => {
  ElMessage.info('正在测试代理连接...')
  setTimeout(() => {
    ElMessage.success('代理连接测试成功')
  }, 1500)
}

const saveTranslationSettings = () => {
  ElMessage.success('翻译设置已保存')
}

const savePriceSettings = () => {
  ElMessage.success('价格设置已保存')
}

const saveSystemSettings = () => {
  ElMessage.success('系统设置已保存')
}
</script>

<style scoped>
.settings-page {
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

.setting-card {
  border: none;
  border-radius: 8px;
}

.setting-card h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #1f2937;
}
</style>
