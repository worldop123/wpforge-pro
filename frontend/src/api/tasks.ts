import api from './index'

// 获取任务列表
export function getTasks(params?: { 
  page?: number; 
  page_size?: number; 
  status?: string;
  task_type?: string;
  site_id?: number;
}) {
  return api.get('/tasks', { params })
}

// 获取任务详情
export function getTask(id: number) {
  return api.get(`/tasks/${id}`)
}

// 创建任务
export function createTask(data: any) {
  return api.post('/tasks', data)
}

// 更新任务
export function updateTask(id: number, data: any) {
  return api.put(`/tasks/${id}`, data)
}

// 删除任务
export function deleteTask(id: number) {
  return api.delete(`/tasks/${id}`)
}

// 取消任务
export function cancelTask(id: number) {
  return api.post(`/tasks/${id}/cancel`)
}

// 重试任务
export function retryTask(id: number) {
  return api.post(`/tasks/${id}/retry`)
}

// 获取任务日志
export function getTaskLogs(id: number, params?: { page?: number; page_size?: number }) {
  return api.get(`/tasks/${id}/logs`, { params })
}

// 获取任务统计
export function getTaskStats() {
  return api.get('/tasks/stats')
}

// 批量删除任务
export function batchDeleteTasks(ids: number[]) {
  return api.post('/tasks/batch-delete', { ids })
}
