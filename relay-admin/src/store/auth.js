import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('relay_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('relay_user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    try {
      const result = await apiLogin(username, password)
      if (result.success) {
        token.value = result.token
        user.value = result.user
        localStorage.setItem('relay_token', result.token)
        localStorage.setItem('relay_user', JSON.stringify(result.user))
        return true
      }
      return false
    } catch (err) {
      console.error('Login error:', err)
      return false
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('relay_token')
    localStorage.removeItem('relay_user')
  }

  function getToken() {
    return token.value
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout,
    getToken
  }
})
