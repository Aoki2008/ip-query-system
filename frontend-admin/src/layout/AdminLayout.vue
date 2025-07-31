<template>
  <el-container class="admin-layout">
    <!-- 移动端遮罩层 -->
    <div
      class="mobile-overlay"
      :class="{ show: isMobile && showMobileSidebar }"
      @click="hideMobileSidebar"
    ></div>

    <!-- 侧边栏 -->
    <el-aside
      :width="getSidebarWidth"
      class="sidebar"
      :class="{ 'mobile-show': isMobile && showMobileSidebar }"
    >
      <div class="logo">
        <h2 v-if="!isCollapse || isMobile">管理后台</h2>
        <h2 v-else>管</h2>
      </div>

      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse && !isMobile"
        :unique-opened="true"
        router
        class="sidebar-menu"
        @select="onMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>仪表板</template>
        </el-menu-item>

        <el-menu-item index="/permissions">
          <el-icon><Lock /></el-icon>
          <template #title>权限管理</template>
        </el-menu-item>

        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>

        <el-menu-item index="/system">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>

        <el-menu-item index="/seo">
          <el-icon><Search /></el-icon>
          <template #title>SEO设置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-button
            type="text"
            @click="toggleCollapse"
            class="collapse-btn"
          >
            <el-icon><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ authStore.user?.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Lock,
  User,
  Setting,
  Search,
  Monitor,
  Fold,
  Expand,
  SwitchButton,
  ArrowDown
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)
const isMobile = ref(false)
const showMobileSidebar = ref(false)

const currentPageTitle = computed(() => {
  return route.meta.title as string || '未知页面'
})

const getSidebarWidth = computed(() => {
  if (isMobile.value) {
    return '200px'
  }
  return isCollapse.value ? '64px' : '200px'
})

// 检查是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    showMobileSidebar.value = false
  }
}

// 切换侧边栏
const toggleCollapse = () => {
  if (isMobile.value) {
    showMobileSidebar.value = !showMobileSidebar.value
  } else {
    isCollapse.value = !isCollapse.value
  }
}

// 隐藏移动端侧边栏
const hideMobileSidebar = () => {
  if (isMobile.value) {
    showMobileSidebar.value = false
  }
}

// 菜单选择事件
const onMenuSelect = () => {
  if (isMobile.value) {
    showMobileSidebar.value = false
  }
}

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人信息功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch (error) {
        // 用户取消
      }
      break
  }
}

onMounted(async () => {
  // 获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.getProfile()
  }

  // 初始化移动端检查
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  position: relative;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: none;
  transition: opacity 0.3s ease;
}

.mobile-overlay.show {
  display: block;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s, transform 0.3s;
  position: relative;
  z-index: 1000;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4b;
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.sidebar-menu {
  border: none;
  background-color: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background-color: #263445;
  color: #409eff;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  font-size: 18px;
  border: none;
  background: none;
  color: #606266;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.collapse-btn:hover {
  background-color: #f5f7fa;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
  color: #606266;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  min-height: calc(100vh - 60px);
}

/* 移动端样式 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    transform: translateX(-100%);
    width: 200px !important;
  }

  .sidebar.mobile-show {
    transform: translateX(0);
  }

  .header {
    padding: 0 15px;
    height: 50px;
  }

  .header-left {
    gap: 10px;
  }

  .collapse-btn {
    font-size: 20px;
  }

  .main-content {
    padding: 10px;
    min-height: calc(100vh - 50px);
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 10px;
  }

  .main-content {
    padding: 8px;
  }

  .user-info {
    font-size: 14px;
    padding: 6px 8px;
  }
}
</style>
