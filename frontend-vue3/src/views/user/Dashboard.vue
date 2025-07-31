<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>用户仪表板</h1>
      <p>欢迎回来，{{ authStore.user?.username }}！</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3>总查询数</h3>
          <p class="stat-number">{{ stats.totalQueries }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-content">
          <h3>今日查询</h3>
          <p class="stat-number">{{ stats.todayQueries }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <h3>本月查询</h3>
          <p class="stat-number">{{ stats.monthQueries }}</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <h3>成功率</h3>
          <p class="stat-number">{{ stats.successRate }}%</p>
        </div>
      </div>
    </div>

    <!-- 最近查询 -->
    <div class="recent-queries">
      <h2>最近查询</h2>
      <div class="query-list">
        <div v-if="recentQueries.length === 0" class="empty-state">
          <p>暂无查询记录</p>
          <router-link to="/" class="start-query-btn">
            开始查询
          </router-link>
        </div>
        
        <div v-else class="query-item" v-for="query in recentQueries" :key="query.id">
          <div class="query-ip">{{ query.ip }}</div>
          <div class="query-location">{{ query.location }}</div>
          <div class="query-time">{{ formatTime(query.time) }}</div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <h2>快捷操作</h2>
      <div class="action-grid">
        <router-link to="/" class="action-card">
          <div class="action-icon">🔍</div>
          <h3>IP查询</h3>
          <p>查询IP地址信息</p>
        </router-link>
        
        <router-link to="/user/history" class="action-card">
          <div class="action-icon">📝</div>
          <h3>查询历史</h3>
          <p>查看历史记录</p>
        </router-link>
        
        <router-link to="/user/settings" class="action-card">
          <div class="action-icon">⚙️</div>
          <h3>账户设置</h3>
          <p>管理个人设置</p>
        </router-link>
        
        <router-link v-if="authStore.isPremium" to="/user/api-keys" class="action-card premium">
          <div class="action-icon">🔑</div>
          <h3>API密钥</h3>
          <p>管理API访问</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

// 认证状态
const authStore = useAuthStore()

// 统计数据
const stats = ref({
  totalQueries: 0,
  todayQueries: 0,
  monthQueries: 0,
  successRate: 0
})

// 最近查询
const recentQueries = ref<Array<{
  id: string
  ip: string
  location: string
  time: Date
}>>([])

// 格式化时间
const formatTime = (time: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(time)
}

// 加载用户数据
const loadUserData = async () => {
  try {
    // 这里可以调用API获取用户统计数据
    // 暂时使用模拟数据
    stats.value = {
      totalQueries: 156,
      todayQueries: 12,
      monthQueries: 89,
      successRate: 98.5
    }
    
    // 模拟最近查询数据
    recentQueries.value = [
      {
        id: '1',
        ip: '8.8.8.8',
        location: '美国 加利福尼亚州',
        time: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
      },
      {
        id: '2',
        ip: '114.114.114.114',
        location: '中国 北京市',
        time: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
      },
      {
        id: '3',
        ip: '1.1.1.1',
        location: '美国 加利福尼亚州',
        time: new Date(Date.now() - 1000 * 60 * 60 * 5) // 5小时前
      }
    ]
  } catch (error) {
    console.error('加载用户数据失败:', error)
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 120px);
}

.dashboard-header {
  text-align: center;
  margin-bottom: 3rem;
}

.dashboard-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.dashboard-header p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  border-radius: 12px;
  color: white;
}

.stat-content h3 {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.recent-queries,
.quick-actions {
  margin-bottom: 3rem;
}

.recent-queries h2,
.quick-actions h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
}

.query-list {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.start-query-btn {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: background 0.3s ease;
}

.start-query-btn:hover {
  background: var(--primary-hover);
}

.query-item {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.3s ease;
}

.query-item:last-child {
  border-bottom: none;
}

.query-item:hover {
  background: var(--bg-secondary);
}

.query-ip {
  font-family: monospace;
  font-weight: 600;
  color: var(--text-primary);
}

.query-location {
  color: var(--text-secondary);
}

.query-time {
  color: var(--text-secondary);
  font-size: 0.9rem;
  text-align: right;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.3s ease;
  text-align: center;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.action-card.premium {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border: none;
}

.action-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.action-card p {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .query-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .query-time {
    text-align: left;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
