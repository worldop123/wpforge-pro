<template>
  <div class="plugin-market">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>插件市场</h2>
      <p>扩展WPForge功能，发现更多强大插件</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="toolbar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索插件..."
        style="width: 300px"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-radio-group v-model="activeTab" size="default">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="installed">已安装</el-radio-button>
        <el-radio-button label="available">可用</el-radio-button>
      </el-radio-group>

      <el-select v-model="categoryFilter" placeholder="分类" style="width: 150px" clearable>
        <el-option label="SEO优化" value="seo" />
        <el-option label="营销工具" value="marketing" />
        <el-option label="数据分析" value="analytics" />
        <el-option label="支付网关" value="payment" />
        <el-option label="物流配送" value="shipping" />
        <el-option label="安全防护" value="security" />
        <el-option label="性能优化" value="performance" />
      </el-select>
    </div>

    <!-- 已安装插件 -->
    <div v-if="activeTab === 'all' || activeTab === 'installed'" class="plugin-section">
      <h3 class="section-title">
        <el-icon><SuccessFilled /></el-icon>
        已安装插件
        <span class="badge">{{ installedPlugins.length }}</span>
      </h3>

      <div class="plugin-grid">
        <div
          v-for="plugin in filteredInstalledPlugins"
          :key="plugin.id"
          class="plugin-card installed"
        >
          <div class="plugin-header">
            <div class="plugin-icon" :style="{ backgroundColor: plugin.color }">
              <el-icon :size="28"><component :is="plugin.icon" /></el-icon>
            </div>
            <div class="plugin-status">
              <el-switch
                v-model="plugin.enabled"
                size="small"
                @change="togglePlugin(plugin)"
              />
            </div>
          </div>

          <div class="plugin-body">
            <h4 class="plugin-name">{{ plugin.name }}</h4>
            <p class="plugin-desc">{{ plugin.description }}</p>
            <div class="plugin-meta">
              <span class="version">v{{ plugin.version }}</span>
              <span class="author">{{ plugin.author }}</span>
            </div>
          </div>

          <div class="plugin-footer">
            <el-button size="small" @click="viewPlugin(plugin)">详情</el-button>
            <el-button size="small" type="primary" @click="configurePlugin(plugin)">
              配置
            </el-button>
            <el-dropdown @command="(cmd) => handlePluginAction(cmd, plugin)">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="update" v-if="plugin.hasUpdate">
                    <el-icon><Top /></el-icon>
                    更新到 v{{ plugin.latestVersion }}
                  </el-dropdown-item>
                  <el-dropdown-item command="settings">
                    <el-icon><Setting /></el-icon>
                    设置
                  </el-dropdown-item>
                  <el-dropdown-item command="uninstall" divided>
                    <el-icon><Delete /></el-icon>
                    卸载
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <div v-if="plugin.hasUpdate" class="update-badge">
            有更新
          </div>
        </div>
      </div>
    </div>

    <!-- 可用插件 -->
    <div v-if="activeTab === 'all' || activeTab === 'available'" class="plugin-section">
      <h3 class="section-title">
        <el-icon><Shop /></el-icon>
        发现更多
        <span class="badge">{{ availablePlugins.length }}</span>
      </h3>

      <div class="plugin-grid">
        <div
          v-for="plugin in filteredAvailablePlugins"
          :key="plugin.id"
          class="plugin-card"
        >
          <div class="plugin-header">
            <div class="plugin-icon" :style="{ backgroundColor: plugin.color }">
              <el-icon :size="28"><component :is="plugin.icon" /></el-icon>
            </div>
            <div class="plugin-rating">
              <el-rate v-model="plugin.rating" disabled size="small" />
              <span class="rating-count">({{ plugin.reviews }})</span>
            </div>
          </div>

          <div class="plugin-body">
            <h4 class="plugin-name">{{ plugin.name }}</h4>
            <p class="plugin-desc">{{ plugin.description }}</p>
            <div class="plugin-meta">
              <span class="version">v{{ plugin.version }}</span>
              <span class="author">{{ plugin.author }}</span>
              <span class="downloads">{{ plugin.downloads }} 下载</span>
            </div>
          </div>

          <div class="plugin-footer">
            <el-button size="small" @click="viewPlugin(plugin)">详情</el-button>
            <el-button size="small" type="primary" @click="installPlugin(plugin)" :loading="plugin.installing">
              安装
            </el-button>
            <div class="plugin-price" v-if="plugin.price > 0">
              ¥{{ plugin.price }}
            </div>
            <div class="plugin-price free" v-else>
              免费
            </div>
          </div>

          <div v-if="plugin.featured" class="featured-badge">
            推荐
          </div>
        </div>
      </div>
    </div>

    <!-- 插件详情弹窗 -->
    <el-dialog v-model="detailVisible" title="插件详情" width="600px">
      <div v-if="selectedPlugin" class="plugin-detail">
        <div class="detail-header">
          <div class="detail-icon" :style="{ backgroundColor: selectedPlugin.color }">
            <el-icon :size="40"><component :is="selectedPlugin.icon" /></el-icon>
          </div>
          <div class="detail-info">
            <h3>{{ selectedPlugin.name }}</h3>
            <p>{{ selectedPlugin.author }} · v{{ selectedPlugin.version }}</p>
            <div class="detail-rating">
              <el-rate v-model="selectedPlugin.rating" disabled size="small" />
              <span>{{ selectedPlugin.reviews }} 评价</span>
              <span class="downloads">{{ selectedPlugin.downloads }} 下载</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>插件介绍</h4>
          <p>{{ selectedPlugin.fullDescription }}</p>
        </div>

        <div class="detail-section">
          <h4>主要功能</h4>
          <ul>
            <li v-for="(feature, index) in selectedPlugin.features" :key="index">
              <el-icon><Check /></el-icon>
              {{ feature }}
            </li>
          </ul>
        </div>

        <div class="detail-section">
          <h4>截图</h4>
          <div class="screenshots">
            <div v-for="i in 3" :key="i" class="screenshot-placeholder">
              <el-icon :size="48"><Picture /></el-icon>
              <span>截图 {{ i }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="installFromDetail">
          {{ selectedPlugin?.price > 0 ? '购买' : '安装' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  SuccessFilled,
  Shop,
  ArrowDown,
  Top,
  Setting,
  Delete,
  Check,
  Picture,
  DataAnalysis,
  MagicStick,
  Lock,
  TrendCharts,
  Coin,
  Van,
  Shield,
  Lightning,
  Bell,
  ChatDotRound,
  User,
  Goods
} from '@element-plus/icons-vue'

const searchQuery = ref('')
const activeTab = ref('all')
const categoryFilter = ref('')
const detailVisible = ref(false)
const selectedPlugin = ref(null)

const installedPlugins = ref([
  {
    id: 'seo-pro',
    name: 'SEO Pro',
    description: '高级SEO优化工具，自动生成Schema、优化关键词',
    version: '1.2.0',
    latestVersion: '1.3.0',
    author: 'WPForge',
    icon: 'TrendCharts',
    color: '#10b981',
    enabled: true,
    hasUpdate: true,
    category: 'seo'
  },
  {
    id: 'analytics',
    name: 'Analytics Pro',
    description: '网站数据分析与统计，漏斗分析、用户行为追踪',
    version: '2.0.1',
    author: 'WPForge',
    icon: 'DataAnalysis',
    color: '#6366f1',
    enabled: true,
    hasUpdate: false,
    category: 'analytics'
  },
  {
    id: 'cache-booster',
    name: 'Cache Booster',
    description: '高性能缓存插件，大幅提升网站速度',
    version: '1.5.0',
    author: 'WPForge',
    icon: 'Lightning',
    color: '#f59e0b',
    enabled: false,
    hasUpdate: false,
    category: 'performance'
  },
  {
    id: 'security-guard',
    name: 'Security Guard',
    description: '网站安全防护，防火墙、恶意扫描、登录保护',
    version: '2.1.0',
    author: 'WPForge',
    icon: 'Shield',
    color: '#ef4444',
    enabled: true,
    hasUpdate: true,
    latestVersion: '2.2.0',
    category: 'security'
  }
])

const availablePlugins = ref([
  {
    id: 'email-marketing',
    name: 'Email Marketing',
    description: '邮件营销自动化，弃购挽回、欢迎邮件、促销推送',
    fullDescription: '强大的邮件营销自动化插件，帮助您提升转化率和客户留存率。支持自动化邮件序列、细分用户群体、A/B测试等高级功能。',
    version: '1.0.0',
    author: 'WPForge',
    icon: 'Bell',
    color: '#ec4899',
    rating: 4.8,
    reviews: 1256,
    downloads: '12.5K',
    price: 0,
    featured: true,
    category: 'marketing',
    installing: false,
    features: [
      '自动化邮件序列',
      '弃购挽回邮件',
      '用户细分与标签',
      '邮件模板编辑器',
      'A/B测试功能',
      '详细统计报表'
    ]
  },
  {
    id: 'live-chat',
    name: 'Live Chat',
    description: '在线客服系统，实时聊天、智能客服机器人',
    fullDescription: '专业的在线客服解决方案，支持多渠道接入、智能客服机器人、客服工单系统，提升客户满意度。',
    version: '1.2.0',
    author: 'WPForge',
    icon: 'ChatDotRound',
    color: '#06b6d4',
    rating: 4.6,
    reviews: 892,
    downloads: '8.3K',
    price: 99,
    featured: true,
    category: 'marketing',
    installing: false,
    features: [
      '实时在线聊天',
      '智能客服机器人',
      '多渠道接入',
      '客服工单系统',
      '聊天记录存档',
      '满意度评价'
    ]
  },
  {
    id: 'membership',
    name: 'Membership Pro',
    description: '会员系统，付费内容、会员等级、权限控制',
    fullDescription: '完整的会员管理系统，支持多种会员等级、付费内容访问控制、会员订阅、 drip content 等功能。',
    version: '2.0.0',
    author: 'WPForge',
    icon: 'User',
    color: '#8b5cf6',
    rating: 4.9,
    reviews: 2341,
    downloads: '18.7K',
    price: 199,
    featured: false,
    category: 'marketing',
    installing: false,
    features: [
      '无限会员等级',
      '内容访问控制',
      '订阅付款系统',
      ' drip content',
      '会员报表',
      '集成支付网关'
    ]
  },
  {
    id: 'stripe-gateway',
    name: 'Stripe Gateway',
    description: 'Stripe支付网关集成，支持信用卡、Apple Pay',
    fullDescription: '完整的Stripe支付集成，支持多种支付方式，订阅付款，保存支付方式，强大的安全保护。',
    version: '1.3.0',
    author: 'WPForge',
    icon: 'Coin',
    color: '#635bff',
    rating: 4.7,
    reviews: 1567,
    downloads: '25.3K',
    price: 0,
    featured: false,
    category: 'payment',
    installing: false,
    features: [
      '信用卡支付',
      'Apple Pay / Google Pay',
      '订阅付款',
      '保存支付方式',
      '3D Secure验证',
      '详细交易记录'
    ]
  },
  {
    id: 'shipping-pro',
    name: 'Shipping Pro',
    description: '高级物流配送，实时运费计算、多物流商集成',
    fullDescription: '专业的物流配送解决方案，集成多家物流商，实时运费计算，物流追踪，面单打印等功能。',
    version: '1.1.0',
    author: 'WPForge',
    icon: 'Van',
    color: '#f97316',
    rating: 4.5,
    reviews: 623,
    downloads: '5.8K',
    price: 149,
    featured: false,
    category: 'shipping',
    installing: false,
    features: [
      '实时运费计算',
      '多物流商集成',
      '物流追踪',
      '面单打印',
      '运费规则',
      '配送区域管理'
    ]
  },
  {
    id: 'product-badges',
    name: 'Product Badges',
    description: '产品徽章系统，新品、热销、特价等营销标签',
    fullDescription: '灵活的产品徽章系统，支持多种徽章类型，自定义样式，智能显示规则，提升产品吸引力。',
    version: '1.0.0',
    author: 'WPForge',
    icon: 'Goods',
    color: '#14b8a6',
    rating: 4.4,
    reviews: 345,
    downloads: '3.2K',
    price: 0,
    featured: false,
    category: 'marketing',
    installing: false,
    features: [
      '多种徽章类型',
      '自定义样式',
      '智能显示规则',
      '批量设置',
      '动画效果',
      '移动端适配'
    ]
  }
])

const filteredInstalledPlugins = computed(() => {
  let result = installedPlugins.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    )
  }

  if (categoryFilter.value) {
    result = result.filter(p => p.category === categoryFilter.value)
  }

  return result
})

const filteredAvailablePlugins = computed(() => {
  let result = availablePlugins.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    )
  }

  if (categoryFilter.value) {
    result = result.filter(p => p.category === categoryFilter.value)
  }

  return result
})

const togglePlugin = (plugin) => {
  ElMessage.success(`${plugin.name} 已${plugin.enabled ? '启用' : '禁用'}`)
}

const viewPlugin = (plugin) => {
  selectedPlugin.value = plugin
  detailVisible.value = true
}

const configurePlugin = (plugin) => {
  ElMessage.info(`正在打开 ${plugin.name} 配置页面...`)
}

const handlePluginAction = (command, plugin) => {
  switch (command) {
    case 'update':
      ElMessage.success(`${plugin.name} 更新成功！`)
      plugin.hasUpdate = false
      plugin.version = plugin.latestVersion
      break
    case 'settings':
      configurePlugin(plugin)
      break
    case 'uninstall':
      ElMessageBox.confirm(
        `确定要卸载 ${plugin.name} 吗？此操作不可恢复。`,
        '卸载插件',
        {
          confirmButtonText: '确定卸载',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        const index = installedPlugins.value.findIndex(p => p.id === plugin.id)
        if (index > -1) {
          installedPlugins.value.splice(index, 1)
        }
        ElMessage.success('插件已卸载')
      }).catch(() => {})
      break
  }
}

const installPlugin = (plugin) => {
  plugin.installing = true
  setTimeout(() => {
    plugin.installing = false
    installedPlugins.value.push({
      ...plugin,
      enabled: true,
      hasUpdate: false
    })
    ElMessage.success(`${plugin.name} 安装成功！`)
  }, 1500)
}

const installFromDetail = () => {
  if (selectedPlugin.value) {
    installPlugin(selectedPlugin.value)
    detailVisible.value = false
  }
}
</script>

<style scoped>
.plugin-market {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.plugin-section {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 16px 0;
}

.section-title .badge {
  background: #e5e7eb;
  color: #6b7280;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.plugin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.plugin-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.plugin-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.plugin-card.installed {
  border-color: #10b98120;
}

.plugin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.plugin-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.plugin-rating {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-count {
  font-size: 12px;
  color: #6b7280;
}

.plugin-body {
  margin-bottom: 16px;
}

.plugin-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.plugin-desc {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.plugin-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #9ca3af;
}

.plugin-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.plugin-price {
  margin-left: auto;
  font-weight: 600;
  color: #10b981;
}

.plugin-price.free {
  color: #10b981;
}

.update-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #f59e0b;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.featured-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.plugin-detail {
  padding: 10px 0;
}

.detail-header {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.detail-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.detail-info h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
}

.detail-info p {
  margin: 0 0 8px 0;
  color: #6b7280;
  font-size: 14px;
}

.detail-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #6b7280;
}

.detail-rating .downloads {
  margin-left: 8px;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
}

.detail-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.detail-section li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  color: #374151;
}

.detail-section li .el-icon {
  color: #10b981;
}

.screenshots {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.screenshot-placeholder {
  aspect-ratio: 16/10;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  gap: 8px;
}
</style>
