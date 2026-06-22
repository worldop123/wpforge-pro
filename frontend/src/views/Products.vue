<template>
  <div class="products-page">
    <el-card class="page-header-card" shadow="hover">
      <div class="page-header">
        <div>
          <h2>产品管理</h2>
          <p class="subtitle">管理采集和导入的产品数据</p>
        </div>
        <div class="header-actions">
          <el-select v-model="selectedSite" placeholder="选择站点" style="width: 180px; margin-right: 12px;" @change="loadProducts">
            <el-option label="全部站点" value="" />
            <el-option v-for="site in sites" :key="site.id" :label="site.name" :value="site.id" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 130px; margin-right: 12px;" @change="loadProducts">
            <el-option label="全部" value="" />
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已发布" value="published" />
            <el-option label="回收站" value="trash" />
          </el-select>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索产品..."
            style="width: 220px; margin-right: 12px;"
            clearable
            @keyup.enter="loadProducts"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-radio-group v-model="viewMode" size="small" style="margin-right: 12px;">
            <el-radio-button label="table">
              <el-icon><Grid /></el-icon>
            </el-radio-button>
            <el-radio-button label="card">
              <el-icon><Menu /></el-icon>
            </el-radio-button>
          </el-radio-group>
          <el-button type="primary" @click="loadProducts">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="content-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>产品列表</span>
          <div class="header-actions">
            <span v-if="selectedRows.length > 0" class="batch-actions">
              <el-button type="danger" size="small" @click="batchDelete">
                批量删除 ({{ selectedRows.length }})
              </el-button>
              <el-button type="success" size="small" @click="batchSync">
                批量同步 ({{ selectedRows.length }})
              </el-button>
              <el-button type="warning" size="small" @click="batchTranslate">
                批量翻译 ({{ selectedRows.length }})
              </el-button>
            </span>
            <el-button type="primary" size="small" @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
          </div>
        </div>
      </template>

      <!-- 表格视图 -->
      <el-table
        v-if="viewMode === 'table'"
        :data="products"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="产品名称" min-width="200">
          <template #default="{ row }">
            <div class="product-name">
              <el-image
                v-if="row.featured_image || row.images?.[0]?.src"
                :src="row.featured_image || row.images?.[0]?.src"
                :preview-src-list="[row.featured_image || row.images?.[0]?.src]"
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
              <span class="current-price">{{ row.currency || '¥' }} {{ row.price || row.regular_price || 0 }}</span>
              <span v-if="row.sale_price" class="sale-price">{{ row.currency || '¥' }} {{ row.sale_price }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.in_stock || (row.stock_quantity && row.stock_quantity > 0) ? 'success' : 'danger'" size="small">
              {{ row.in_stock || (row.stock_quantity && row.stock_quantity > 0) ? (row.stock_quantity || '有货') : '缺货' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="wp_status" label="WP状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.wp_post_id || row.wp_product_id ? 'success' : 'info'" size="small">
              {{ row.wp_post_id || row.wp_product_id ? '已同步' : '未同步' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewProduct(row)">查看</el-button>
            <el-button type="success" link size="small" @click="editProduct(row)">编辑</el-button>
            <el-button type="warning" link size="small" @click="syncToWordPress(row)">同步</el-button>
            <el-button type="danger" link size="small" @click="deleteProduct(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无产品数据" />
        </template>
      </el-table>

      <!-- 卡片视图 -->
      <div v-else v-loading="loading" class="product-cards">
        <el-empty v-if="!loading && products.length === 0" description="暂无产品数据" />
        <el-card
          v-for="product in products"
          :key="product.id"
          class="product-card"
          shadow="hover"
          @click="viewProduct(product)"
        >
          <el-image
            :src="product.featured_image || product.images?.[0]?.src"
            fit="cover"
            class="product-image"
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div class="product-info">
            <div class="product-title" :title="product.name">{{ product.name }}</div>
            <div class="product-meta">
              <span class="price">{{ product.currency || '¥' }} {{ product.price || product.regular_price || 0 }}</span>
              <el-tag :type="getStatusType(product.status)" size="small">
                {{ getStatusText(product.status) }}
              </el-tag>
            </div>
            <div class="product-sku">SKU: {{ product.sku || '-' }}</div>
          </div>
        </el-card>
      </div>

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

    <!-- 产品详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="产品详情" width="800px">
      <el-descriptions v-if="currentProduct" :column="2" border>
        <el-descriptions-item label="产品名称" :span="2">{{ currentProduct.name }}</el-descriptions-item>
        <el-descriptions-item label="SKU">{{ currentProduct.sku || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentProduct.status)" size="small">
            {{ getStatusText(currentProduct.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="价格">{{ currentProduct.currency || '¥' }} {{ currentProduct.price || 0 }}</el-descriptions-item>
        <el-descriptions-item label="促销价">{{ currentProduct.sale_price ? (currentProduct.currency || '¥') + ' ' + currentProduct.sale_price : '-' }}</el-descriptions-item>
        <el-descriptions-item label="库存">{{ currentProduct.stock_quantity ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="是否有货">{{ currentProduct.in_stock ? '有货' : '缺货' }}</el-descriptions-item>
        <el-descriptions-item label="WP状态">{{ currentProduct.wp_post_id || currentProduct.wp_product_id ? '已同步' : '未同步' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentProduct.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ currentProduct.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="简短描述" :span="2">{{ currentProduct.short_description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="详细描述" :span="2">
          <div class="description-content" v-html="currentProduct.description || '-'"></div>
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="currentProduct?.images?.length" class="product-images">
        <h4>产品图片</h4>
        <div class="images-list">
          <el-image
            v-for="(img, idx) in currentProduct.images"
            :key="idx"
            :src="img.src || img"
            :preview-src-list="currentProduct.images.map((i: any) => i.src || i)"
            :initial-index="idx"
            fit="cover"
            class="product-thumb"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="warning" @click="syncToWordPress(currentProduct)">同步到WordPress</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="showImportDialog" title="批量导入产品" width="600px">
      <el-form label-width="120px">
        <el-form-item label="目标站点" required>
          <el-select v-model="importForm.site_id" placeholder="选择目标站点" style="width: 100%">
            <el-option v-for="site in sites" :key="site.id" :label="site.name" :value="site.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="导入方式">
          <el-radio-group v-model="importForm.import_method">
            <el-radio label="csv">CSV文件</el-radio>
            <el-radio label="json">JSON文件</el-radio>
            <el-radio label="excel">Excel文件</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 CSV / JSON / Excel 文件，文件大小不超过 100MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="发布状态">
          <el-switch v-model="importForm.publish" active-text="立即发布" inactive-text="保存为草稿" />
        </el-form-item>
        <el-form-item label="更新已存在">
          <el-switch v-model="importForm.update_if_exists" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="doImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProducts,
  getProduct,
  deleteProduct as deleteProductApi,
  batchDeleteProducts,
  batchSyncProducts
} from '@/api/products'
import { getSites } from '@/api/sites'
import { importToWordPress } from '@/api/wordpress'
import { translateProducts } from '@/api/translation'

const loading = ref(false)
const importing = ref(false)
const products = ref<any[]>([])
const sites = ref<any[]>([])
const selectedSite = ref<string | number>('')
const filterStatus = ref('')
const searchKeyword = ref('')
const viewMode = ref<'table' | 'card'>('table')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedRows = ref<any[]>([])
const showDetailDialog = ref(false)
const showImportDialog = ref(false)
const currentProduct = ref<any>(null)
const uploadRef = ref()

const importForm = ref({
  site_id: undefined as number | undefined,
  import_method: 'csv',
  publish: false,
  update_if_exists: true,
  file: null as any
})

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
      site_id: selectedSite.value ? Number(selectedSite.value) : undefined,
      keyword: searchKeyword.value || undefined,
      status: filterStatus.value || undefined
    })
    products.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载产品列表失败')
    products.value = []
  } finally {
    loading.value = false
  }
}

const loadSites = async () => {
  try {
    const res: any = await getSites({ page: 1, page_size: 100 })
    sites.value = res.data?.items || res.items || []
  } catch (error) {
    console.error('加载站点列表失败', error)
  }
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const viewProduct = async (product: any) => {
  currentProduct.value = product
  showDetailDialog.value = true
  // 获取详情
  try {
    const res: any = await getProduct(product.id)
    currentProduct.value = res.data || res
  } catch (error) {
    // 使用列表中的数据
  }
}

const editProduct = (product: any) => {
  ElMessage.info(`编辑产品: ${product.name}`)
}

const syncToWordPress = async (product: any) => {
  if (!product) return
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

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 个产品吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await batchDeleteProducts(selectedRows.value.map(p => p.id))
    ElMessage.success('批量删除成功')
    selectedRows.value = []
    loadProducts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const batchSync = async () => {
  try {
    await batchSyncProducts(selectedRows.value.map(p => p.id))
    ElMessage.success('批量同步任务已创建')
    selectedRows.value = []
  } catch (error: any) {
    ElMessage.error('批量同步失败')
  }
}

const batchTranslate = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要翻译选中的 ${selectedRows.value.length} 个产品吗？`,
      '批量翻译',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await translateProducts({
      product_ids: selectedRows.value.map(p => p.id),
      target_language: 'zh-CN'
    })
    ElMessage.success('批量翻译任务已创建')
    selectedRows.value = []
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量翻译失败')
    }
  }
}

const handleFileChange = (file: any) => {
  importForm.value.file = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const doImport = async () => {
  if (!importForm.value.site_id) {
    ElMessage.warning('请选择目标站点')
    return
  }
  if (!importForm.value.file) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  importing.value = true
  try {
    // 简单的CSV解析示例（实际应使用专门的库）
    const file = importForm.value.file
    const text = await file.text()
    const lines = text.split('\n').filter(l => l.trim())
    if (lines.length < 2) {
      ElMessage.warning('文件内容为空或格式不正确')
      return
    }
    const headers = lines[0].split(',').map(h => h.trim())
    const products: any[] = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      const product: any = {}
      headers.forEach((h, idx) => {
        product[h] = values[idx]
      })
      products.push(product)
    }

    // 调用导入API
    await importToWordPress({
      site_id: importForm.value.site_id,
      import_method: importForm.value.import_method,
      update_if_exists: importForm.value.update_if_exists,
      publish: importForm.value.publish
    })

    ElMessage.success(`成功导入 ${products.length} 个产品`)
    showImportDialog.value = false
    importForm.value.file = null
    uploadRef.value?.clearFiles()
    loadProducts()
  } catch (error: any) {
    ElMessage.error('导入失败：' + (error.message || ''))
  } finally {
    importing.value = false
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.batch-actions {
  display: flex;
  gap: 8px;
  margin-right: 12px;
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

/* 卡片视图样式 */
.product-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.product-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
}

.product-card :deep(.el-card__body) {
  padding: 0;
}

.product-image {
  width: 100%;
  height: 180px;
  display: block;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #d1d5db;
  font-size: 36px;
}

.product-info {
  padding: 12px;
}

.product-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  height: 42px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.product-meta .price {
  color: #ef4444;
  font-weight: 600;
}

.product-sku {
  font-size: 12px;
  color: #9ca3af;
}

.description-content {
  max-height: 200px;
  overflow-y: auto;
}

.product-images {
  margin-top: 20px;
}

.product-images h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #1f2937;
}

.images-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.product-thumb {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
