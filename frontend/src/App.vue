<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <h2>WPForge</h2>
        <p>WordPress AI仿站工具</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#1f2937"
        text-color="#9ca3af"
        active-text-color="#3b82f6"
      >
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/sites">
          <el-icon><Monitor /></el-icon>
          <span>站点管理</span>
        </el-menu-item>
        <el-menu-item index="/scraping">
          <el-icon><Collection /></el-icon>
          <span>采集任务</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>产品管理</span>
        </el-menu-item>
        <el-menu-item index="/translation">
          <el-icon><ChatDotRound /></el-icon>
          <span>翻译管理</span>
        </el-menu-item>
        <el-menu-item index="/seo">
          <el-icon><TrendCharts /></el-icon>
          <span>SEO工具</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务中心</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button type="primary" size="small" @click="goCreateTask">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ userStore.username || '用户' }}</span>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><UserFilled /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const currentPageName = computed(() => {
  const nameMap: Record<string, string> = {
    '/': '仪表盘',
    '/sites': '站点管理',
    '/scraping': '采集任务',
    '/products': '产品管理',
    '/translation': '翻译管理',
    '/seo': 'SEO工具',
    '/tasks': '任务中心',
    '/settings': '系统设置'
  }
  return nameMap[route.path] || '页面'
})

const goCreateTask = () => {
  router.push('/scraping')
}

const handleUserCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
      // 用户取消
    }
  } else if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中')
  }
}

onMounted(() => {
  userStore.restoreFromStorage()
})
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.sidebar {
  background-color: #1f2937;
  color: white;
}

.logo {
  padding: 24px 20px;
  border-bottom: 1px solid #374151;
}

.logo h2 {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: #3b82f6;
}

.logo p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #9ca3af;
}

.menu {
  border-right: none;
  margin-top: 16px;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  margin-left: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f3f4f6;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #1f2937;
}

.user-info .arrow {
  font-size: 12px;
  color: #6b7280;
}

.main-content {
  background-color: #f3f4f6;
  padding: 24px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
