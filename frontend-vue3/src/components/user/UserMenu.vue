<template>
  <div class="user-menu" v-if="authStore.isAuthenticated">
    <!-- 用户头像和信息 -->
    <div class="user-info" @click="toggleDropdown">
      <div class="user-avatar">
        <img 
          v-if="authStore.user?.avatar_url" 
          :src="authStore.user.avatar_url" 
          :alt="authStore.user.username"
        />
        <div v-else class="avatar-placeholder">
          {{ getInitials(authStore.user?.username || '') }}
        </div>
      </div>
      <div class="user-details">
        <span class="username">{{ authStore.user?.username }}</span>
        <span class="user-type" :class="{ premium: authStore.isPremium }">
          {{ authStore.isPremium ? '高级用户' : '普通用户' }}
        </span>
      </div>
      <div class="dropdown-arrow" :class="{ open: showDropdown }">
        ▼
      </div>
    </div>

    <!-- 下拉菜单 -->
    <Transition name="dropdown">
      <div v-if="showDropdown" class="dropdown-menu">
        <div class="menu-section">
          <h4>账户管理</h4>
          <router-link to="/user/dashboard" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">📊</span>
            <span>用户仪表板</span>
          </router-link>
          <router-link to="/user/profile" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">👤</span>
            <span>个人资料</span>
          </router-link>
          <router-link to="/user/settings" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">⚙️</span>
            <span>账户设置</span>
          </router-link>
        </div>

        <div class="menu-section">
          <h4>查询管理</h4>
          <router-link to="/user/history" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">📝</span>
            <span>查询历史</span>
          </router-link>
          <router-link to="/user/favorites" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">⭐</span>
            <span>收藏夹</span>
          </router-link>
        </div>

        <div class="menu-section" v-if="authStore.isPremium">
          <h4>高级功能</h4>
          <router-link to="/user/api-keys" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">🔑</span>
            <span>API密钥</span>
          </router-link>
          <router-link to="/user/exports" class="menu-item" @click="closeDropdown">
            <span class="menu-icon">📤</span>
            <span>数据导出</span>
          </router-link>
        </div>

        <div class="menu-divider"></div>

        <div class="menu-section">
          <button class="menu-item logout-btn" @click="handleLogout">
            <span class="menu-icon">🚪</span>
            <span>退出登录</span>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 点击外部关闭下拉菜单 -->
    <div v-if="showDropdown" class="dropdown-overlay" @click="closeDropdown"></div>
  </div>

  <!-- 未登录状态 -->
  <div v-else class="auth-buttons">
    <router-link to="/auth" class="auth-btn login-btn">
      登录
    </router-link>
    <router-link to="/auth" class="auth-btn register-btn">
      注册
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

// 路由和状态
const router = useRouter()
const authStore = useAuthStore()

// 组件状态
const showDropdown = ref(false)

// 获取用户名首字母
const getInitials = (username: string): string => {
  return username.slice(0, 2).toUpperCase()
}

// 切换下拉菜单
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

// 关闭下拉菜单
const closeDropdown = () => {
  showDropdown.value = false
}

// 处理登出
const handleLogout = async () => {
  try {
    await authStore.logout()
    closeDropdown()
    router.push('/')
  } catch (error) {
    console.error('登出失败:', error)
  }
}

// 键盘事件处理
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    closeDropdown()
  }
}

// 组件挂载和卸载
onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.user-menu {
  position: relative;
  display: inline-block;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.user-info:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.username {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.user-type {
  font-size: 0.75rem;
  color: var(--text-secondary);
  padding: 0.125rem 0.5rem;
  background: var(--bg-secondary);
  border-radius: 6px;
}

.user-type.premium {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
}

.dropdown-arrow {
  font-size: 0.7rem;
  color: var(--text-secondary);
  transition: transform 0.3s ease;
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 250px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: var(--shadow-xl);
  z-index: 1000;
  overflow: hidden;
}

.menu-section {
  padding: 1rem;
}

.menu-section h4 {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.75rem 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  margin-bottom: 0.25rem;
  border: none;
  background: none;
  width: 100%;
  cursor: pointer;
  font-size: 0.9rem;
}

.menu-item:hover {
  background: var(--bg-secondary);
  transform: translateX(4px);
}

.menu-item.router-link-active {
  background: var(--primary-color);
  color: white;
}

.menu-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.menu-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0.5rem 0;
}

.logout-btn {
  color: var(--error-color);
}

.logout-btn:hover {
  background: var(--error-bg);
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

/* 未登录状态 */
.auth-buttons {
  display: flex;
  gap: 0.75rem;
}

.auth-btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.login-btn {
  color: var(--text-primary);
  background: var(--glass-bg);
  border-color: var(--glass-border);
  backdrop-filter: blur(10px);
}

.login-btn:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
}

.register-btn {
  color: white;
  background: var(--primary-color);
}

.register-btn:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
  transform-origin: top right;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-info {
    padding: 0.5rem;
  }
  
  .user-details {
    display: none;
  }
  
  .dropdown-menu {
    right: -1rem;
    min-width: 200px;
  }
  
  .auth-buttons {
    gap: 0.5rem;
  }
  
  .auth-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
}
</style>
