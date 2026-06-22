<template>
  <div class="funnel-dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2>电商漏斗数据</h2>
        <p>多站点电商转化数据集中管理与分析</p>
      </div>
      <div class="header-actions">
        <el-select v-model="timeRange" style="width: 150px">
          <el-option label="今天" value="today" />
          <el-option label="昨天" value="yesterday" />
          <el-option label="近7天" value="7days" />
          <el-option label="近30天" value="30days" />
          <el-option label="本月" value="thisMonth" />
          <el-option label="上月" value="lastMonth" />
        </el-select>
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 站点选择器 -->
    <div class="site-selector">
      <el-radio-group v-model="viewMode">
        <el-radio-button label="overview">总览</el-radio-button>
        <el-radio-button label="compare">对比分析</el-radio-button>
        <el-radio-button label="ranking">站点排名</el-radio-button>
      </el-radio-group>

      <el-select v-model="selectedSites" multiple placeholder="选择站点" style="width: 400px">
        <el-option
          v-for="site in sites"
          :key="site.id"
          :label="site.name"
          :value="site.id"
        />
      </el-select>
    </div>

    <!-- 总览模式 -->
    <div v-if="viewMode === 'overview'">
      <!-- KPI卡片 -->
      <el-row :gutter="20" class="kpi-row">
        <el-col :span="4" v-for="kpi in kpiData" :key="kpi.key">
          <el-card class="kpi-card" :class="kpi.color">
            <div class="kpi-icon">
              <el-icon :size="24"><component :is="kpi.icon" /></el-icon>
            </div>
            <div class="kpi-value">{{ kpi.value }}</div>
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-change" :class="kpi.trend">
              <el-icon><component :is="kpi.trend === 'up' ? 'Top' : 'Bottom'" /></el-icon>
              {{ kpi.change }}
              <span class="vs">环比</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 漏斗图 + 趋势图 -->
      <el-row :gutter="20" class="chart-row">
        <el-col :span="10">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>转化漏斗</span>
                <el-radio-group v-model="funnelView" size="small">
                  <el-radio-button label="absolute">绝对值</el-radio-button>
                  <el-radio-button label="percent">转化率</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div class="funnel-chart">
              <div
                v-for="(stage, index) in funnelData"
                :key="index"
                class="funnel-stage"
              >
                <div
                  class="funnel-bar"
                  :style="{ width: stage.percent + '%' }"
                  :class="'stage-' + index"
                >
                  <span class="stage-value">{{ stage.value }}</span>
                </div>
                <div class="stage-info">
                  <span class="stage-name">{{ stage.name }}</span>
                  <span class="stage-rate">转化率: {{ stage.conversionRate }}%</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="14">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>销售趋势</span>
                <el-radio-group v-model="trendView" size="small">
                  <el-radio-button label="sales">销售额</el-radio-button>
                  <el-radio-button label="orders">订单数</el-radio-button>
                  <el-radio-button label="conversion">转化率</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div class="trend-chart-placeholder">
              <el-icon :size="64" color="#d1d5db"><DataLine /></el-icon>
              <p>销售趋势图表</p>
              <p class="hint">集成Chart.js后显示完整图表</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 热销产品 + 弃购产品 -->
      <el-row :gutter="20" class="chart-row">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>热销产品 TOP10</span>
                <el-select v-model="hotProductsSort" size="small" style="width: 120px">
                  <el-option label="按销量" value="sales" />
                  <el-option label="按销售额" value="revenue" />
                  <el-option label="按加购数" value="cart" />
                </el-select>
              </div>
            </template>
            <div class="product-list">
              <div
                v-for="(product, index) in hotProducts"
                :key="product.id"
                class="product-item"
              >
                <div class="product-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="product-image">
                  <el-icon><Goods /></el-icon>
                </div>
                <div class="product-info">
                  <div class="product-name">{{ product.name }}</div>
                  <div class="product-meta">
                    销量: {{ product.sales }} · 销售额: ¥{{ product.revenue }}
                  </div>
                </div>
                <div class="product-bar">
                  <div
                    class="bar-fill"
                    :style="{ width: (product.sales / hotProducts[0].sales * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>弃购产品 TOP10</span>
                <el-select v-model="abandonedSort" size="small" style="width: 120px">
                  <el-option label="按弃购率" value="rate" />
                  <el-option label="按弃购数" value="count" />
                  <el-option label="按金额" value="amount" />
                </el-select>
              </div>
            </template>
            <div class="product-list">
              <div
                v-for="(product, index) in abandonedProducts"
                :key="product.id"
                class="product-item"
              >
                <div class="product-rank abandon">{{ index + 1 }}</div>
                <div class="product-image abandon">
                  <el-icon><Goods /></el-icon>
                </div>
                <div class="product-info">
                  <div class="product-name">{{ product.name }}</div>
                  <div class="product-meta">
                    弃购率: {{ product.abandonRate }}% · 弃购金额: ¥{{ product.amount }}
                  </div>
                </div>
                <div class="product-bar abandon">
                  <div
                    class="bar-fill"
                    :style="{ width: (product.abandonRate / 100 * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 智能洞察 -->
      <el-card class="insights-card">
        <template #header>
          <div class="card-header">
            <span><el-icon><MagicStick /></el-icon> 智能洞察与优化建议</span>
            <el-tag size="small">AI 生成</el-tag>
          </div>
        </template>
        <div class="insights-list">
          <div
            v-for="(insight, index) in insights"
            :key="index"
            class="insight-item"
            :class="insight.type"
          >
            <div class="insight-icon">
              <el-icon><component :is="insight.icon" /></el-icon>
            </div>
            <div class="insight-content">
              <div class="insight-title">{{ insight.title }}</div>
              <div class="insight-desc">{{ insight.description }}</div>
              <div class="insight-data">
                <span>数据依据: {{ insight.data }}</span>
                <span class="priority">优先级: {{ insight.priority }}</span>
              </div>
            </div>
            <el-button size="small" type="primary">立即优化</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 对比分析模式 -->
    <div v-if="viewMode === 'compare'">
      <el-card class="compare-card">
        <template #header>
          <span>站点对比分析</span>
        </template>
        <div class="compare-table-wrapper">
          <el-table :data="compareData" style="width: 100%">
            <el-table-column prop="siteName" label="站点" width="200" fixed />
            <el-table-column prop="visitors" label="访客数" sortable />
            <el-table-column prop="productViews" label="浏览产品" sortable />
            <el-table-column prop="cartAdds" label="加购数" sortable />
            <el-table-column prop="checkouts" label="结账数" sortable />
            <el-table-column prop="orders" label="订单数" sortable />
            <el-table-column prop="revenue" label="销售额" sortable />
            <el-table-column prop="conversionRate" label="转化率" sortable>
              <template #default="{ row }">
                <span :class="row.conversionRate > 3 ? 'high-rate' : 'low-rate'">
                  {{ row.conversionRate }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="avgOrderValue" label="客单价" sortable />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewSiteDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 站点排名模式 -->
    <div v-if="viewMode === 'ranking'">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="ranking-card">
            <template #header>
              <span>销售额排名</span>
            </template>
            <div class="ranking-list">
              <div
                v-for="(site, index) in revenueRanking"
                :key="site.id"
                class="ranking-item"
              >
                <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ site.name }}</div>
                  <div class="rank-value">¥{{ site.revenue }}</div>
                </div>
                <div class="rank-trend" :class="site.trend">
                  <el-icon><component :is="site.trend === 'up' ? 'Top' : 'Bottom'" /></el-icon>
                  {{ site.change }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="ranking-card">
            <template #header>
              <span>转化率排名</span>
            </template>
            <div class="ranking-list">
              <div
                v-for="(site, index) in conversionRanking"
                :key="site.id"
                class="ranking-item"
              >
                <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ site.name }}</div>
                  <div class="rank-value">{{ site.conversionRate }}%</div>
                </div>
                <div class="rank-trend" :class="site.trend">
                  <el-icon><component :is="site.trend === 'up' ? 'Top' : 'Bottom'" /></el-icon>
                  {{ site.change }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="ranking-card">
            <template #header>
              <span>访客数排名</span>
            </template>
            <div class="ranking-list">
              <div
                v-for="(site, index) in visitorRanking"
                :key="site.id"
                class="ranking-item"
              >
                <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ site.name }}</div>
                  <div class="rank-value">{{ site.visitors }}</div>
                </div>
                <div class="rank-trend" :class="site.trend">
                  <el-icon><component :is="site.trend === 'up' ? 'Top' : 'Bottom'" /></el-icon>
                  {{ site.change }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download,
  DataLine,
  Goods,
  MagicStick,
  Warning,
  Opportunity,
  Top,
  Bottom,
  User,
  ShoppingCart,
  Money,
  TrendCharts,
  Check
} from '@element-plus/icons-vue'

const timeRange = ref('30days')
const viewMode = ref('overview')
const selectedSites = ref([])
const funnelView = ref('percent')
const trendView = ref('sales')
const hotProductsSort = ref('sales')
const abandonedSort = ref('rate')

const sites = ref([
  { id: 1, name: 'BangVape HU' },
  { id: 2, name: 'BangVape RO' },
  { id: 3, name: 'BangVape AT' },
  { id: 4, name: 'US Vape Shop' },
  { id: 5, name: 'Vape Pro DE' }
])

const kpiData = ref([
  { key: 'visitors', label: '总访客数', value: '128,456', change: '12.5%', trend: 'up', icon: 'User', color: 'blue' },
  { key: 'orders', label: '总订单数', value: '3,248', change: '8.3%', trend: 'up', icon: 'ShoppingCart', color: 'green' },
  { key: 'revenue', label: '总销售额', value: '¥289,560', change: '15.2%', trend: 'up', icon: 'Money', color: 'purple' },
  { key: 'conversion', label: '整体转化率', value: '2.53%', change: '0.3%', trend: 'up', icon: 'TrendCharts', color: 'orange' },
  { key: 'aov', label: '客单价', value: '¥89.2', change: '6.8%', trend: 'up', icon: 'Goods', color: 'cyan' }
])

const funnelData = ref([
  { name: '访客数', value: '128,456', percent: 100, conversionRate: '100' },
  { name: '浏览产品', value: '89,234', percent: 69.5, conversionRate: '69.5' },
  { name: '加入购物车', value: '28,456', percent: 22.2, conversionRate: '31.9' },
  { name: '开始结账', value: '15,678', percent: 12.2, conversionRate: '55.1' },
  { name: '完成购买', value: '3,248', percent: 2.5, conversionRate: '20.7' }
])

const hotProducts = ref([
  { id: 1, name: 'Bang XXL 2000 Puffs', sales: 1256, revenue: '28,960' },
  { id: 2, name: 'Bang Pro 3000 Puffs', sales: 987, revenue: '24,675' },
  { id: 3, name: 'Bang Max 5000 Puffs', sales: 845, revenue: '29,575' },
  { id: 4, name: 'Bang Mini 800 Puffs', sales: 723, revenue: '10,845' },
  { id: 5, name: 'Bang Ultra 7000 Puffs', sales: 612, revenue: '27,540' },
  { id: 6, name: 'Bang Nano 600 Puffs', sales: 534, revenue: '6,942' },
  { id: 7, name: 'Bang Plus 1500 Puffs', sales: 478, revenue: '11,950' },
  { id: 8, name: 'Bang King 10000 Puffs', sales: 412, revenue: '28,840' }
])

const abandonedProducts = ref([
  { id: 1, name: 'Bang King 10000 Puffs', abandonRate: 68.5, amount: '15,680' },
  { id: 2, name: 'Bang Ultra 7000 Puffs', abandonRate: 62.3, amount: '12,450' },
  { id: 3, name: 'Bang Max 5000 Puffs', abandonRate: 58.7, amount: '10,230' },
  { id: 4, name: 'Bang Pro 3000 Puffs', abandonRate: 54.2, amount: '8,960' },
  { id: 5, name: 'Bang XXL 2000 Puffs', abandonRate: 49.8, amount: '7,840' },
  { id: 6, name: 'Bang Plus 1500 Puffs', abandonRate: 45.6, amount: '5,670' },
  { id: 7, name: 'Bang Mini 800 Puffs', abandonRate: 41.3, amount: '3,450' },
  { id: 8, name: 'Bang Nano 600 Puffs', abandonRate: 38.9, amount: '2,180' }
])

const insights = ref([
  {
    type: 'warning',
    icon: 'Warning',
    title: '结账页面弃购率偏高',
    description: '结账页面的弃购率达到 79.3%，高于行业平均水平。建议优化结账流程，减少填写字段，添加信任徽章。',
    data: '结账弃购率 79.3%，行业平均 65%',
    priority: '高'
  },
  {
    type: 'opportunity',
    icon: 'Opportunity',
    title: '移动端转化率有提升空间',
    description: '移动端访客占比 65%，但转化率仅为 1.8%，低于桌面端的 3.2%。建议优化移动端购物体验。',
    data: '移动端转化率 1.8%，桌面端 3.2%',
    priority: '中'
  },
  {
    type: 'success',
    icon: 'Check',
    title: '本周销售额增长显著',
    description: '本周销售额环比增长 15.2%，主要得益于新品上市和促销活动。建议保持当前营销策略。',
    data: '销售额增长 15.2%，订单增长 8.3%',
    priority: '低'
  },
  {
    type: 'optimization',
    icon: 'TrendCharts',
    title: '高客单价产品加购率低',
    description: 'Bang King 10000 Puffs 虽然单价高，但加购率偏低。建议添加产品对比、增加用户评价、提供分期付款选项。',
    data: '加购率 12.5%，平均 22.2%',
    priority: '中'
  }
])

const compareData = ref([
  { siteName: 'BangVape HU', visitors: 45678, productViews: 32456, cartAdds: 12345, checkouts: 5678, orders: 1234, revenue: '¥98,760', conversionRate: 2.7, avgOrderValue: '¥80.0' },
  { siteName: 'BangVape RO', visitors: 34567, productViews: 23456, cartAdds: 8765, checkouts: 4321, orders: 876, revenue: '¥65,430', conversionRate: 2.53, avgOrderValue: '¥74.7' },
  { siteName: 'BangVape AT', visitors: 23456, productViews: 18765, cartAdds: 6543, checkouts: 3210, orders: 654, revenue: '¥54,320', conversionRate: 2.79, avgOrderValue: '¥83.1' },
  { siteName: 'US Vape Shop', visitors: 18765, productViews: 12345, cartAdds: 4567, checkouts: 2345, orders: 345, revenue: '¥45,670', conversionRate: 1.84, avgOrderValue: '¥132.4' },
  { siteName: 'Vape Pro DE', visitors: 5990, productViews: 2212, cartAdds: 1236, checkouts: 524, orders: 139, revenue: '¥25,380', conversionRate: 2.32, avgOrderValue: '¥182.6' }
])

const revenueRanking = ref([
  { id: 1, name: 'BangVape HU', revenue: '98,760', change: '15.2%', trend: 'up' },
  { id: 2, name: 'BangVape RO', revenue: '65,430', change: '8.3%', trend: 'up' },
  { id: 3, name: 'BangVape AT', revenue: '54,320', change: '12.1%', trend: 'up' },
  { id: 4, name: 'US Vape Shop', revenue: '45,670', change: '5.6%', trend: 'up' },
  { id: 5, name: 'Vape Pro DE', revenue: '25,380', change: '2.1%', trend: 'down' }
])

const conversionRanking = ref([
  { id: 1, name: 'BangVape AT', conversionRate: '2.79', change: '0.4%', trend: 'up' },
  { id: 2, name: 'BangVape HU', conversionRate: '2.70', change: '0.3%', trend: 'up' },
  { id: 3, name: 'BangVape RO', conversionRate: '2.53', change: '0.1%', trend: 'up' },
  { id: 4, name: 'Vape Pro DE', conversionRate: '2.32', change: '0.2%', trend: 'down' },
  { id: 5, name: 'US Vape Shop', conversionRate: '1.84', change: '0.5%', trend: 'up' }
])

const visitorRanking = ref([
  { id: 1, name: 'BangVape HU', visitors: '45,678', change: '18.5%', trend: 'up' },
  { id: 2, name: 'BangVape RO', visitors: '34,567', change: '12.3%', trend: 'up' },
  { id: 3, name: 'BangVape AT', visitors: '23,456', change: '9.7%', trend: 'up' },
  { id: 4, name: 'US Vape Shop', visitors: '18,765', change: '6.2%', trend: 'up' },
  { id: 5, name: 'Vape Pro DE', visitors: '5,990', change: '3.1%', trend: 'down' }
])

const refreshData = () => {
  ElMessage.success('数据已刷新')
}

const exportReport = () => {
  ElMessage.info('正在生成报告...')
}

const viewSiteDetail = (row) => {
  ElMessage.info(`正在查看 ${row.siteName} 详细数据...`)
}
</script>

<style scoped>
.funnel-dashboard {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.site-selector {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
}

.kpi-row {
  margin-bottom: 20px;
}

.kpi-card {
  text-align: center;
  border: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.kpi-card.blue .kpi-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.kpi-card.green .kpi-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.kpi-card.purple .kpi-icon {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
}

.kpi-card.orange .kpi-icon {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.kpi-card.cyan .kpi-icon {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin: 0 auto 12px;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.kpi-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.kpi-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.kpi-change.up {
  color: #10b981;
}

.kpi-change.down {
  color: #ef4444;
}

.kpi-change .vs {
  color: #9ca3af;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.funnel-chart {
  padding: 20px 0;
}

.funnel-stage {
  margin-bottom: 16px;
}

.funnel-bar {
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  color: #fff;
  font-weight: 600;
  margin-bottom: 4px;
  transition: width 0.5s ease;
}

.stage-0 .funnel-bar {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.stage-1 .funnel-bar {
  background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
}

.stage-2 .funnel-bar {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.stage-3 .funnel-bar {
  background: linear-gradient(90deg, #f97316 0%, #fb923c 100%);
}

.stage-4 .funnel-bar {
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.stage-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.stage-name {
  color: #374151;
  font-weight: 500;
}

.stage-rate {
  color: #6b7280;
}

.trend-chart-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.trend-chart-placeholder p {
  margin: 8px 0 4px;
  font-size: 14px;
}

.trend-chart-placeholder .hint {
  font-size: 12px;
  color: #d1d5db;
}

.product-list {
  max-height: 400px;
  overflow-y: auto;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.product-item:last-child {
  border-bottom: none;
}

.product-rank {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.product-rank.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #fff;
}

.product-rank.rank-2 {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  color: #fff;
}

.product-rank.rank-3 {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #fff;
}

.product-rank.abandon {
  background: #fee2e2;
  color: #ef4444;
}

.product-image {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  flex-shrink: 0;
}

.product-image.abandon {
  background: #fee2e2;
  color: #ef4444;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-meta {
  font-size: 12px;
  color: #6b7280;
}

.product-bar {
  width: 100px;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
  flex-shrink: 0;
}

.product-bar .bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
  border-radius: 3px;
}

.product-bar.abandon .bar-fill {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.insights-card {
  margin-bottom: 20px;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  background: #f9fafb;
}

.insight-item.warning {
  background: #fef3c720;
  border-left: 4px solid #f59e0b;
}

.insight-item.opportunity {
  background: #dbeafe20;
  border-left: 4px solid #3b82f6;
}

.insight-item.success {
  background: #d1fae520;
  border-left: 4px solid #10b981;
}

.insight-item.optimization {
  background: #ede9fe20;
  border-left: 4px solid #8b5cf6;
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
}

.insight-item.warning .insight-icon {
  background: #fef3c7;
  color: #f59e0b;
}

.insight-item.opportunity .insight-icon {
  background: #dbeafe;
  color: #3b82f6;
}

.insight-item.success .insight-icon {
  background: #d1fae5;
  color: #10b981;
}

.insight-item.optimization .insight-icon {
  background: #ede9fe;
  color: #8b5cf6;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.insight-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 8px;
}

.insight-data {
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  gap: 16px;
}

.insight-data .priority {
  color: #f59e0b;
  font-weight: 500;
}

.compare-card {
  margin-bottom: 20px;
}

.compare-table-wrapper {
  overflow-x: auto;
}

.high-rate {
  color: #10b981;
  font-weight: 600;
}

.low-rate {
  color: #f59e0b;
  font-weight: 600;
}

.ranking-card {
  height: 100%;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.rank-number {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.rank-number.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #fff;
}

.rank-number.rank-2 {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  color: #fff;
}

.rank-number.rank-3 {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #fff;
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-value {
  font-size: 12px;
  color: #6b7280;
}

.rank-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.rank-trend.up {
  color: #10b981;
}

.rank-trend.down {
  color: #ef4444;
}
</style>
