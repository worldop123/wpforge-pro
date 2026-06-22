import request from './request'

// 管理员登录
export function login(username, password) {
  return request.post('/auth/login', { username, password })
}

export default {
  login
}
