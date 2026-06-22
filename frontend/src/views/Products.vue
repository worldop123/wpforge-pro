<template>
  <div class="products-page">
    <el-card class="page-header-card">
      <div class="page-header">
        <div>
          <h2>产品管理</h2>
          <p class="subtitle">管理采集和导入的产品数据</p>
        </div>
        <div class="header-actions">
          <el-select v-model="selectedSite" placeholder="选择站点" style="width: 200px; margin-right: 12px;">
            <el-option label="全部站点" value="" />
            <el-option v-for="site in sites" :key="site.id" :label="site.name" :value="site.id" />
          </el-select>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索产品..."
            style="width: 250px; margin-right: 12px;"
            clearable
            @keyup.enter="loadProducts"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="loadProducts">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="content-card">
      <el-table :data="products" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="产品名称" min-width="200">
          <template #default="{ row }">
            <div class="product-name">
              <el-image
                v-if="row.featured_image"
                :src="row.featured_image"
                :preview-src-list="[row.featured_image]"
                fit="cover"
                style="width: 50px; height: 50px; margin-right: 12px; border-radius: 4px;"
              />
              <div>
                <div class="name">{{ row.name }}</div>
                <div class="sku">SKU: {{ row.sku || '-' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            <div class="price">
              <span class="current-price">{{ row.currency }} {{ row.price }}</span>
              <span v-if="row.sale_price" class="sale-price">{{ row.currency }} {{ row.sale_price }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.in_stock ? 'success' : 'danger'">
              {{ row.in_stock ? row.stock_quantity : '缺货' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="wp_status" label="WP状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.wp_post_id ? 'success' : 'info'">
              {{ row.wp_post_id ? '已同步' : '未同步' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewProduct(row)">
              查看
            </el-button>
            <el-button type="success" link size="small" @click="editProduct(row)">
              编辑
            </el-button>
            <el-button type="warning" link size="small" @click="syncToWordPress(row)">
              同步
            </el-button>
            <el-button type="danger" link size="small" @click="deleteProduct(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProducts, deleteProduct as deleteProductApi } from '@/api/products'
import { getSites } from '@/api/sites'

const loading = ref(false)
const products = ref<any[]>([])
const sites = ref<any[]>([])
const selectedSite = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    published: 'success',
    trash: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    published: '已发布',
    trash: '回收站'
  }
  return map[status] || status
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res: any = await getProducts({
      page: currentPage.value,
      page_size: pageSize.value,
      site_id: selectedSite.value || undefined,
      search: searchKeyword.value || undefined
    })
    products.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载产品列表失败')
  } finally {
    loading.value = false
  }
}

const loadSites = async () => {
  try {
    const res: any = await getSites({ page: 1, page_size: 100 })
    sites.value = res.data?.items || []
  } catch (error) {
    console.error('加载站点列表失败', error)
  }
}

const viewProduct = (product: any) => {
  ElMessage.info(`查看产品: ${product.name}`)
}

const editProduct = (product: any) => {
  ElMessage.info(`编辑产品: ${product.name}`)
}

const syncToWordPress = async (product: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要将产品 "${product.name}" 同步到WordPress吗？`,
      '确认同步',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success('同步任务已创建')
  } catch {
    // 用户取消
  }
}

const deleteProduct = async (product: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品 "${product.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteProductApi(product.id)
    ElMessage.success('删除成功')
    loadProducts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadProducts()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadProducts()
}

onMounted(() => {
  loadSites()
  loadProducts()
})
</script>

<style scoped>
.products-page {
  padding: 0;
}

.page-header-card {
  margin-bottom: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.content-card {
  margin-bottom: 20px;
}

.product-name {
  display: flex;
  align-items: center;
}

.product-name .name {
  font-weight: 500;
  color: #1f2937;
}

.product-name .sku {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.price {
  display: flex;
  flex-direction: column;
}

.current-price {
  font-weight: 600;
  color: #1f2937;
}

.sale-price {
  font-size: 12px;
  color: #ef4444;
  text-decoration: line-through;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
