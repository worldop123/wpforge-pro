import api from './index'

// 导入到WordPress
export function importToWordPress(data: {
  site_id: number;
  product_ids?: number[];
  import_method?: string;
  update_if_exists?: boolean;
  skip_images?: boolean;
  publish?: boolean;
}) {
  return api.post('/wordpress/import', data)
}

// 测试WordPress连接
export function testWordPressConnection(site_id: number) {
  return api.post('/wordpress/test-connection', null, {
    params: { site_id }
  })
}

// 获取导入方式列表
export function getImportMethods() {
  return api.get('/wordpress/import-methods')
}

// 检查WordPress兼容性
export function checkWordPressCompatibility(site_id: number) {
  return api.post('/wordpress/check-compatibility', null, {
    params: { site_id }
  })
}

// 获取WordPress产品分类
export function getWordPressCategories(site_id: number) {
  return api.get('/wordpress/categories', {
    params: { site_id }
  })
}

// 获取WordPress产品列表
export function getWordPressProducts(site_id: number, params?: {
  page?: number;
  per_page?: number;
}) {
  return api.get('/wordpress/products', {
    params: { site_id, ...params }
  })
}
