<template>
  <div class="funnel-dashboard" v-loading="loading" element-loading-text="加载漏斗数据中...">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2>电商漏斗数据</h2>
        <p>多站点电商转化数据集中管理与分析</p>
      </div>
      <div class="header-actions">
        <el-select v-model="timeRange" style="width: 150px" @change="loadAll">
          <el-option label="今天" value="today" />
          <el-option label="昨天" value="yesterday" />
          <el-option label="近7天" value="7days" />
          <el-option label="近30天" value="30days" />
          <el-option label="本月" value="thisMonth" />
          <el-option label="上月" value="lastMonth" />
        </el-select>
        <el-button type="primary" @click="loadAll">
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

      <el-select v-model="selectedSites" multiple placeholder="选择站点（留空查看全部）" style="width: 400px" @change="loadAll">
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
              <el-empty v-if="!funnelData.length" description="暂无漏斗数据" :image-size="80" />
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
                <el-radio-group v-model="trendView" size="small" @change="updateTrendChart">
                  <el-radio-button label="sales">销售额</el-radio-button>
                  <el-radio-button label="orders">订单数</el-radio-button>
                  <el-radio-button label="conversion">转化率</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="trendChartRef" class="trend-chart"></div>
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
                <el-select v-model="hotProductsSort" size="small" style="width: 120px" @change="loadTopProducts">
                  <el-option label="按销量" value="sales" />
                  <el-option label="按销售额" value="revenue" />
                  <el-option label="按加购数" value="cart" />
                </el-select>
              </div>
            </template>
            <div class="product-list">
              <el-empty v-if="!hotProducts.length" description="暂无热销产品" :image-size="60" />
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
                    :style="{ width: (hotProducts[0]?.sales ? product.sales / hotProducts[0].sales * 100 : 0) + '%' }"
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
                <el-select v-model="abandonedSort" size="small" style="width: 120px" @change="loadTopProducts">
                  <el-option label="按弃购率" value="rate" />
                  <el-option label="按弃购数" value="count" />
                  <el-option label="按金额" value="amount" />
                </el-select>
              </div>
            </template>
            <div class="product-list">
              <el-empty v-if="!abandonedProducts.length" description="暂无弃购产品" :image-size="60" />
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
                    :style="{ width: product.abandonRate + '%' }"
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
          <el-empty v-if="!insights.length" description="暂无洞察数据" :image-size="60" />
          <div
            v-for="(insight, index) in insights"
            :key="index"
            class="insight-item"
            :class="insight.type"
          >
            <div class="insight-icon">
              <span class="insight-emoji">{{ insight.icon || '💡' }}</span>
            </div>
            <div class="insight-content">
              <div class="insight-title">{{ insight.title }}</div>
              <div class="insight-desc">{{ insight.description }}</div>
              <div class="insight-data">
                <span v-if="insight.data">数据依据: {{ insight.data }}</span>
                <span class="priority" v-if="insight.priority">优先级: {{ insight.priority }}</span>
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
          <el-table :data="compareData" style="width: 100%" v-loading="loading">
            <el-table-column prop="siteName" label="站点" width="200" fixed />
            <el-table-column prop="visitors" label="访客数" sortable />
            <el-table-column prop="productViews" label="浏览产品" sortable />
            <el-table-column prop="cartAdds" label="加购数" sortable />
            <el-table-column prop="checkouts" label="结账数" sortable />
            <el-table-column prop="orders" label="订单数" sortable />
            <el-table-column prop="revenue" label="销售额" sortable>
              <template #default="{ row }">
                ¥{{ row.revenue }}
              </template>
            </el-table-column>
            <el-table-column prop="conversionRate" label="转化率" sortable>
              <template #default="{ row }">
                <span :class="row.conversionRate > 3 ? 'high-rate' : 'low-rate'">
                  {{ row.conversionRate }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="avgOrderValue" label="客单价" sortable>
              <template #default="{ row }">
                ¥{{ row.avgOrderValue }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="viewSiteDetail(row)">详情</el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="暂无对比数据" />
            </template>
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
              <el-empty v-if="!revenueRanking.length" description="暂无数据" :image-size="60" />
              <div
                v-for="(site, index) in revenueRanking"
                :key="site.siteId"
                class="ranking-item"
              >
                <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ site.siteName }}</div>
                  <div class="rank-value">¥{{ site.revenue }}</div>
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
              <el-empty v-if="!conversionRanking.length" description="暂无数据" :image-size="60" />
              <div
                v-for="(site, index) in conversionRanking"
                :key="site.siteId"
                class="ranking-item"
              >
                <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ site.siteName }}</div>
                  <div class="rank-value">{{ site.conversionRate }}%</div>
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
              <el-empty v-if="!visitorRanking.length" description="暂无数据" :image-size="60" />
              <div
                v-for="(site, index) in visitorRanking"
                :key="site.siteId"
                class="ranking-item"
              >
                <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
                <div class="rank-info">
                  <div class="rank-name">{{ site.siteName }}</div>
                  <div class="rank-value">{{ site.visitors }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download,
  Goods,
  MagicStick,
  Top,
  Bottom,
  User,
  ShoppingCart,
  Money,
  TrendCharts,
} from '@element-plus/icons-vue'
import {
  getFunnelOverview,
  getFunnelSalesTrend,
  getFunnelTopProducts,
  getFunnelInsights,
  getFunnelComparison,
} from '@/api/funnel'

const loading = ref(false)
const timeRange = ref('30days')
const viewMode = ref('overview')
const selectedSites = ref<number[]>([])
const funnelView = ref('percent')
const trendView = ref<'sales' | 'orders' | 'conversion'>('sales')
const hotProductsSort = ref('sales')
const abandonedSort = ref('rate')

const sites = ref<Array<{ id: number; name: string }>>([])
const trendData = ref<Array<{ date: string; revenue: number; orders: number; visitors: number }>>([])

// KPI 配置（图标固定，数值来自接口）
const kpiData = ref([
  { key: 'visitors', label: '总访客数', value: '0', change: '-', trend: 'up', icon: User, color: 'blue' },
  { key: 'orders', label: '总订单数', value: '0', change: '-', trend: 'up', icon: ShoppingCart, color: 'green' },
  { key: 'revenue', label: '总销售额', value: '¥0', change: '-', trend: 'up', icon: Money, color: 'purple' },
  { key: 'conversion', label: '整体转化率', value: '0%', change: '-', trend: 'up', icon: TrendCharts, color: 'orange' },
  { key: 'aov', label: '客单价', value: '¥0', change: '-', trend: 'up', icon: Goods, color: 'cyan' },
])

const funnelData = ref<Array<{ name: string; value: string | number; percent: number; conversionRate: string | number }>>([])
const hotProducts = ref<Array<any>>([])
const abandonedProducts = ref<Array<any>>([])
const insights = ref<Array<any>>([])
const compareData = ref<Array<any>>([])

const revenueRanking = ref<Array<any>>([])
const conversionRanking = ref<Array<any>>([])
const visitorRanking = ref<Array<any>>([])

const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

// 格式化数字
const formatNumber = (n: number): string => {
  if (!n) return '0'
  return n.toLocaleString('zh-CN')
}

// 选中的站点ID字符串
const siteIdsParam = (): string => {
  return selectedSites.value.length ? selectedSites.value.join(',') : ''
}

// 加载概览数据
const loadOverview = async () => {
  try {
    const res: any = await getFunnelOverview({ time_range: timeRange.value, site_ids: siteIdsParam() })
    const data = res.data || res
    sites.value = data.sites || []
    const metrics = data.metrics || {}

    // 更新 KPI
    kpiData.value[0].value = formatNumber(metrics.visitors || 0)
    kpiData.value[1].value = formatNumber(metrics.orders || metrics.purchases || 0)
    kpiData.value[2].value = '¥' + formatNumber(Math.round(metrics.revenue || 0))
    kpiData.value[3].value = (metrics.conversion_rate || 0) + '%'
    kpiData.value[4].value = '¥' + (metrics.avg_order_value || 0)

    // 构建漏斗层级
    const stages = data.stages || []
    const maxVal = stages.length ? Math.max(...stages.map((s: any) => s.value || 0), 1) : 1
    funnelData.value = stages.map((s: any) => ({
      name: s.name,
      value: formatNumber(s.value || 0),
      percent: maxVal ? Math.round((s.value / maxVal) * 100) : 0,
      conversionRate: s.conversion_from_prev ?? 0,
    }))
  } catch (error) {
    console.warn('加载漏斗概览失败', error)
  }
}

// 加载销售趋势
const loadSalesTrend = async () => {
  try {
    const res: any = await getFunnelSalesTrend({ time_range: timeRange.value, site_ids: siteIdsParam() })
    trendData.value = (res.data || res) || []
  } catch (error) {
    console.warn('加载销售趋势失败', error)
    trendData.value = []
  }
  await nextTick()
  updateTrendChart()
}

// 更新趋势图
const updateTrendChart = () => {
  if (!trendChartRef.value) return
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }

  const dates = trendData.value.map((d) => d.date)
  let seriesData: number[] = []
  let seriesName = '销售额'

  if (trendView.value === 'sales') {
    seriesData = trendData.value.map((d) => Number(d.revenue || 0))
    seriesName = '销售额'
  } else if (trendView.value === 'orders') {
    seriesData = trendData.value.map((d) => Number(d.orders || 0))
    seriesName = '订单数'
  } else {
    seriesData = trendData.value.map((d) => {
      const v = Number(d.visitors || 0)
      return v ? Number(((d.orders / v) * 100).toFixed(2)) : 0
    })
    seriesName = '转化率(%)'
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value' },
    series: [
      {
        name: seriesName,
        type: 'line',
        smooth: true,
        data: seriesData,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.5)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' },
          ]),
        },
        lineStyle: { color: '#3b82f6', width: 2 },
        itemStyle: { color: '#3b82f6' },
      },
    ],
  }
  trendChart.setOption(option, true)
}

// 加载热销/弃购产品
const loadTopProducts = async () => {
  try {
    const orderBy = hotProductsSort.value === 'cart' ? 'add_to_cart' : hotProductsSort.value
    const res: any = await getFunnelTopProducts({
      time_range: timeRange.value,
      order_by: orderBy,
      limit: 20,
      site_ids: siteIdsParam(),
    })
    const products = (res.data || res) || []

    // 热销产品：按当前排序
    const hotSorted = [...products].sort((a, b) => {
      const key = hotProductsSort.value === 'sales' ? 'sales' : hotProductsSort.value === 'revenue' ? 'revenue' : 'add_to_cart'
      return (b[key] || 0) - (a[key] || 0)
    })
    hotProducts.value = hotSorted.slice(0, 10)

    // 弃购产品：按弃购率/弃购数/金额
    const abanSorted = [...products].sort((a, b) => {
      if (abandonedSort.value === 'rate') return (b.abandonRate || 0) - (a.abandonRate || 0)
      if (abandonedSort.value === 'amount') return (b.amount || 0) - (a.amount || 0)
      // count = add_to_cart - sales
      return ((b.add_to_cart || 0) - (b.sales || 0)) - ((a.add_to_cart || 0) - (a.sales || 0))
    })
    abandonedProducts.value = abanSorted.slice(0, 10)
  } catch (error) {
    console.warn('加载热销产品失败', error)
    hotProducts.value = []
    abandonedProducts.value = []
  }
}

// 加载 AI 洞察
const loadInsights = async () => {
  try {
    const res: any = await getFunnelInsights({ time_range: timeRange.value, site_ids: siteIdsParam() })
    const data = res.data || res
    insights.value = data.insights || []
  } catch (error) {
    console.warn('加载洞察失败', error)
    insights.value = []
  }
}

// 加载对比数据
const loadComparison = async () => {
  try {
    const res: any = await getFunnelComparison({ time_range: timeRange.value, site_ids: siteIdsParam() })
    compareData.value = (res.data || res) || []
    // 构建排名
    revenueRanking.value = [...compareData.value].sort((a, b) => (b.revenue || 0) - (a.revenue || 0))
    conversionRanking.value = [...compareData.value].sort((a, b) => (b.conversionRate || 0) - (a.conversionRate || 0))
    visitorRanking.value = [...compareData.value].sort((a, b) => (b.visitors || 0) - (a.visitors || 0))
  } catch (error) {
    console.warn('加载对比数据失败', error)
    compareData.value = []
  }
}

// 加载全部数据
const loadAll = async () => {
  loading.value = true
  try {
    await Promise.allSettled([
      loadOverview(),
      loadSalesTrend(),
      loadTopProducts(),
      loadInsights(),
      loadComparison(),
    ])
  } finally {
    loading.value = false
  }
}

const exportReport = () => {
  ElMessage.info('正在生成报告，请稍候...')
}

const viewSiteDetail = (row: any) => {
  ElMessage.info(`正在查看 ${row.siteName} 详细数据...`)
}

const handleResize = () => {
  trendChart?.resize()
}

// 切换视图模式时加载对比数据
watch(viewMode, (val) => {
  if (val === 'compare' || val === 'ranking') {
    if (!compareData.value.length) loadComparison()
  }
})

onMounted(async () => {
  await loadAll()
  await nextTick()
  updateTrendChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  trendChart = null
})
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

.trend-chart {
  width: 100%;
  height: 300px;
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

.insight-item.critical {
  background: #fee2e220;
  border-left: 4px solid #ef4444;
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
  background: #f3f4f6;
}

.insight-emoji {
  font-size: 20px;
  line-height: 1;
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
</style>
