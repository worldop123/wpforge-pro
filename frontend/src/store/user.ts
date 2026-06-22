import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<any>(null)
  const isLoggedIn = ref<boolean>(!!token.value)
  const loading = ref<boolean>(false)

  // 计算属性
  const username = computed(() => user.value?.username || '')
  const email = computed(() => user.value?.email || '')
  const avatar = computed(() => user.value?.avatar || '')
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 登录
  async function login(username: string, password: string) {
    loading.value = true
    try {
      const result: any = await apiLogin(username, password)
      token.value = result.access_token
      localStorage.setItem('token', result.access_token)
      isLoggedIn.value = true
      
      // 获取用户信息
      await fetchUser()
      
      return result
    } finally {
      loading.value = false
    }
  }

  // 登出
  async function logout() {
    try {
      await apiLogout()
    } catch (e) {
      // 忽略登出错误
    } finally {
      token.value = null
      user.value = null
      isLoggedIn.value = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  // 获取用户信息
  async function fetchUser() {
    try {
      const result: any = await getCurrentUser()
      user.value = result.data
      localStorage.setItem('user', JSON.stringify(result.data))
      return result.data
    } catch (e) {
      // 如果获取用户信息失败，可能是token过期
      logout()
      throw e
    }
  }

  // 从本地存储恢复用户信息
  function restoreFromStorage() {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('解析用户信息失败', e)
      }
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    loading,
    username,
    email,
    avatar,
    isAdmin,
    login,
    logout,
    fetchUser,
    restoreFromStorage,
  }
})
