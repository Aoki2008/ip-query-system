<template>
  <div class="auth-page">
    <div class="auth-container">
      <!-- 背景装饰 -->
      <div class="auth-background">
        <div class="floating-shapes">
          <div class="shape shape-1"></div>
          <div class="shape shape-2"></div>
          <div class="shape shape-3"></div>
        </div>
      </div>

      <!-- 认证表单容器 -->
      <div class="auth-content">
        <!-- 标题区域 -->
        <div class="auth-header">
          <h1>IP查询工具</h1>
          <p>专业的IP地址查询和分析平台</p>
        </div>

        <!-- 表单切换标签 -->
        <div class="auth-tabs">
          <button
            :class="{ active: currentTab === 'login' }"
            @click="currentTab = 'login'"
          >
            登录
          </button>
          <button
            :class="{ active: currentTab === 'register' }"
            @click="currentTab = 'register'"
          >
            注册
          </button>
        </div>

        <!-- 表单内容 -->
        <div class="auth-forms">
          <Transition name="slide" mode="out-in">
            <LoginForm
              v-if="currentTab === 'login'"
              key="login"
              @switch-to-register="currentTab = 'register'"
              @forgot-password="showForgotPassword = true"
            />
            <RegisterForm
              v-else
              key="register"
              @switch-to-login="currentTab = 'login'"
            />
          </Transition>
        </div>

        <!-- 功能特色 -->
        <div class="auth-features">
          <div class="feature">
            <div class="feature-icon">🌍</div>
            <div class="feature-text">
              <h3>全球IP数据库</h3>
              <p>覆盖全球的IP地址信息</p>
            </div>
          </div>
          <div class="feature">
            <div class="feature-icon">⚡</div>
            <div class="feature-text">
              <h3>快速查询</h3>
              <p>毫秒级响应速度</p>
            </div>
          </div>
          <div class="feature">
            <div class="feature-icon">📊</div>
            <div class="feature-text">
              <h3>详细分析</h3>
              <p>提供丰富的地理位置信息</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 忘记密码模态框 -->
    <div v-if="showForgotPassword" class="modal-overlay" @click="showForgotPassword = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>重置密码</h3>
          <button class="modal-close" @click="showForgotPassword = false">×</button>
        </div>
        <div class="modal-body">
          <p>请输入您的邮箱地址，我们将发送重置密码的链接。</p>
          <form @submit.prevent="handleForgotPassword">
            <div class="form-group">
              <label for="reset-email">邮箱地址</label>
              <input
                id="reset-email"
                v-model="resetEmail"
                type="email"
                placeholder="请输入邮箱地址"
                required
              />
            </div>
            <button type="submit" class="submit-btn" :disabled="isResetting">
              {{ isResetting ? '发送中...' : '发送重置链接' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginForm from '../components/auth/LoginForm.vue'
import RegisterForm from '../components/auth/RegisterForm.vue'

// 路由和状态
const router = useRouter()
const authStore = useAuthStore()

// 组件状态
const currentTab = ref<'login' | 'register'>('login')
const showForgotPassword = ref(false)
const resetEmail = ref('')
const isResetting = ref(false)

// 处理忘记密码
const handleForgotPassword = async () => {
  if (!resetEmail.value) return

  try {
    isResetting.value = true
    // 这里调用忘记密码API
    // await authService.requestPasswordReset({ email: resetEmail.value })
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    alert('重置密码链接已发送到您的邮箱')
    showForgotPassword.value = false
    resetEmail.value = ''
  } catch (error) {
    alert('发送失败，请稍后重试')
  } finally {
    isResetting.value = false
  }
}

// 检查是否已登录
onMounted(async () => {
  if (authStore.isAuthenticated) {
    router.push('/')
    return
  }
  
  // 尝试从本地存储恢复认证状态
  await authStore.initAuth()
  
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  position: relative;
  overflow: hidden;
}

.auth-container {
  width: 100%;
  max-width: 1200px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  position: relative;
  z-index: 2;
}

.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 100px;
  height: 100px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 20%;
  animation-delay: 2s;
}

.shape-3 {
  width: 80px;
  height: 80px;
  bottom: 20%;
  left: 60%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.auth-content {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid var(--glass-border);
  padding: 3rem;
  box-shadow: var(--shadow-xl);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.auth-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.auth-tabs {
  display: flex;
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 2rem;
}

.auth-tabs button {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.auth-tabs button.active {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow-md);
}

.auth-forms {
  margin-bottom: 2rem;
}

.auth-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-color);
}

.feature {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.feature:hover {
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  border-radius: 12px;
  color: white;
}

.feature-text h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.feature-text p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.modal-close:hover {
  background: var(--bg-secondary);
}

.modal-body p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .auth-content {
    padding: 2rem;
  }
  
  .auth-header h1 {
    font-size: 2rem;
  }
  
  .auth-features {
    grid-template-columns: 1fr;
  }
}
</style>
