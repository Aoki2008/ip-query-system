<template>
  <div class="batch-results-container">
    <!-- 结果统计和操作栏 -->
    <div class="results-header">
      <div class="results-stats">
        <span class="stats-item">
          <strong>{{ results.length }}</strong> 条结果
        </span>
        <span class="stats-item" v-if="successCount > 0">
          <span class="success-badge">{{ successCount }}</span> 成功
        </span>
        <span class="stats-item" v-if="errorCount > 0">
          <span class="error-badge">{{ errorCount }}</span> 失败
        </span>
      </div>
      
      <div class="results-actions">
        <!-- 排序选择 -->
        <div class="sort-controls">
          <label for="sortBy">排序：</label>
          <select id="sortBy" v-model="sortBy" @change="applySorting" class="sort-select">
            <option value="index">查询顺序</option>
            <option value="ip">IP地址</option>
            <option value="country">国家</option>
            <option value="city">城市</option>
            <option value="isp">ISP</option>
            <option value="queryTime">查询时间</option>
          </select>
          <button @click="toggleSortOrder" class="sort-order-btn" :title="sortOrder === 'asc' ? '升序' : '降序'">
            {{ sortOrder === 'asc' ? '↑' : '↓' }}
          </button>
        </div>
        
        <!-- 筛选控制 -->
        <div class="filter-controls">
          <input 
            v-model="filterText" 
            @input="applyFilters"
            placeholder="筛选结果..." 
            class="filter-input"
          />
          <button @click="clearFilters" class="clear-filter-btn" v-if="filterText">
            ✕
          </button>
        </div>
        
        <!-- 导出按钮 -->
        <div class="export-controls">
          <button @click="exportResults('csv')" class="export-btn">
            📊 CSV
          </button>
          <button @click="exportResults('json')" class="export-btn">
            📄 JSON
          </button>
          <button @click="exportResults('excel')" class="export-btn">
            📈 Excel
          </button>
        </div>
      </div>
    </div>
    
    <!-- 结果表格 -->
    <div class="table-container">
      <div class="table-wrapper">
        <table class="results-table">
          <thead>
            <tr>
              <th class="col-index">#</th>
              <th class="col-ip" @click="setSortBy('ip')">
                IP地址 <span class="sort-indicator" v-if="sortBy === 'ip'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="col-location" @click="setSortBy('country')">
                位置 <span class="sort-indicator" v-if="sortBy === 'country'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="col-isp" @click="setSortBy('isp')">
                ISP信息 <span class="sort-indicator" v-if="sortBy === 'isp'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="col-details">详细信息</th>
              <th class="col-time" @click="setSortBy('queryTime')">
                查询时间 <span class="sort-indicator" v-if="sortBy === 'queryTime'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </th>
              <th class="col-status">状态</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(result, index) in filteredResults" 
              :key="result.ip || index"
              :class="{ 'error-row': result.error, 'success-row': !result.error }"
            >
              <td class="col-index">{{ index + 1 }}</td>
              <td class="col-ip">
                <code class="ip-code">{{ result.ip }}</code>
              </td>
              <td class="col-location">
                <div v-if="!result.error" class="location-info">
                  <div class="country">{{ result.country || '未知' }}</div>
                  <div class="city" v-if="result.city">{{ result.city }}</div>
                </div>
                <div v-else class="error-text">查询失败</div>
              </td>
              <td class="col-isp">
                <div v-if="!result.error" class="isp-info">
                  <div class="isp-name">{{ result.isp || '未知' }}</div>
                  <div class="asn" v-if="result.asn">ASN: {{ result.asn }}</div>
                </div>
                <div v-else class="error-text">-</div>
              </td>
              <td class="col-details">
                <div v-if="!result.error" class="details-info">
                  <div v-if="result.coordinates" class="coordinates">
                    📍 {{ result.coordinates }}
                  </div>
                  <div v-if="result.timezone" class="timezone">
                    🕐 {{ result.timezone }}
                  </div>
                </div>
                <div v-else class="error-details">
                  {{ result.error }}
                </div>
              </td>
              <td class="col-time">
                <span class="query-time">{{ formatQueryTime(result.queryTime) }}</span>
              </td>
              <td class="col-status">
                <span :class="['status-badge', result.error ? 'status-error' : 'status-success']">
                  {{ result.error ? '失败' : '成功' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-if="filteredResults.length === 0 && results.length > 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <div class="empty-text">没有找到匹配的结果</div>
      <button @click="clearFilters" class="clear-filter-btn">清除筛选条件</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface BatchResult {
  ip: string
  country?: string
  city?: string
  isp?: string
  asn?: string
  coordinates?: string
  timezone?: string
  queryTime?: number
  error?: string
}

interface Props {
  results: BatchResult[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  export: [format: string, data: BatchResult[]]
}>()

// 排序和筛选状态
const sortBy = ref<string>('index')
const sortOrder = ref<'asc' | 'desc'>('asc')
const filterText = ref('')

// 计算属性
const successCount = computed(() => props.results.filter(r => !r.error).length)
const errorCount = computed(() => props.results.filter(r => r.error).length)

const sortedResults = computed(() => {
  if (sortBy.value === 'index') {
    return [...props.results]
  }
  
  return [...props.results].sort((a, b) => {
    let aVal: any, bVal: any
    
    switch (sortBy.value) {
      case 'ip':
        aVal = a.ip
        bVal = b.ip
        break
      case 'country':
        aVal = a.country || ''
        bVal = b.country || ''
        break
      case 'city':
        aVal = a.city || ''
        bVal = b.city || ''
        break
      case 'isp':
        aVal = a.isp || ''
        bVal = b.isp || ''
        break
      case 'queryTime':
        aVal = a.queryTime || 0
        bVal = b.queryTime || 0
        break
      default:
        return 0
    }
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
})

const filteredResults = computed(() => {
  if (!filterText.value.trim()) {
    return sortedResults.value
  }
  
  const filter = filterText.value.toLowerCase()
  return sortedResults.value.filter(result => {
    return (
      result.ip.toLowerCase().includes(filter) ||
      (result.country && result.country.toLowerCase().includes(filter)) ||
      (result.city && result.city.toLowerCase().includes(filter)) ||
      (result.isp && result.isp.toLowerCase().includes(filter))
    )
  })
})

// 方法
const setSortBy = (field: string) => {
  if (sortBy.value === field) {
    toggleSortOrder()
  } else {
    sortBy.value = field
    sortOrder.value = 'asc'
  }
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const applySorting = () => {
  // 排序逻辑已在计算属性中处理
}

const applyFilters = () => {
  // 筛选逻辑已在计算属性中处理
}

const clearFilters = () => {
  filterText.value = ''
}

const formatQueryTime = (time?: number) => {
  if (!time) return '-'
  return `${time.toFixed(2)}ms`
}

const exportResults = (format: string) => {
  emit('export', format, filteredResults.value)
}
</script>

<style scoped>
.batch-results-container {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--border-radius-lg);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

/* 结果头部 */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md);
  border-bottom: 1px solid var(--glass-border);
  background: var(--glass-bg-light);
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.results-stats {
  display: flex;
  gap: var(--space-md);
  align-items: center;
}

.stats-item {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.success-badge, .error-badge {
  background: var(--success-color);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.8rem;
  font-weight: 500;
}

.error-badge {
  background: var(--error-color);
}

.results-actions {
  display: flex;
  gap: var(--space-md);
  align-items: center;
  flex-wrap: wrap;
}

/* 排序控制 */
.sort-controls {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.sort-select {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--border-radius-sm);
  padding: 0.4rem 0.8rem;
  color: var(--text-primary);
  font-size: 0.9rem;
}

.sort-order-btn {
  background: var(--button-secondary-bg);
  border: 1px solid var(--button-secondary-border);
  border-radius: var(--border-radius-sm);
  padding: 0.4rem 0.6rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-order-btn:hover {
  background: var(--button-secondary-hover);
}

/* 筛选控制 */
.filter-controls {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-input {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: var(--border-radius-sm);
  padding: 0.4rem 0.8rem;
  color: var(--text-primary);
  font-size: 0.9rem;
  width: 200px;
}

.clear-filter-btn {
  background: var(--error-color);
  color: white;
  border: none;
  border-radius: var(--border-radius-sm);
  padding: 0.4rem 0.6rem;
  margin-left: 0.5rem;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.clear-filter-btn:hover {
  background: var(--error-hover);
}

/* 导出控制 */
.export-controls {
  display: flex;
  gap: var(--space-xs);
}

.export-btn {
  background: var(--button-secondary-bg);
  border: 1px solid var(--button-secondary-border);
  border-radius: var(--border-radius-sm);
  padding: 0.4rem 0.8rem;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.export-btn:hover {
  background: var(--button-secondary-hover);
  transform: translateY(-1px);
}

/* 表格容器 */
.table-container {
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}

.table-wrapper {
  min-width: 100%;
}

/* 表格样式 */
.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.results-table th {
  background: var(--glass-bg-light);
  color: var(--text-primary);
  font-weight: 600;
  padding: var(--space-sm) var(--space-xs);
  text-align: left;
  border-bottom: 2px solid var(--glass-border);
  position: sticky;
  top: 0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.results-table th:hover {
  background: var(--glass-bg-hover);
}

.sort-indicator {
  margin-left: 0.5rem;
  color: var(--primary-color);
  font-weight: bold;
}

.results-table td {
  padding: var(--space-sm) var(--space-xs);
  border-bottom: 1px solid var(--glass-border);
  vertical-align: top;
}

.results-table tr:hover {
  background: var(--glass-bg-hover);
}

.success-row {
  background: rgba(34, 197, 94, 0.05);
}

.error-row {
  background: rgba(239, 68, 68, 0.05);
}

/* 列宽控制 */
.col-index { width: 60px; }
.col-ip { width: 140px; }
.col-location { width: 180px; }
.col-isp { width: 200px; }
.col-details { width: 220px; }
.col-time { width: 100px; }
.col-status { width: 80px; }

/* 单元格内容样式 */
.ip-code {
  background: var(--code-bg);
  color: var(--code-color);
  padding: 0.2rem 0.4rem;
  border-radius: var(--border-radius-xs);
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
}

.location-info .country {
  font-weight: 500;
  color: var(--text-primary);
}

.location-info .city {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.isp-info .isp-name {
  color: var(--text-primary);
}

.isp-info .asn {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.2rem;
}

.details-info {
  font-size: 0.8rem;
  line-height: 1.4;
}

.coordinates, .timezone {
  color: var(--text-secondary);
  margin-bottom: 0.2rem;
}

.query-time {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.status-badge {
  padding: 0.2rem 0.5rem;
  border-radius: var(--border-radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-success {
  background: var(--success-color);
  color: white;
}

.status-error {
  background: var(--error-color);
  color: white;
}

.error-text, .error-details {
  color: var(--error-color);
  font-size: 0.85rem;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-xl);
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--space-md);
}

.empty-text {
  font-size: 1.1rem;
  margin-bottom: var(--space-md);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .results-header {
    flex-direction: column;
    align-items: stretch;
  }

  .results-actions {
    justify-content: space-between;
  }

  .filter-input {
    width: 150px;
  }
}

@media (max-width: 768px) {
  .results-actions {
    flex-direction: column;
    gap: var(--space-sm);
  }

  .sort-controls, .filter-controls, .export-controls {
    width: 100%;
    justify-content: center;
  }

  .filter-input {
    width: 100%;
  }

  .results-table {
    font-size: 0.8rem;
  }

  .results-table th,
  .results-table td {
    padding: var(--space-xs);
  }

  /* 隐藏部分列在小屏幕上 */
  .col-details,
  .col-time {
    display: none;
  }
}

@media (max-width: 480px) {
  .col-isp {
    display: none;
  }

  .results-table {
    font-size: 0.75rem;
  }
}
</style>
