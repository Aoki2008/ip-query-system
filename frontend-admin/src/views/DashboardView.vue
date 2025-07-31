<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>仪表板</h1>
      <p>欢迎使用IP查询工具管理后台</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon system">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <h3>系统状态</h3>
              <p class="stat-value">正常运行</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>管理员用户</h3>
              <p class="stat-value">{{ stats.adminUsers }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon permissions">
              <el-icon><Lock /></el-icon>
            </div>
            <div class="stat-info">
              <h3>系统权限</h3>
              <p class="stat-value">{{ stats.permissions }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon roles">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <h3>系统角色</h3>
              <p class="stat-value">{{ stats.roles }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card>
          <template #header>
            <h3>快捷操作</h3>
          </template>
          
          <div class="action-buttons">
            <el-button type="primary" @click="$router.push('/permissions')">
              <el-icon><Lock /></el-icon>
              权限管理
            </el-button>
            
            <el-button type="success" @click="$router.push('/users')">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            
            <el-button type="warning" @click="$router.push('/system')">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-button>
            
            <el-button type="info" @click="checkSystemHealth">
              <el-icon><Monitor /></el-icon>
              系统检查
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="12" :lg="12">
        <el-card>
          <template #header>
            <h3>系统信息</h3>
          </template>
          
          <div class="system-info">
            <div class="info-item">
              <span class="label">服务状态：</span>
              <el-tag :type="systemHealth.status === 'healthy' ? 'success' : 'danger'">
                {{ systemHealth.status === 'healthy' ? '正常' : '异常' }}
              </el-tag>
            </div>
            
            <div class="info-item">
              <span class="label">服务类型：</span>
              <span>{{ systemHealth.service_type || 'FastAPI' }}</span>
            </div>
            
            <div class="info-item">
              <span class="label">当前用户：</span>
              <span>{{ authStore.user?.username }}</span>
            </div>
            
            <div class="info-item">
              <span class="label">用户角色：</span>
              <el-tag type="primary">{{ authStore.user?.role }}</el-tag>
            </div>
            
            <div class="info-item">
              <span class="label">最后登录：</span>
              <span>{{ formatDate(authStore.user?.last_login) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Monitor, User, DataLine, Setting, Lock, UserFilled } from '@element-plus/icons-vue'
import api from '@/utils/api'

const authStore = useAuthStore()

const stats = ref({
  adminUsers: 1,
  permissions: 27,
  roles: 3
})

const systemHealth = ref({
  status: 'healthy',
  service_type: 'FastAPI',
  message: '服务运行正常'
})

const checkSystemHealth = async () => {
  try {
    const response = await api.get('/health')
    systemHealth.value = response.data
    ElMessage.success('系统状态检查完成')
  } catch (error) {
    ElMessage.error('系统状态检查失败')
  }
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(async () => {
  await checkSystemHealth()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #303133;
  margin-bottom: 8px;
}

.page-header p {
  color: #909399;
  margin: 0;
}

.stats-row {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
}

.stat-icon.system {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.users {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.permissions {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.roles {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info h3 {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
  font-weight: normal;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.quick-actions {
  margin-bottom: 30px;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.action-buttons .el-button {
  height: 50px;
  font-size: 14px;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.label {
  color: #606266;
  font-weight: 500;
}
</style>
