<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="logo">WPForge</h1>
        <p class="subtitle">WordPress AI仿站原创系统</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
              <el-link type="primary" :underline="false" @click="forgotPassword">忘记密码？</el-link>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="switch-text">
            还没有账号？
            <el-link type="primary" :underline="false" @click="activeTab = 'register'">立即注册</el-link>
          </div>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
            @keyup.enter="handleRegister"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>

            <el-form-item prop="full_name">
              <el-input
                v-model="registerForm.full_name"
                placeholder="请输入姓名（可选）"
                size="large"
                :prefix-icon="UserFilled"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="registerLoading"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>

          <div class="switch-text">
            已有账号？
            <el-link type="primary" :underline="false" @click="activeTab = 'login'">返回登录</el-link>
          </div>
        </el-tab-pane>
      </el-tabs>

      <div class="login-footer">
        <p>默认账号: admin / admin123</p>
        <p class="copyright">© 2024 WPForge. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Message, UserFilled } from '@element-plus/icons-vue'
import { login, register } from '@/api/auth'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref<'login' | 'register'>('login')
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const registerLoading = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: 'admin123',
  remember: true
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ]
}

const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res: any = await login(
          loginForm.username,
          loginForm.password
        )

        // 保存token
        if (loginForm.remember) {
          localStorage.setItem('token', res.access_token)
          localStorage.setItem('user', JSON.stringify(res.user))
        } else {
          sessionStorage.setItem('token', res.access_token)
          sessionStorage.setItem('user', JSON.stringify(res.user))
        }

        // 更新用户状态
        userStore.user = res.user
        userStore.token = res.access_token
        userStore.isLoggedIn = true

        ElMessage.success('登录成功')
        router.push('/')
      } catch (error: any) {
        ElMessage.error(error.message || '登录失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      try {
        await register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          full_name: registerForm.full_name || undefined
        })
        ElMessage.success('注册成功，请登录')
        // 复制用户名到登录表单
        loginForm.username = registerForm.username
        loginForm.password = ''
        activeTab.value = 'login'
      } catch (error: any) {
        ElMessage.error(error.message || '注册失败')
      } finally {
        registerLoading.value = false
      }
    }
  })
}

const forgotPassword = () => {
  ElMessage.info('请联系管理员重置密码')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  background: white;
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 36px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px;
}

.subtitle {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.login-tabs {
  margin-bottom: 16px;
}

.login-form {
  margin-bottom: 16px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.switch-text {
  text-align: center;
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 8px;
}

.login-footer {
  text-align: center;
  color: #9ca3af;
  font-size: 13px;
  border-top: 1px solid #f3f4f6;
  padding-top: 20px;
}

.login-footer p {
  margin: 4px 0;
}

.copyright {
  font-size: 12px;
  color: #d1d5db;
}
</style>
