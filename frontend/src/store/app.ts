import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const sidebarCollapsed = ref<boolean>(false)
  const darkMode = ref<boolean>(false)
  const language = ref<string>('zh-CN')
  const loading = ref<boolean>(false)
  const advancedMode = ref<boolean>(false)

  // 计算属性
  const isSidebarCollapsed = computed(() => sidebarCollapsed.value)
  const isDarkMode = computed(() => darkMode.value)
  const isAdvancedMode = computed(() => advancedMode.value)

  // 切换侧边栏
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 切换深色模式
  function toggleDarkMode() {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', String(darkMode.value))
    
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 切换高级模式
  function toggleAdvancedMode() {
    advancedMode.value = !advancedMode.value
    localStorage.setItem('advancedMode', String(advancedMode.value))
  }

  // 设置语言
  function setLanguage(lang: string) {
    language.value = lang
    localStorage.setItem('language', lang)
  }

  // 显示加载状态
  function showLoading() {
    loading.value = true
  }

  // 隐藏加载状态
  function hideLoading() {
    loading.value = false
  }

  // 从本地存储恢复设置
  function restoreFromStorage() {
    const storedDarkMode = localStorage.getItem('darkMode')
    if (storedDarkMode === 'true') {
      darkMode.value = true
      document.documentElement.classList.add('dark')
    }

    const storedAdvancedMode = localStorage.getItem('advancedMode')
    if (storedAdvancedMode === 'true') {
      advancedMode.value = true
    }

    const storedLanguage = localStorage.getItem('language')
    if (storedLanguage) {
      language.value = storedLanguage
    }
  }

  return {
    sidebarCollapsed,
    darkMode,
    language,
    loading,
    advancedMode,
    isSidebarCollapsed,
    isDarkMode,
    isAdvancedMode,
    toggleSidebar,
    toggleDarkMode,
    toggleAdvancedMode,
    setLanguage,
    showLoading,
    hideLoading,
    restoreFromStorage,
  }
})
