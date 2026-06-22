import api from './index'

// 登录
export function login(username: string, password: string) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  return api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

// 注册
export function register(data: { username: string; email: string; password: string; full_name?: string }) {
  return api.post('/auth/register', data)
}

// 获取当前用户信息
export function getCurrentUser() {
  return api.get('/auth/me')
}

// 登出
export function logout() {
  return api.post('/auth/logout')
}

// 刷新令牌
export function refreshToken() {
  return api.post('/auth/refresh')
}
