<template>
  <div class="ip-lookup-container">
    <div class="container">
      <GlassContainer variant="card" class="page-header">
        <h1>IP查询</h1>
        <p>专业的IP地址查询工具，支持单个和批量查询</p>
      </GlassContainer>

      <!-- 查询表单 -->
      <GlassContainer variant="card" class="query-section">
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
          <button 
            class="tab-btn"
            :class="{ active: activeTab === 'history' }"
            @click="activeTab = 'history'"
          >
            查询历史
          </button>
        </div>

        <!-- 单个查询 -->
        <div v-if="activeTab === 'single'" class="single-query">
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
        </div>

        <!-- 批量查询 -->
        <div v-if="activeTab === 'batch'" class="batch-query">
          <textarea
            v-model="batchIps"
            class="input batch-textarea"
            placeholder="请输入多个IP地址，每行一个"
            rows="8"
          ></textarea>
          <div class="batch-actions">
            <button class="btn btn-secondary" @click="importFile">
              📁 导入文件
            </button>
            <button 
              class="btn btn-primary"
              @click="queryBatchIps"
              :disabled="loading || !batchIps.trim()"
            >
              {{ loading ? '批量查询中...' : '批量查询' }}
            </button>
          </div>
        </div>

        <!-- 查询历史 -->
        <div v-if="activeTab === 'history'" class="history-section">
          <div class="history-header">
            <h3>查询历史</h3>
            <button class="btn btn-secondary" @click="clearHistory">
              🗑️ 清空历史
            </button>
          </div>
          <div v-if="queryHistory.length === 0" class="empty-history">
            暂无查询历史
          </div>
          <div v-else class="history-list">
            <div
              v-for="(item, index) in queryHistory"
              :key="index"
              class="history-item"
              @click="loadHistoryItem(item)"
            >
              <div class="history-type">
                <span class="type-badge" :class="item.queryType || 'single'">
                  {{ (item.queryType === 'batch') ? '批量' : '单个' }}
                </span>
              </div>
              <div class="history-ip">{{ item.ip }}</div>
              <div class="history-info">{{ item.country }} {{ item.city }}</div>
              <div class="history-time">{{ formatTime(item.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="errorMessage" class="error-message">
          <div class="error-content">
            <span class="error-icon">!</span>
            <span class="error-text">{{ errorMessage }}</span>
            <button class="error-close" @click="errorMessage = ''">×</button>
          </div>
        </div>
      </GlassContainer>

      <!-- 查询结果 -->
      <div v-if="queryResults.length > 0" class="results-section">
        <GlassContainer variant="card">
          <div class="results-header">
            <h2>查询结果 ({{ queryResults.length }}条)</h2>
            <div class="results-actions">
              <button class="btn btn-secondary" @click="exportResults('csv')">
                导出CSV
              </button>
              <button class="btn btn-secondary" @click="exportResults('json')">
                导出JSON
              </button>
              <button class="btn btn-secondary" @click="clearResults">
                清空结果
              </button>
            </div>
          </div>
          
          <div class="results-table">
            <div class="table-header">
              <div>IP地址</div>
              <div>国家/地区</div>
              <div>城市</div>
              <div>ISP</div>
              <div>坐标</div>
            </div>
            <div 
              v-for="(result, index) in queryResults" 
              :key="index"
              class="table-row"
            >
              <div class="result-ip">{{ result.ip }}</div>
              <div>{{ result.country }} {{ result.region }}</div>
              <div>{{ result.city || '未知' }}</div>
              <div>{{ result.isp || '未知' }}</div>
              <div>{{ result.latitude }}, {{ result.longitude }}</div>
            </div>
          </div>
        </GlassContainer>
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
const queryResults = ref<any[]>([])
const queryHistory = ref<any[]>([])

// 单个IP查询
const querySingleIp = async () => {
  if (!singleIp.value.trim()) return

  loading.value = true
  errorMessage.value = ''
  try {
    const result = await ipService.queryIp(singleIp.value.trim())
    queryResults.value = [result]
    addToHistory(result, 'single')
  } catch (error) {
    console.error('查询失败:', error)
    errorMessage.value = (error as Error).message || '查询失败，请检查网络连接或稍后重试'
    queryResults.value = []
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

  if (ips.length === 0) return

  loading.value = true
  errorMessage.value = ''
  try {
    const results = await ipService.queryBatch(ips)
    queryResults.value = results
    results.forEach(result => addToHistory(result, 'batch'))
  } catch (error) {
    console.error('批量查询失败:', error)
    errorMessage.value = (error as Error).message || '批量查询失败，请检查网络连接或稍后重试'
    queryResults.value = []
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
        batchIps.value = ips.join('\n')
      } catch (error) {
        console.error('文件导入失败:', error)
        // TODO: 添加错误提示
      }
    }
  }
  input.click()
}

// 导出结果
const exportResults = (format: 'csv' | 'json') => {
  if (queryResults.value.length === 0) return
  
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
  const filename = `ip_query_results_${timestamp}.${format}`
  
  if (format === 'csv') {
    fileService.exportToCsv(queryResults.value, filename)
  } else {
    fileService.exportToJson(queryResults.value, filename)
  }
}

// 清空结果
const clearResults = () => {
  queryResults.value = []
}

// 添加到历史记录
const addToHistory = (result: any, queryType: 'single' | 'batch' = 'single') => {
  const historyItem = {
    ...result,
    timestamp: Date.now(),
    queryType
  }

  // 避免重复
  const existingIndex = queryHistory.value.findIndex(item => item.ip === result.ip)
  if (existingIndex >= 0) {
    queryHistory.value.splice(existingIndex, 1)
  }

  queryHistory.value.unshift(historyItem)

  // 限制历史记录数量
  if (queryHistory.value.length > 100) {
    queryHistory.value = queryHistory.value.slice(0, 100)
  }

  // 保存到localStorage
  localStorage.setItem('ipQueryHistory', JSON.stringify(queryHistory.value))
}

// 加载历史记录项
const loadHistoryItem = (item: any) => {
  singleIp.value = item.ip
  activeTab.value = 'single'
  queryResults.value = [item]
}

// 清空历史记录
const clearHistory = () => {
  queryHistory.value = []
  localStorage.removeItem('ipQueryHistory')
}

// 格式化时间
const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 加载历史记录
const loadHistory = () => {
  const saved = localStorage.getItem('ipQueryHistory')
  if (saved) {
    try {
      queryHistory.value = JSON.parse(saved)
    } catch (error) {
      console.error('加载历史记录失败:', error)
    }
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.ip-lookup-container {
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 1024px; /* 与导航栏保持一致 */
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.page-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.page-header p {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.query-section {
  margin-bottom: var(--space-xl);
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
}

.input-group .input {
  flex: 1;
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

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.empty-history {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-xl);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.history-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: var(--bg-card);
  transform: translateX(4px);
}

.history-type {
  display: flex;
  align-items: center;
}

.type-badge {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.type-badge.single {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.type-badge.batch {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.history-ip {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--primary-color);
  min-width: 120px;
}

.history-info {
  flex: 1;
  color: var(--text-primary);
}

.history-time {
  color: var(--text-muted);
  font-size: 0.9rem;
}

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

.results-table {
  overflow-x: auto;
}

.table-header {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 140px;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.table-row {
  display: grid;
  grid-template-columns: 140px 1fr 1fr 1fr 140px;
  gap: var(--space-md);
  padding: var(--space-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-sm);
  transition: all 0.3s ease;
}

.table-row:hover {
  background: var(--bg-secondary);
}

.result-ip {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--primary-color);
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

@media (max-width: 768px) {
  .input-group {
    flex-direction: column;
  }
  
  .batch-actions {
    flex-direction: column;
  }
  
  .results-header {
    flex-direction: column;
    gap: var(--space-md);
    align-items: flex-start;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: var(--space-sm);
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-sm);
  }

  .history-item .history-type {
    align-self: flex-end;
  }
}
</style>
