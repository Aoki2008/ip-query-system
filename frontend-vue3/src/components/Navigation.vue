<template>
  <nav class="nav-container">
    <div class="container">
      <div class="logo-container">
        <div class="logo">
          <AppLogo size="normal" />
        </div>
        <div class="site-title">
          <h1>IP查询工具</h1>
        </div>
      </div>

      <!-- 移动端汉堡菜单按钮 -->
      <button
        class="mobile-menu-toggle"
        @click="toggleMobileMenu"
        :class="{ active: mobileMenuOpen }"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <ul class="nav-list" :class="{ 'mobile-open': mobileMenuOpen }">
        <li class="nav-item">
          <router-link to="/" class="nav-link" @click="closeMobileMenu">
            首页
          </router-link>
        </li>
        
        <li class="nav-item dropdown" :class="{ open: toolsDropdownOpen }">
          <a
            href="#"
            class="nav-link dropdown-toggle"
            @click.prevent="toggleToolsDropdown"
          >
            工具箱 <span class="dropdown-arrow">▼</span>
          </a>
          <ul class="dropdown-menu">
            <li>
              <router-link
                to="/ip-lookup"
                class="nav-link"
                @click="closeMobileMenu"
              >
                IP查询
              </router-link>
            </li>
          </ul>
        </li>
        
        <li class="nav-item dropdown" :class="{ open: helpDropdownOpen }">
          <a
            href="#"
            class="nav-link dropdown-toggle"
            @click.prevent="toggleHelpDropdown"
          >
            使用帮助 <span class="dropdown-arrow">▼</span>
          </a>
          <ul class="dropdown-menu">
            <li>
              <router-link
                to="/guide"
                class="nav-link"
                @click="closeMobileMenu"
              >
                使用指南
              </router-link>
            </li>
            <li>
              <router-link
                to="/faq"
                class="nav-link"
                @click="closeMobileMenu"
              >
                常见问题
              </router-link>
            </li>
          </ul>
        </li>
        
        <li class="nav-item">
          <router-link
            to="/about"
            class="nav-link"
            @click="closeMobileMenu"
          >
            关于我们
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppLogo from './AppLogo.vue'

// 下拉菜单状态
const toolsDropdownOpen = ref(false)
const helpDropdownOpen = ref(false)
const mobileMenuOpen = ref(false)

// 下拉菜单控制方法
const toggleToolsDropdown = () => {
  helpDropdownOpen.value = false
  toolsDropdownOpen.value = !toolsDropdownOpen.value
}

const toggleHelpDropdown = () => {
  toolsDropdownOpen.value = false
  helpDropdownOpen.value = !helpDropdownOpen.value
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
  // 关闭所有下拉菜单
  toolsDropdownOpen.value = false
  helpDropdownOpen.value = false
}

const closeAllDropdowns = () => {
  toolsDropdownOpen.value = false
  helpDropdownOpen.value = false
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
  closeAllDropdowns()
}
</script>

<style scoped>
.container {
  max-width: 1024px; /* 优化为更合理的宽度，参考主流网站 */
  margin: 0 auto;
  padding: 0 var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.logo-icon {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: var(--radius-md);
}

.site-title h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 汉堡菜单按钮 */
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
  z-index: 1001;
}

.mobile-menu-toggle span {
  width: 25px;
  height: 3px;
  background: var(--text-primary);
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.mobile-menu-toggle.active span:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.mobile-menu-toggle.active span:nth-child(2) {
  opacity: 0;
}

.mobile-menu-toggle.active span:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

@media (max-width: 768px) {
  .container {
    position: relative;
    /* 保持水平布局 */
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-md);
  }

  .logo-container {
    /* 确保logo在左边 */
    flex: 0 0 auto;
  }

  .site-title h1 {
    font-size: 1.2rem;
  }

  /* 显示汉堡菜单按钮 */
  .mobile-menu-toggle {
    display: flex;
  }

  /* 隐藏桌面端导航菜单 */
  .nav-list {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    z-index: 1000;
    flex-direction: column;
    padding: var(--space-md);
    margin-top: var(--space-sm);
  }

  /* 显示移动端菜单 */
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
  }

  .nav-link:hover {
    background: var(--bg-secondary);
  }

  /* 下拉菜单在移动端的样式 */
  .dropdown-menu {
    position: static;
    display: none;
    background: var(--bg-secondary);
    border: none;
    box-shadow: none;
    margin-top: var(--space-sm);
    border-radius: var(--radius-sm);
  }

  .dropdown.open .dropdown-menu {
    display: block;
  }

  .dropdown-menu .nav-link {
    padding: var(--space-sm) var(--space-md);
    font-size: 0.9rem;
    margin-left: 0;
    border: none;
  }
}
</style>
