<template>
  <div class="home-container">
    <div class="container">
      <!-- 主标题区域 -->
      <div class="hero-section">
        <GlassContainer variant="card" class="hero-card">
          <h1 class="hero-title">🌐 IP查询工具</h1>
          <p class="hero-subtitle">快速、准确、专业的IP地址查询服务</p>
          
          <!-- 当前IP显示功能已移除以提升性能 -->
        </GlassContainer>
      </div>

      <!-- 快速查询区域 -->
      <div class="quick-query-section">
        <GlassContainer variant="card" class="query-card">
          <h2>🚀 快速查询</h2>
          
          <div class="query-tabs">
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'single' }"
              @click="activeTab = 'single'"
            >
              单个查询
            </button>
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'batch' }"
              @click="activeTab = 'batch'"
            >
              批量查询
            </button>
          </div>

          <!-- 单个查询 -->
          <div v-if="activeTab === 'single'" class="query-form">
            <div class="input-group">
              <input
                v-model="singleIp"
                type="text"
                class="input"
                placeholder="请输入IP地址，如：8.8.8.8"
                @keyup.enter="querySingleIp"
              />
              <button 
                class="btn btn-primary"
                @click="querySingleIp"
                :disabled="loading"
              >
                {{ loading ? '查询中...' : '查询' }}
              </button>
            </div>
            
            <!-- 示例IP -->
            <div class="example-ips">
              <span>示例：</span>
              <button 
                v-for="ip in exampleIps" 
                :key="ip"
                class="example-btn"
                @click="singleIp = ip"
              >
                {{ ip }}
              </button>
            </div>
          </div>

          <!-- 批量查询 -->
          <div v-if="activeTab === 'batch'" class="query-form">
            <div class="batch-input">
              <textarea
                v-model="batchIps"
                class="input batch-textarea"
                placeholder="请输入多个IP地址，每行一个&#10;8.8.8.8&#10;114.114.114.114&#10;1.1.1.1"
                rows="6"
              ></textarea>
              <div class="batch-actions">
                <button 
                  class="btn btn-secondary"
                  @click="importFile"
                >
                  📁 导入文件
                </button>
                <button 
                  class="btn btn-primary"
                  @click="queryBatchIps"
                  :disabled="loading || !batchIps.trim()"
                >
                  {{ loading ? '查询中...' : '批量查询' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 错误信息 -->
          <div v-if="errorMessage" class="error-message">
            <div class="error-content">
              <span class="error-icon">⚠️</span>
              <span class="error-text">{{ errorMessage }}</span>
              <button class="error-close" @click="errorMessage = ''">×</button>
            </div>
          </div>
        </GlassContainer>
      </div>

      <!-- 查询结果 -->
      <div v-if="queryResults.length > 0" class="results-section">
        <GlassContainer variant="card" class="results-card">
          <div class="results-header">
            <h2>📊 查询结果</h2>
            <div class="results-actions">
              <button class="btn btn-secondary" @click="exportResults">
                📤 导出结果
              </button>
              <button class="btn btn-secondary" @click="clearResults">
                🗑️ 清空结果
              </button>
            </div>
          </div>
          
          <div class="results-list">
            <div
              v-for="(result, index) in queryResults"
              :key="index"
              class="result-item"
            >
              <div class="result-ip">{{ result.ip }}</div>
              <div class="result-info">
                <div class="result-location">
                  🌍 {{ formatLocation(result) }}
                </div>
                <div class="result-isp">
                  🏢 {{ formatISP(result) }}
                </div>
                <div v-if="result.location && (result.location.latitude || result.location.longitude)" class="result-coordinates">
                  📍 {{ result.location.latitude }}, {{ result.location.longitude }}
                </div>
                <div v-if="result.location && result.location.timezone" class="result-timezone">
                  🕐 {{ result.location.timezone }}
                </div>
                <div v-if="result.query_time" class="result-time">
                  ⚡ 查询耗时: {{ (result.query_time * 1000).toFixed(2) }}ms
                </div>
              </div>
            </div>
          </div>
        </GlassContainer>
      </div>

      <!-- 功能特色 -->
      <div class="features-section">
        <div class="features-grid">
          <GlassContainer variant="card" class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>精准查询</h3>
            <p>基于MaxMind数据库，提供准确的IP地理位置信息</p>
          </GlassContainer>
          
          <GlassContainer variant="card" class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>批量处理</h3>
            <p>支持最多100个IP地址同时查询，提高工作效率</p>
          </GlassContainer>
          
          <GlassContainer variant="card" class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>数据导出</h3>
            <p>支持CSV、JSON、Excel多种格式导出查询结果</p>
          </GlassContainer>
          

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import GlassContainer from '../components/GlassContainer.vue'
import { ipService, fileService } from '../services/ipService'

// 响应式数据
const activeTab = ref('single')
const singleIp = ref('')
const batchIps = ref('')
const loading = ref(false)
const errorMessage = ref('')
const currentIp = ref<any>(null)
const queryResults = ref<any[]>([])

// 示例IP地址
const exampleIps = ['8.8.8.8', '114.114.114.114', '1.1.1.1', '208.67.222.222']

// 单个IP查询
const querySingleIp = async () => {
  if (!singleIp.value.trim()) return

  loading.value = true
  try {
    const result = await ipService.queryIp(singleIp.value.trim())
    queryResults.value = [result]
    console.log('查询结果:', result)
    console.log('格式化位置:', formatLocation(result))
    console.log('格式化ISP:', formatISP(result))
  } catch (error) {
    console.error('查询失败:', error)
    // 显示错误提示给用户
    alert('查询失败，请检查IP地址格式或网络连接')
  } finally {
    loading.value = false
  }
}

// 批量IP查询
const queryBatchIps = async () => {
  const ips = batchIps.value
    .split('\n')
    .map(ip => ip.trim())
    .filter(ip => ip && fileService.isValidIp(ip))

  if (ips.length === 0) {
    errorMessage.value = '请输入有效的IP地址'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    const results = await ipService.queryBatch(ips)
    queryResults.value = results
    console.log('批量查询结果:', results)
  } catch (error) {
    console.error('批量查询失败:', error)
    errorMessage.value = (error as Error).message || '批量查询失败，请检查网络连接或稍后重试'
  } finally {
    loading.value = false
  }
}

// 导入文件
const importFile = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.txt,.csv'
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      try {
        const content = await fileService.readFile(file)
        const ips = fileService.parseIpList(content)

        if (ips.length === 0) {
          errorMessage.value = '文件中没有找到有效的IP地址'
          return
        }

        if (ips.length > 100) {
          errorMessage.value = `文件包含${ips.length}个IP地址，已截取前100个`
          ips.splice(100)
        }

        batchIps.value = ips.join('\n')
        errorMessage.value = ''
        console.log(`成功导入${ips.length}个IP地址`)
      } catch (error) {
        console.error('文件导入失败:', error)
        errorMessage.value = '文件导入失败，请检查文件格式'
      }
    }
  }
  input.click()
}

// 导出结果
const exportResults = () => {
  // TODO: 实现结果导出功能
  console.log('导出结果功能待实现')
}

// 清空结果
const clearResults = () => {
  queryResults.value = []
}

// 获取当前IP (暂时禁用)
// const getCurrentIp = async () => {
//   try {
//     // 暂时注释掉，避免启动时的网络请求错误
//     console.log('获取当前IP功能待实现')
//   } catch (error) {
//     console.error('获取当前IP失败:', error)
//   }
// }

// 格式化地理位置信息
const formatLocation = (result: any) => {
  const parts = []

  // 检查location对象是否存在
  if (result.location && typeof result.location === 'object') {
    const location = result.location

    if (location.country && location.country !== 'null' && location.country !== null) {
      parts.push(location.country)
    }
    if (location.region && location.region !== 'null' && location.region !== null) {
      parts.push(location.region)
    }
    if (location.city && location.city !== 'null' && location.city !== null) {
      parts.push(location.city)
    }
  }

  return parts.length > 0 ? parts.join(', ') : '未知位置'
}

// 格式化ISP信息
const formatISP = (result: any) => {
  // 检查ISP对象的各个字段
  if (result.isp && typeof result.isp === 'object') {
    const isp = result.isp
    const ispParts = []

    // 优先显示ISP名称
    if (isp.isp && isp.isp !== 'null' && isp.isp !== null) {
      ispParts.push(`ISP: ${isp.isp}`)
    }

    // 其次显示组织名称
    if (isp.organization && isp.organization !== 'null' && isp.organization !== null) {
      ispParts.push(`组织: ${isp.organization}`)
    }

    // 再次显示ASN组织
    if (isp.asn_organization && isp.asn_organization !== 'null' && isp.asn_organization !== null) {
      ispParts.push(`ASN组织: ${isp.asn_organization}`)
    }

    // 最后显示ASN号码
    if (isp.asn && isp.asn !== 'null' && isp.asn !== null) {
      ispParts.push(`ASN: ${isp.asn}`)
    }

    // 如果有任何ISP信息，返回组合结果
    if (ispParts.length > 0) {
      return ispParts.join(' | ')
    }
  }

  // 如果ISP是字符串
  if (typeof result.isp === 'string' && result.isp && result.isp !== 'null') {
    return result.isp
  }

  return '未知ISP'
}

onMounted(() => {
  // getCurrentIp() // 暂时注释掉
})
</script>

<style scoped>
.home-container {
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 1024px; /* 与导航栏保持一致 */
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

/* 主标题区域 */
.hero-section {
  text-align: center;
  margin-bottom: var(--space-2xl);
}

.hero-card {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.hero-subtitle {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-bottom: var(--space-xl);
}

.current-ip {
  margin-top: var(--space-xl);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--border-color);
}

.current-ip h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.ip-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.ip-address {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
  font-family: 'JetBrains Mono', monospace;
}

.ip-location {
  color: var(--text-secondary);
}

/* 查询区域 */
.query-card {
  margin-bottom: var(--space-2xl);
}

.query-tabs {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.tab-btn {
  padding: var(--space-sm) var(--space-lg);
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.input-group {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.input-group .input {
  flex: 1;
}

.example-ips {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

.example-btn {
  padding: var(--space-xs) var(--space-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
}

.example-btn:hover {
  background: var(--primary-color);
  color: white;
}

.batch-textarea {
  width: 100%;
  resize: vertical;
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: var(--space-md);
}

.batch-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: flex-end;
}

/* 结果区域 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.results-actions {
  display: flex;
  gap: var(--space-sm);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.result-item {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.result-ip {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--primary-color);
  min-width: 120px;
}

.result-info {
  flex: 1;
}

.result-location {
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.result-isp {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: var(--space-xs);
}

.result-coordinates {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: var(--space-xs);
}

.result-timezone {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: var(--space-xs);
}

.result-time {
  color: var(--success-color);
  font-size: 0.8rem;
  font-weight: 500;
}

/* 功能特色 */
.features-section {
  margin-top: var(--space-2xl);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-lg);
}

.feature-card {
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: var(--space-md);
}

.feature-card h3 {
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 错误信息样式 */
.error-message {
  margin-top: var(--space-md);
  animation: slideDown 0.3s ease;
}

.error-content {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: var(--radius-md);
  color: #ff6b6b;
}

.error-icon {
  font-size: 1.2em;
}

.error-text {
  flex: 1;
  font-weight: 500;
}

.error-close {
  background: none;
  border: none;
  color: #ff6b6b;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.error-close:hover {
  background: rgba(255, 107, 107, 0.2);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }
  
  .results-header {
    flex-direction: column;
    gap: var(--space-md);
    align-items: flex-start;
  }
  
  .batch-actions {
    flex-direction: column;
  }
}
</style>
