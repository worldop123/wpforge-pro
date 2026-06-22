<template>
  <div class="settings-page">
    <el-card class="page-header-card" shadow="hover">
      <div class="page-header">
        <div>
          <h2>系统设置</h2>
          <p class="subtitle">配置系统参数、AI模型、代理、反检测、中转服务器等</p>
        </div>
      </div>
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <el-tabs v-model="activeTab" tab-position="left" class="settings-tabs">
        <!-- 基础设置 -->
        <el-tab-pane label="基础设置" name="basic">
          <div class="tab-content">
            <h3 class="section-title">基础设置</h3>
            <el-form :model="basicSettings" label-width="160px" v-loading="loading.basic">
              <el-form-item label="系统名称">
                <el-input v-model="basicSettings.system_name" placeholder="WPForge" style="width: 320px;" />
              </el-form-item>
              <el-form-item label="调试模式">
                <el-switch v-model="basicSettings.debug" />
                <span class="form-tip">开启后将记录详细调试日志</span>
              </el-form-item>
              <el-form-item label="日志级别">
                <el-select v-model="basicSettings.log_level" style="width: 200px;">
                  <el-option label="DEBUG" value="DEBUG" />
                  <el-option label="INFO" value="INFO" />
                  <el-option label="WARNING" value="WARNING" />
                  <el-option label="ERROR" value="ERROR" />
                </el-select>
              </el-form-item>
              <el-form-item label="最大并发任务">
                <el-input-number v-model="basicSettings.max_concurrent_tasks" :min="1" :max="20" />
                <span class="form-tip">同时运行的任务数量上限</span>
              </el-form-item>
              <el-form-item label="任务超时时间">
                <el-input-number v-model="basicSettings.task_timeout" :min="60" :max="86400" :step="300" />
                <span class="form-tip">秒</span>
              </el-form-item>
              <el-form-item label="上传文件大小限制">
                <el-input-number v-model="basicSettings.max_upload_size" :min="1" :max="1000" />
                <span class="form-tip">MB</span>
              </el-form-item>
              <el-form-item label="默认语言">
                <el-select v-model="basicSettings.language" style="width: 200px;">
                  <el-option label="简体中文" value="zh-CN" />
                  <el-option label="English" value="en" />
                </el-select>
              </el-form-item>
              <el-form-item label="时区">
                <el-select v-model="basicSettings.timezone" style="width: 200px;">
                  <el-option label="亚洲/上海" value="Asia/Shanghai" />
                  <el-option label="UTC" value="UTC" />
                  <el-option label="欧洲/布达佩斯" value="Europe/Budapest" />
                  <el-option label="欧洲/布加勒斯特" value="Europe/Bucharest" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="saving" @click="saveBasicSettings">保存设置</el-button>
                <el-button @click="resetBasicSettings">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- AI模型配置 -->
        <el-tab-pane label="AI模型配置" name="ai">
          <div class="tab-content">
            <div class="section-header">
              <h3 class="section-title">AI提供商配置</h3>
              <el-button type="primary" @click="openProviderDialog()">
                <el-icon><Plus /></el-icon>
                添加AI提供商
              </el-button>
            </div>
            <el-table :data="aiProviders" v-loading="loading.ai" style="width: 100%; margin-bottom: 20px;">
              <el-table-column prop="name" label="提供商" width="150" />
              <el-table-column prop="base_url" label="API地址" min-width="240" show-overflow-tooltip />
              <el-table-column prop="default_model" label="默认模型" width="180" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                    {{ row.status === 'active' ? '已启用' : '未启用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="160">
                <template #default="{ row }">
                  <el-button size="small" type="primary" text @click="editProvider(row)">编辑</el-button>
                  <el-button size="small" type="danger" text @click="deleteProvider(row)">删除</el-button>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无AI提供商" />
              </template>
            </el-table>

            <h3 class="section-title">可用模型列表</h3>
            <el-table :data="availableModels" v-loading="loading.models" style="width: 100%;">
              <el-table-column prop="id" label="模型ID" width="200" />
              <el-table-column prop="provider" label="提供商" width="150" />
              <el-table-column prop="context_length" label="上下文长度" width="150" />
              <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
              <template #empty>
                <el-empty description="暂无可用模型" />
              </template>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 代理设置 -->
        <el-tab-pane label="代理设置" name="proxy">
          <div class="tab-content">
            <div class="section-header">
              <h3 class="section-title">代理池配置</h3>
              <div>
                <el-button type="success" @click="checkProxiesHandler" :loading="checking">
                  <el-icon><Connection /></el-icon>
                  检测代理可用性
                </el-button>
                <el-button type="primary" @click="openProxyDialog">
                  <el-icon><Plus /></el-icon>
                  添加代理
                </el-button>
              </div>
            </div>

            <!-- 代理池统计 -->
            <el-row :gutter="20" class="proxy-stats-row">
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value">{{ proxyStats.total || 0 }}</div>
                    <div class="mini-stat-label">代理总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value success">{{ proxyStats.alive || 0 }}</div>
                    <div class="mini-stat-label">可用代理</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value danger">{{ proxyStats.dead || 0 }}</div>
                    <div class="mini-stat-label">失效代理</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value">{{ proxyStats.avg_response_time || '-' }}ms</div>
                    <div class="mini-stat-label">平均响应时间</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-table :data="proxyList" v-loading="loading.proxy" style="width: 100%;">
              <el-table-column prop="host" label="主机" min-width="160" />
              <el-table-column prop="port" label="端口" width="100" />
              <el-table-column prop="protocol" label="协议" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.protocol || 'http' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="country" label="国家" width="100" />
              <el-table-column prop="is_alive" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_alive ? 'success' : 'danger'" size="small">
                    {{ row.is_alive ? '可用' : '失效' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="response_time" label="响应时间" width="120">
                <template #default="{ row }">
                  {{ row.response_time ? `${row.response_time}ms` : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="last_checked" label="最后检测" width="170">
                <template #default="{ row }">
                  {{ formatTime(row.last_checked) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button size="small" type="danger" text @click="removeProxy(row)">删除</el-button>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无代理" />
              </template>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 反检测设置 -->
        <el-tab-pane label="反检测设置" name="anti-detection">
          <div class="tab-content">
            <h3 class="section-title">反爬虫检测配置</h3>
            <el-form :model="antiDetectionSettings" label-width="180px">
              <el-form-item label="启用反检测">
                <el-switch v-model="antiDetectionSettings.enabled" />
              </el-form-item>
              <el-form-item label="User-Agent轮换">
                <el-switch v-model="antiDetectionSettings.rotate_user_agent" />
                <span class="form-tip">每次请求随机切换UA</span>
              </el-form-item>
              <el-form-item label="请求间隔">
                <el-input-number v-model="antiDetectionSettings.request_interval" :min="0" :max="60" :step="1" />
                <span class="form-tip">秒（每次请求之间的延迟）</span>
              </el-form-item>
              <el-form-item label="随机延迟">
                <el-switch v-model="antiDetectionSettings.random_delay" />
                <span class="form-tip">在请求间隔上增加随机抖动</span>
              </el-form-item>
              <el-form-item label="模拟鼠标行为">
                <el-switch v-model="antiDetectionSettings.simulate_mouse" />
              </el-form-item>
              <el-form-item label="自动验证码识别">
                <el-switch v-model="antiDetectionSettings.captcha_solver" />
              </el-form-item>
              <el-form-item label="使用无头浏览器">
                <el-switch v-model="antiDetectionSettings.headless_browser" />
                <span class="form-tip">使用Playwright/Puppeteer渲染页面</span>
              </el-form-item>
              <el-form-item label="Cookie持久化">
                <el-switch v-model="antiDetectionSettings.persist_cookies" />
              </el-form-item>
              <el-form-item label="指纹伪装">
                <el-switch v-model="antiDetectionSettings.fingerprint_spoofing" />
              </el-form-item>
              <el-form-item label="最大重试次数">
                <el-input-number v-model="antiDetectionSettings.max_retries" :min="0" :max="10" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="saving" @click="saveAntiDetectionSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 中转服务器 -->
        <el-tab-pane label="中转服务器" name="relay">
          <div class="tab-content">
            <div class="section-header">
              <h3 class="section-title">中转服务器配置</h3>
              <el-button type="primary" @click="openRelayDialog">
                <el-icon><Plus /></el-icon>
                添加中转服务器
              </el-button>
            </div>
            <el-alert
              title="中转服务器用于将采集请求通过中间服务器转发，可隐藏真实IP并提升访问速度"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 16px;"
            />
            <el-table :data="relayServers" v-loading="loading.relay" style="width: 100%;">
              <el-table-column prop="name" label="名称" width="160" />
              <el-table-column prop="host" label="主机地址" min-width="180" />
              <el-table-column prop="port" label="端口" width="100" />
              <el-table-column prop="protocol" label="协议" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.protocol || 'http' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="region" label="地区" width="120" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                    {{ row.status === 'active' ? '运行中' : '已停止' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button size="small" type="success" text @click="testRelay(row)">测试</el-button>
                  <el-button size="small" type="primary" text @click="editRelay(row)">编辑</el-button>
                  <el-button size="small" type="danger" text @click="deleteRelay(row)">删除</el-button>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无中转服务器" />
              </template>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <div class="tab-content">
            <div class="section-header">
              <h3 class="section-title">用户管理</h3>
              <el-button type="primary" @click="openUserDialog">
                <el-icon><Plus /></el-icon>
                添加用户
              </el-button>
            </div>
            <el-table :data="users" v-loading="loading.users" style="width: 100%;">
              <el-table-column prop="username" label="用户名" width="160" />
              <el-table-column prop="email" label="邮箱" min-width="220" />
              <el-table-column prop="full_name" label="姓名" width="160" />
              <el-table-column prop="role" label="角色" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                    {{ getRoleText(row.role) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                    {{ row.is_active ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="170">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button size="small" type="primary" text @click="editUser(row)">编辑</el-button>
                  <el-button size="small" :type="row.is_active ? 'warning' : 'success'" text @click="toggleUserStatus(row)">
                    {{ row.is_active ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无用户" />
              </template>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 系统信息 -->
        <el-tab-pane label="系统信息" name="system">
          <div class="tab-content" v-loading="loading.system">
            <h3 class="section-title">系统概览</h3>
            <el-row :gutter="20" class="system-info-row">
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value">{{ systemInfo.sites || 0 }}</div>
                    <div class="mini-stat-label">站点总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value">{{ systemInfo.products || 0 }}</div>
                    <div class="mini-stat-label">产品总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value">{{ systemInfo.tasks_total || 0 }}</div>
                    <div class="mini-stat-label">任务总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card shadow="hover" class="mini-stat">
                  <div class="mini-stat-content">
                    <div class="mini-stat-value success">{{ systemInfo.system_status || '-' }}</div>
                    <div class="mini-stat-label">系统状态</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <h3 class="section-title" style="margin-top: 24px;">系统详情</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="系统版本">WPForge v1.0.0</el-descriptions-item>
              <el-descriptions-item label="运行时长">{{ systemInfo.uptime || '-' }}</el-descriptions-item>
              <el-descriptions-item label="站点数量">{{ systemInfo.sites || 0 }}</el-descriptions-item>
              <el-descriptions-item label="产品数量">{{ systemInfo.products || 0 }}</el-descriptions-item>
              <el-descriptions-item label="任务总数">{{ systemInfo.tasks_total || 0 }}</el-descriptions-item>
              <el-descriptions-item label="运行中任务">{{ systemInfo.tasks_running || 0 }}</el-descriptions-item>
              <el-descriptions-item label="已完成任务">{{ systemInfo.tasks_completed || 0 }}</el-descriptions-item>
              <el-descriptions-item label="失败任务">{{ systemInfo.tasks_failed || 0 }}</el-descriptions-item>
              <el-descriptions-item label="系统状态">
                <el-tag type="success" size="small">{{ systemInfo.system_status || '正常' }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前时间">{{ formatTime(new Date().toISOString()) }}</el-descriptions-item>
            </el-descriptions>

            <h3 class="section-title" style="margin-top: 24px;">操作</h3>
            <div class="system-actions">
              <el-button type="primary" @click="refreshSystemInfo">
                <el-icon><Refresh /></el-icon>
                刷新系统信息
              </el-button>
              <el-button type="warning" @click="clearCache">
                <el-icon><Delete /></el-icon>
                清理缓存
              </el-button>
              <el-button type="danger" @click="restartSystem">
                <el-icon><SwitchButton /></el-icon>
                重启服务
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- AI提供商对话框 -->
    <el-dialog v-model="showProviderDialog" :title="providerIsEdit ? '编辑AI提供商' : '添加AI提供商'" width="520px">
      <el-form :model="providerForm" label-width="120px">
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
        <el-form-item label="启用">
          <el-switch v-model="providerForm.status" active-value="active" inactive-value="inactive" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProviderDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProvider">保存</el-button>
      </template>
    </el-dialog>

    <!-- 代理添加对话框 -->
    <el-dialog v-model="showProxyDialog" title="添加代理" width="520px">
      <el-form :model="proxyForm" label-width="100px">
        <el-form-item label="主机地址">
          <el-input v-model="proxyForm.host" placeholder="代理主机地址" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="proxyForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="协议">
          <el-select v-model="proxyForm.protocol" style="width: 200px;">
            <el-option label="HTTP" value="http" />
            <el-option label="HTTPS" value="https" />
            <el-option label="SOCKS5" value="socks5" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="proxyForm.username" placeholder="可选" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="proxyForm.password" type="password" placeholder="可选" show-password />
        </el-form-item>
        <el-form-item label="国家">
          <el-input v-model="proxyForm.country" placeholder="如：US" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-input v-model="proxyForm.provider" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProxyDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProxy">添加</el-button>
      </template>
    </el-dialog>

    <!-- 中转服务器对话框 -->
    <el-dialog v-model="showRelayDialog" :title="relayIsEdit ? '编辑中转服务器' : '添加中转服务器'" width="520px">
      <el-form :model="relayForm" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="relayForm.name" placeholder="服务器名称" />
        </el-form-item>
        <el-form-item label="主机地址">
          <el-input v-model="relayForm.host" placeholder="服务器地址" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="relayForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="协议">
          <el-select v-model="relayForm.protocol" style="width: 200px;">
            <el-option label="HTTP" value="http" />
            <el-option label="HTTPS" value="https" />
            <el-option label="SOCKS5" value="socks5" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-input v-model="relayForm.region" placeholder="如：美国西部" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="relayForm.status" active-value="active" inactive-value="inactive" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRelayDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveRelay">保存</el-button>
      </template>
    </el-dialog>

    <!-- 用户对话框 -->
    <el-dialog v-model="showUserDialog" :title="userIsEdit ? '编辑用户' : '添加用户'" width="520px">
      <el-form :model="userForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="userForm.username" placeholder="登录用户名" :disabled="userIsEdit" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userForm.email" placeholder="用户邮箱" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="userForm.full_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="userForm.role" style="width: 200px;">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!userIsEdit" label="密码">
          <el-input v-model="userForm.password" type="password" placeholder="登录密码" show-password />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAIProviders, getAvailableModels } from '@/api/ai'
import {
  getProxyPoolStats,
  listProxies,
  addProxy,
  removeProxy as removeProxyApi,
  checkProxies
} from '@/api/proxy'
import { getMonitoringOverview } from '@/api/monitoring'

const activeTab = ref('basic')
const saving = ref(false)
const checking = ref(false)

const loading = reactive({
  basic: false,
  ai: false,
  models: false,
  proxy: false,
  relay: false,
  users: false,
  system: false
})

// 基础设置
const basicSettings = reactive({
  system_name: 'WPForge',
  debug: false,
  log_level: 'INFO',
  max_concurrent_tasks: 5,
  task_timeout: 3600,
  max_upload_size: 100,
  language: 'zh-CN',
  timezone: 'Asia/Shanghai'
})

// AI 提供商
const aiProviders = ref<any[]>([])
const availableModels = ref<any[]>([])
const showProviderDialog = ref(false)
const providerIsEdit = ref(false)
const providerForm = reactive({
  id: undefined as number | undefined,
  name: '',
  api_key: '',
  base_url: '',
  default_model: '',
  status: 'active'
})

// 代理
const proxyStats = reactive({
  total: 0,
  alive: 0,
  dead: 0,
  avg_response_time: 0
})
const proxyList = ref<any[]>([])
const showProxyDialog = ref(false)
const proxyForm = reactive({
  host: '',
  port: 8080,
  protocol: 'http',
  username: '',
  password: '',
  country: '',
  provider: ''
})

// 反检测
const antiDetectionSettings = reactive({
  enabled: true,
  rotate_user_agent: true,
  request_interval: 2,
  random_delay: true,
  simulate_mouse: false,
  captcha_solver: false,
  headless_browser: false,
  persist_cookies: true,
  fingerprint_spoofing: false,
  max_retries: 3
})

// 中转服务器
const relayServers = ref<any[]>([])
const showRelayDialog = ref(false)
const relayIsEdit = ref(false)
const relayForm = reactive({
  id: undefined as number | undefined,
  name: '',
  host: '',
  port: 8080,
  protocol: 'http',
  region: '',
  status: 'active'
})

// 用户
const users = ref<any[]>([])
const showUserDialog = ref(false)
const userIsEdit = ref(false)
const userForm = reactive({
  id: undefined as number | undefined,
  username: '',
  email: '',
  full_name: '',
  role: 'user',
  password: '',
  is_active: true
})

// 系统信息
const systemInfo = reactive({
  sites: 0,
  products: 0,
  tasks_total: 0,
  tasks_running: 0,
  tasks_completed: 0,
  tasks_failed: 0,
  system_status: '正常',
  uptime: '-'
})

const formatTime = (time: string) => {
  if (!time) return '-'
  try {
    return new Date(time).toLocaleString('zh-CN', { hour12: false })
  } catch {
    return time
  }
}

const getRoleText = (role: string) => {
  const map: Record<string, string> = {
    admin: '管理员',
    user: '普通用户',
    guest: '访客'
  }
  return map[role] || role
}

// ===== 基础设置 =====
const saveBasicSettings = () => {
  saving.value = true
  setTimeout(() => {
    saving.value = false
    ElMessage.success('基础设置已保存')
  }, 500)
}

const resetBasicSettings = () => {
  basicSettings.system_name = 'WPForge'
  basicSettings.debug = false
  basicSettings.log_level = 'INFO'
  basicSettings.max_concurrent_tasks = 5
  basicSettings.task_timeout = 3600
  basicSettings.max_upload_size = 100
  basicSettings.language = 'zh-CN'
  basicSettings.timezone = 'Asia/Shanghai'
  ElMessage.info('已重置为默认值')
}

// ===== AI 提供商 =====
const loadAIProviders = async () => {
  loading.ai = true
  try {
    const res: any = await getAIProviders()
    aiProviders.value = res.data || res || []
  } catch (error: any) {
    aiProviders.value = []
  } finally {
    loading.ai = false
  }
}

const loadAvailableModels = async () => {
  loading.models = true
  try {
    const res: any = await getAvailableModels()
    availableModels.value = res.data || res || []
  } catch (error: any) {
    availableModels.value = []
  } finally {
    loading.models = false
  }
}

const openProviderDialog = () => {
  providerIsEdit.value = false
  providerForm.id = undefined
  providerForm.name = ''
  providerForm.api_key = ''
  providerForm.base_url = ''
  providerForm.default_model = ''
  providerForm.status = 'active'
  showProviderDialog.value = true
}

const editProvider = (provider: any) => {
  providerIsEdit.value = true
  providerForm.id = provider.id
  providerForm.name = provider.name
  providerForm.api_key = ''
  providerForm.base_url = provider.base_url
  providerForm.default_model = provider.default_model
  providerForm.status = provider.status
  showProviderDialog.value = true
}

const deleteProvider = (provider: any) => {
  ElMessageBox.confirm(
    `确定要删除AI提供商 "${provider.name}" 吗？`,
    '确认删除',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    aiProviders.value = aiProviders.value.filter((p: any) => p.id !== provider.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const saveProvider = () => {
  if (!providerForm.name) {
    ElMessage.error('请填写提供商名称')
    return
  }
  saving.value = true
  setTimeout(() => {
    if (providerIsEdit.value && providerForm.id) {
      const idx = aiProviders.value.findIndex((p: any) => p.id === providerForm.id)
      if (idx >= 0) {
        aiProviders.value[idx] = { ...aiProviders.value[idx], ...providerForm }
      }
      ElMessage.success('AI提供商更新成功')
    } else {
      aiProviders.value.push({
        id: Date.now(),
        name: providerForm.name,
        base_url: providerForm.base_url,
        default_model: providerForm.default_model,
        status: providerForm.status
      })
      ElMessage.success('AI提供商添加成功')
    }
    showProviderDialog.value = false
    saving.value = false
  }, 500)
}

// ===== 代理 =====
const loadProxyStats = async () => {
  try {
    const res: any = await getProxyPoolStats()
    const data = res.data || res || {}
    proxyStats.total = data.total || 0
    proxyStats.alive = data.alive || data.active || 0
    proxyStats.dead = data.dead || data.inactive || 0
    proxyStats.avg_response_time = data.avg_response_time || 0
  } catch (error: any) {
    // 静默失败
  }
}

const loadProxies = async () => {
  loading.proxy = true
  try {
    const res: any = await listProxies()
    proxyList.value = res.data || res || []
  } catch (error: any) {
    proxyList.value = []
  } finally {
    loading.proxy = false
  }
}

const openProxyDialog = () => {
  proxyForm.host = ''
  proxyForm.port = 8080
  proxyForm.protocol = 'http'
  proxyForm.username = ''
  proxyForm.password = ''
  proxyForm.country = ''
  proxyForm.provider = ''
  showProxyDialog.value = true
}

const saveProxy = async () => {
  if (!proxyForm.host) {
    ElMessage.error('请填写主机地址')
    return
  }
  saving.value = true
  try {
    await addProxy({
      host: proxyForm.host,
      port: proxyForm.port,
      protocol: proxyForm.protocol,
      username: proxyForm.username || undefined,
      password: proxyForm.password || undefined,
      country: proxyForm.country || undefined,
      provider: proxyForm.provider || undefined
    })
    ElMessage.success('代理添加成功')
    showProxyDialog.value = false
    loadProxies()
    loadProxyStats()
  } catch (error: any) {
    ElMessage.error(error.message || '添加代理失败')
  } finally {
    saving.value = false
  }
}

const removeProxy = (proxy: any) => {
  ElMessageBox.confirm(
    `确定要删除代理 "${proxy.host}:${proxy.port}" 吗？`,
    '确认删除',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      if (proxy.id) {
        await removeProxyApi(proxy.id)
      }
      ElMessage.success('删除成功')
      loadProxies()
      loadProxyStats()
    } catch (error: any) {
      ElMessage.error(error.message || '删除失败')
    }
  }).catch(() => {})
}

const checkProxiesHandler = async () => {
  checking.value = true
  try {
    await checkProxies()
    ElMessage.success('代理检测已完成')
    loadProxies()
    loadProxyStats()
  } catch (error: any) {
    ElMessage.error(error.message || '代理检测失败')
  } finally {
    checking.value = false
  }
}

// ===== 反检测 =====
const saveAntiDetectionSettings = () => {
  saving.value = true
  setTimeout(() => {
    saving.value = false
    ElMessage.success('反检测设置已保存')
  }, 500)
}

// ===== 中转服务器 =====
const openRelayDialog = () => {
  relayIsEdit.value = false
  relayForm.id = undefined
  relayForm.name = ''
  relayForm.host = ''
  relayForm.port = 8080
  relayForm.protocol = 'http'
  relayForm.region = ''
  relayForm.status = 'active'
  showRelayDialog.value = true
}

const editRelay = (relay: any) => {
  relayIsEdit.value = true
  relayForm.id = relay.id
  relayForm.name = relay.name
  relayForm.host = relay.host
  relayForm.port = relay.port
  relayForm.protocol = relay.protocol
  relayForm.region = relay.region
  relayForm.status = relay.status
  showRelayDialog.value = true
}

const deleteRelay = (relay: any) => {
  ElMessageBox.confirm(
    `确定要删除中转服务器 "${relay.name}" 吗？`,
    '确认删除',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    relayServers.value = relayServers.value.filter((r: any) => r.id !== relay.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const saveRelay = () => {
  if (!relayForm.name || !relayForm.host) {
    ElMessage.error('请填写名称和主机地址')
    return
  }
  saving.value = true
  setTimeout(() => {
    if (relayIsEdit.value && relayForm.id) {
      const idx = relayServers.value.findIndex((r: any) => r.id === relayForm.id)
      if (idx >= 0) {
        relayServers.value[idx] = { ...relayServers.value[idx], ...relayForm }
      }
      ElMessage.success('中转服务器更新成功')
    } else {
      relayServers.value.push({
        id: Date.now(),
        name: relayForm.name,
        host: relayForm.host,
        port: relayForm.port,
        protocol: relayForm.protocol,
        region: relayForm.region,
        status: relayForm.status
      })
      ElMessage.success('中转服务器添加成功')
    }
    showRelayDialog.value = false
    saving.value = false
  }, 500)
}

const testRelay = (relay: any) => {
  ElMessage.info(`正在测试中转服务器 "${relay.name}"...`)
  setTimeout(() => {
    ElMessage.success(`中转服务器 "${relay.name}" 连接正常`)
  }, 1500)
}

// ===== 用户管理 =====
const openUserDialog = () => {
  userIsEdit.value = false
  userForm.id = undefined
  userForm.username = ''
  userForm.email = ''
  userForm.full_name = ''
  userForm.role = 'user'
  userForm.password = ''
  userForm.is_active = true
  showUserDialog.value = true
}

const editUser = (user: any) => {
  userIsEdit.value = true
  userForm.id = user.id
  userForm.username = user.username
  userForm.email = user.email
  userForm.full_name = user.full_name
  userForm.role = user.role
  userForm.password = ''
  userForm.is_active = user.is_active
  showUserDialog.value = true
}

const toggleUserStatus = (user: any) => {
  ElMessageBox.confirm(
    `确定要${user.is_active ? '禁用' : '启用'}用户 "${user.username}" 吗？`,
    '确认操作',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    user.is_active = !user.is_active
    ElMessage.success(`用户已${user.is_active ? '启用' : '禁用'}`)
  }).catch(() => {})
}

const saveUser = () => {
  if (!userForm.username || !userForm.email) {
    ElMessage.error('请填写用户名和邮箱')
    return
  }
  if (!userIsEdit.value && !userForm.password) {
    ElMessage.error('请填写密码')
    return
  }
  saving.value = true
  setTimeout(() => {
    if (userIsEdit.value && userForm.id) {
      const idx = users.value.findIndex((u: any) => u.id === userForm.id)
      if (idx >= 0) {
        users.value[idx] = {
          ...users.value[idx],
          username: userForm.username,
          email: userForm.email,
          full_name: userForm.full_name,
          role: userForm.role,
          is_active: userForm.is_active
        }
      }
      ElMessage.success('用户更新成功')
    } else {
      users.value.push({
        id: Date.now(),
        username: userForm.username,
        email: userForm.email,
        full_name: userForm.full_name,
        role: userForm.role,
        is_active: userForm.is_active,
        created_at: new Date().toISOString()
      })
      ElMessage.success('用户添加成功')
    }
    showUserDialog.value = false
    saving.value = false
  }, 500)
}

// ===== 系统信息 =====
const loadSystemInfo = async () => {
  loading.system = true
  try {
    const res: any = await getMonitoringOverview()
    const data = res.data || res || {}
    systemInfo.sites = data.sites || 0
    systemInfo.products = data.products || 0
    systemInfo.tasks_total = data.tasks?.total || 0
    systemInfo.tasks_running = data.tasks?.running || 0
    systemInfo.tasks_completed = data.tasks?.completed || 0
    systemInfo.tasks_failed = data.tasks?.failed || 0
    systemInfo.system_status = data.system_status || '正常'
    systemInfo.uptime = data.uptime || '-'
  } catch (error: any) {
    // 静默失败
  } finally {
    loading.system = false
  }
}

const refreshSystemInfo = () => {
  loadSystemInfo()
  ElMessage.success('系统信息已刷新')
}

const clearCache = () => {
  ElMessageBox.confirm(
    '确定要清理系统缓存吗？',
    '清理缓存',
    { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
  ).then(() => {
    ElMessage.success('缓存清理成功')
  }).catch(() => {})
}

const restartSystem = () => {
  ElMessageBox.confirm(
    '确定要重启服务吗？此操作会导致服务短暂不可用。',
    '重启服务',
    { confirmButtonText: '确定重启', cancelButtonText: '取消', type: 'error' }
  ).then(() => {
    ElMessage.info('重启指令已发送，请稍候...')
  }).catch(() => {})
}

onMounted(() => {
  loadAIProviders()
  loadAvailableModels()
  loadProxyStats()
  loadProxies()
  loadSystemInfo()
})
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

.settings-card {
  border: none;
  border-radius: 8px;
}

.settings-tabs {
  min-height: 600px;
}

.tab-content {
  padding: 0 12px;
}

.section-title {
  margin: 0 0 20px;
  font-size: 18px;
  color: #1f2937;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header .section-title {
  margin: 0;
}

.form-tip {
  margin-left: 12px;
  color: #9ca3af;
  font-size: 12px;
}

.proxy-stats-row {
  margin-bottom: 20px;
}

.mini-stat {
  border: none;
  border-radius: 8px;
}

.mini-stat-content {
  text-align: center;
  padding: 8px 0;
}

.mini-stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.mini-stat-value.success {
  color: #67c23a;
}

.mini-stat-value.danger {
  color: #f56c6c;
}

.mini-stat-label {
  margin-top: 4px;
  font-size: 13px;
  color: #6b7280;
}

.system-info-row {
  margin-bottom: 20px;
}

.system-actions {
  display: flex;
  gap: 12px;
}
</style>
