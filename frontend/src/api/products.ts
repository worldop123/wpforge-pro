import api from './index'

// 获取产品列表
export function getProducts(params?: { 
  page?: number; 
  page_size?: number; 
  site_id?: number;
  keyword?: string;
  category_id?: number;
  status?: string;
}) {
  return api.get('/products', { params })
}

// 获取产品详情
export function getProduct(id: number) {
  return api.get(`/products/${id}`)
}

// 创建产品
export function createProduct(data: any) {
  return api.post('/products', data)
}

// 更新产品
export function updateProduct(id: number, data: any) {
  return api.put(`/products/${id}`, data)
}

// 删除产品
export function deleteProduct(id: number) {
  return api.delete(`/products/${id}`)
}

// 批量删除产品
export function batchDeleteProducts(ids: number[]) {
  return api.post('/products/batch-delete', { ids })
}

// 同步产品
export function syncProduct(id: number) {
  return api.post(`/products/${id}/sync`)
}

// 批量同步产品
export function batchSyncProducts(ids: number[]) {
  return api.post('/products/batch-sync', { ids })
}

// 获取产品分类
export function getProductCategories(siteId?: number) {
  return api.get('/products/categories', { params: { site_id: siteId } })
}
