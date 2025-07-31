<template>
  <nav class="nav-container">
    <div class="container">
      <div class="logo-container">
        <div class="logo">
          <div class="logo-icon">🌐</div>
        </div>
        <div class="site-title">
          <h1>IP查询工具</h1>
        </div>
      </div>

      <!-- 移动端汉堡菜单按钮 -->
      <button
        class="mobile-menu-toggle"
        @click="toggleMobileMenu"
        :class="{ 'active': mobileMenuOpen }"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <div class="nav-content">
        <ul class="nav-list" :class="{ 'mobile-open': mobileMenuOpen }">
          <li class="nav-item">
            <router-link to="/" class="nav-link" @click="closeMobileMenu">
              🏠 首页
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/lookup" class="nav-link" @click="closeMobileMenu">
              🔍 IP查询
            </router-link>
          </li>

          <!-- 工具下拉菜单 -->
          <li class="nav-item dropdown" :class="{ 'open': toolsDropdownOpen }">
            <button
              class="nav-link dropdown-toggle"
              @click="toggleToolsDropdown"
            >
              🛠️ 工具 <span class="dropdown-arrow">▼</span>
            </button>
            <ul class="dropdown-menu">
              <li>
                <router-link to="/guide" class="nav-link" @click="closeMobileMenu">
                  📖 使用指南
                </router-link>
              </li>
              <li>
                <router-link to="/lookup" class="nav-link" @click="closeMobileMenu">
                  🔍 高级查询
                </router-link>
              </li>
            </ul>
          </li>

          <!-- 帮助下拉菜单 -->
          <li class="nav-item dropdown" :class="{ 'open': helpDropdownOpen }">
            <button
              class="nav-link dropdown-toggle"
              @click="toggleHelpDropdown"
            >
              ❓ 帮助 <span class="dropdown-arrow">▼</span>
            </button>
            <ul class="dropdown-menu">
              <li>
                <router-link to="/faq" class="nav-link" @click="closeMobileMenu">
                  ❓ 常见问题
                </router-link>
              </li>
              <li>
                <router-link to="/about" class="nav-link" @click="closeMobileMenu">
                  ℹ️ 关于我们
                </router-link>
              </li>
            </ul>
          </li>
        </ul>

        <div class="nav-actions">
          <UserMenu />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import UserMenu from './user/UserMenu.vue'

// 下拉菜单状态
const toolsDropdownOpen = ref(false)
const helpDropdownOpen = ref(false)
const mobileMenuOpen = ref(false)

// 切换工具下拉菜单
const toggleToolsDropdown = () => {
  toolsDropdownOpen.value = !toolsDropdownOpen.value
  helpDropdownOpen.value = false // 关闭其他下拉菜单
}

// 切换帮助下拉菜单
const toggleHelpDropdown = () => {
  helpDropdownOpen.value = !helpDropdownOpen.value
  toolsDropdownOpen.value = false // 关闭其他下拉菜单
}

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
  // 关闭所有下拉菜单
  toolsDropdownOpen.value = false
  helpDropdownOpen.value = false
}

// 关闭所有下拉菜单
const closeAllDropdowns = () => {
  toolsDropdownOpen.value = false
  helpDropdownOpen.value = false
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  mobileMenuOpen.value = false
  closeAllDropdowns()
}

// 点击外部关闭下拉菜单
const handleClickOutside = (e: Event) => {
  const target = e.target as HTMLElement

  // 如果点击的是表单元素，不要干扰
  if (target.closest('form') || target.closest('.auth-page') || target.closest('.auth-content')) {
    return
  }

  // 只在导航栏区域外的点击才关闭下拉菜单
  if (!target.closest('.nav-container')) {
    closeAllDropdowns()
  }
}

// 在组件挂载时添加事件监听器
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

// 在组件卸载时移除事件监听器
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.nav-container {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--glass-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  position: relative;
  gap: var(--space-lg);
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  flex: 1;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
}

.site-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.nav-list {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: var(--space-lg);
}

.nav-item {
  position: relative;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: var(--space-sm) var(--space-md);
  color: var(--text-primary);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.nav-link:hover {
  background: var(--bg-secondary);
  transform: translateY(-1px);
}

.nav-link.router-link-active {
  background: var(--primary-color);
  color: white;
}

/* 移动端汉堡菜单按钮 */
.mobile-menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 30px;
  height: 30px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 10;
}

.mobile-menu-toggle span {
  width: 100%;
  height: 3px;
  background: var(--text-primary);
  border-radius: 10px;
  transition: all 0.3s linear;
  position: relative;
  transform-origin: 1px;
}

.mobile-menu-toggle.active span:first-child {
  transform: rotate(45deg);
}

.mobile-menu-toggle.active span:nth-child(2) {
  opacity: 0;
  transform: translateX(20px);
}

.mobile-menu-toggle.active span:nth-child(3) {
  transform: rotate(-45deg);
}

/* 下拉菜单样式 */
.dropdown {
  position: relative;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-arrow {
  font-size: 0.8rem;
  transition: transform 0.3s ease;
}

.dropdown.open .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  min-width: 160px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 1002;
  margin-top: var(--space-xs);
  list-style: none;
  padding: var(--space-sm);
}

.dropdown.open .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-menu li {
  margin: 0;
}

.dropdown-menu .nav-link {
  padding: var(--space-sm) var(--space-md);
  margin: 0;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: flex;
  }

  .nav-content {
    position: relative;
  }

  .nav-list {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    flex-direction: column;
    padding: var(--space-md);
    margin-top: var(--space-sm);
    box-shadow: var(--shadow-lg);
    z-index: 1000;
  }

  .nav-list.mobile-open {
    display: flex;
  }

  .nav-item {
    width: 100%;
    margin: 0;
  }

  .nav-link {
    display: block;
    padding: var(--space-md);
    border-radius: var(--radius-sm);
    transition: background-color 0.2s ease;
    width: 100%;
    text-align: left;
    justify-content: flex-start;
  }

  .nav-link:hover {
    background: var(--bg-secondary);
    transform: none;
  }

  .container {
    padding: 0 var(--space-md);
  }

  /* 移动端下拉菜单 */
  .dropdown-menu {
    position: static;
    opacity: 1;
    visibility: visible;
    transform: none;
    box-shadow: none;
    border: none;
    background: transparent;
    margin-top: 0;
    margin-left: var(--space-md);
    display: none;
  }

  .dropdown.open .dropdown-menu {
    display: block;
  }

  .dropdown-menu .nav-link {
    padding: var(--space-sm) var(--space-md);
    margin-left: 0;
    border-left: 2px solid var(--border-color);
    font-size: 0.9rem;
  }

  /* 隐藏桌面端导航 */
  .nav-list:not(.mobile-open) {
    display: none;
  }
}
</style>
