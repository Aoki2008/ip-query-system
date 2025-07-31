<template>
  <div class="system">
    <div class="page-header">
      <h1>系统设置</h1>
      <p>管理系统配置和数据库设置</p>
    </div>

    <!-- 数据库管理 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <div class="card-header">
          <span>🗄️ 数据库管理</span>
          <el-button type="primary" size="small" @click="refreshDatabaseInfo" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="database-info">
            <h4>当前数据库状态</h4>
            <div class="info-item">
              <span class="label">城市数据库：</span>
              <el-tag :type="databaseInfo.database_status?.city_db ? 'success' : 'danger'">
                {{ databaseInfo.current_databases?.city_db || '未设置' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">ASN数据库：</span>
              <el-tag :type="databaseInfo.database_status?.asn_db ? 'success' : 'danger'">
                {{ databaseInfo.current_databases?.asn_db || '未设置' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">国家数据库：</span>
              <el-tag :type="databaseInfo.database_status?.country_db ? 'success' : 'danger'">
                {{ databaseInfo.current_databases?.country_db || '未设置' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">数据库状态：</span>
              <el-tag :type="getDatabaseStatusType()">
                {{ getDatabaseStatusText() }}
              </el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="database-switch">
            <h4>切换数据库文件</h4>
            <el-form :model="switchForm" label-width="120px">
              <el-form-item label="城市数据库">
                <el-select
                  v-model="switchForm.cityDb"
                  placeholder="选择城市数据库文件"
                  style="width: 100%"
                  popper-class="database-file-dropdown"
                >
                  <el-option
                    v-for="(db, key) in detailedDatabaseInfo.city_databases"
                    :key="key"
                    :label="db.display_name"
                    :value="key"
                    :disabled="key === databaseInfo.current_databases?.city_db"
                    class="db-option"
                  >
                    <div class="db-option-content">
                      <div class="db-header">
                        <span class="db-name">
                          <el-icon v-if="key === databaseInfo.current_databases?.city_db" class="current-icon">
                            <Check />
                          </el-icon>
                          {{ db.display_name }}
                        </span>
                        <el-tag
                          v-if="key === databaseInfo.current_databases?.city_db"
                          type="success"
                          size="small"
                          class="current-tag"
                        >
                          当前使用
                        </el-tag>
                      </div>
                      <div class="db-details">
                        <div class="db-info">
                          <span class="db-path">{{ db.path }}</span>
                          <span class="db-size">({{ db.size_mb }}MB)</span>
                          <el-tag
                            :type="getStatusTagType(db.status)"
                            size="small"
                          >
                            {{ db.status }}
                          </el-tag>
                        </div>
                        <div class="db-description">
                          {{ db.source_location }}
                        </div>
                      </div>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="ASN数据库">
                <el-select
                  v-model="switchForm.asnDb"
                  placeholder="选择ASN数据库文件"
                  style="width: 100%"
                  popper-class="database-file-dropdown"
                >
                  <el-option
                    v-for="(db, key) in detailedDatabaseInfo.asn_databases"
                    :key="key"
                    :label="db.display_name"
                    :value="key"
                    :disabled="key === databaseInfo.current_databases?.asn_db"
                    class="db-option"
                  >
                    <div class="db-option-content">
                      <div class="db-header">
                        <span class="db-name">
                          <el-icon v-if="key === databaseInfo.current_databases?.asn_db" class="current-icon">
                            <Check />
                          </el-icon>
                          {{ db.display_name }}
                        </span>
                        <el-tag
                          v-if="key === databaseInfo.current_databases?.asn_db"
                          type="success"
                          size="small"
                          class="current-tag"
                        >
                          当前使用
                        </el-tag>
                      </div>
                      <div class="db-details">
                        <div class="db-info">
                          <span class="db-path">{{ db.path }}</span>
                          <span class="db-size">({{ db.size_mb }}MB)</span>
                          <el-tag
                            :type="getStatusTagType(db.status)"
                            size="small"
                          >
                            {{ db.status }}
                          </el-tag>
                        </div>
                        <div class="db-description">
                          {{ db.source_location }}
                        </div>
                      </div>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="国家数据库">
                <el-select
                  v-model="switchForm.countryDb"
                  placeholder="选择国家数据库文件"
                  style="width: 100%"
                  popper-class="database-file-dropdown"
                >
                  <el-option
                    v-for="(db, key) in detailedDatabaseInfo.country_databases"
                    :key="key"
                    :label="db.display_name"
                    :value="key"
                    :disabled="key === databaseInfo.current_databases?.country_db"
                    class="db-option"
                  >
                    <div class="db-option-content">
                      <div class="db-header">
                        <span class="db-name">
                          <el-icon v-if="key === databaseInfo.current_databases?.country_db" class="current-icon">
                            <Check />
                          </el-icon>
                          {{ db.display_name }}
                        </span>
                        <el-tag
                          v-if="key === databaseInfo.current_databases?.country_db"
                          type="success"
                          size="small"
                          class="current-tag"
                        >
                          当前使用
                        </el-tag>
                      </div>
                      <div class="db-details">
                        <div class="db-info">
                          <span class="db-path">{{ db.path }}</span>
                          <span class="db-size">({{ db.size_mb }}MB)</span>
                          <el-tag
                            :type="getStatusTagType(db.status)"
                            size="small"
                          >
                            {{ db.status }}
                          </el-tag>
                        </div>
                        <div class="db-description">
                          {{ db.source_location }}
                        </div>
                      </div>
                    </div>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="switchDatabase"
                  :loading="switching"
                  :disabled="!canSwitchDatabase"
                >
                  切换数据库
                </el-button>
                <el-button
                  type="success"
                  @click="testDatabase"
                  :loading="testing"
                >
                  测试当前配置
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>
      </el-row>

      <!-- 可用数据库详情 -->
      <el-divider>可用数据库文件</el-divider>
      <el-table :data="databaseTableData" style="width: 100%">
        <el-table-column prop="name" label="数据库名称" width="200" />
        <el-table-column prop="path" label="文件路径" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '可用' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>📊 系统统计</span>
          </template>

          <div class="system-stats" v-if="systemStats">
            <div class="stat-item">
              <span class="label">总查询次数：</span>
              <span class="value">{{ systemStats.total_queries || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="label">成功查询：</span>
              <span class="value success">{{ systemStats.successful_queries || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="label">失败查询：</span>
              <span class="value error">{{ systemStats.failed_queries || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="label">平均响应时间：</span>
              <span class="value">{{ (systemStats.avg_query_time * 1000).toFixed(2) }}ms</span>
            </div>
            <div class="stat-item">
              <span class="label">并发限制：</span>
              <span class="value">{{ systemStats.concurrent_limit || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🛠️ 系统操作</span>
          </template>

          <div class="system-actions">
            <el-button type="primary" @click="checkHealth" :loading="healthChecking">
              <el-icon><Monitor /></el-icon>
              系统健康检查
            </el-button>

            <el-button type="success" @click="rescanDatabases" :loading="rescanning">
              <el-icon><Search /></el-icon>
              重新扫描数据库
            </el-button>

            <el-button type="warning" @click="refreshStats" :loading="refreshingStats">
              <el-icon><Refresh /></el-icon>
              刷新统计信息
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统信息 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>ℹ️ 系统信息</span>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <div class="info-item">
            <span class="label">系统名称：</span>
            <span>IP查询工具管理后台</span>
          </div>
          <div class="info-item">
            <span class="label">系统版本：</span>
            <span>1.0.0</span>
          </div>
          <div class="info-item">
            <span class="label">后端框架：</span>
            <span>FastAPI</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">前端框架：</span>
            <span>Vue 3 + Element Plus</span>
          </div>
          <div class="info-item">
            <span class="label">数据库：</span>
            <span>SQLite + GeoLite2</span>
          </div>
          <div class="info-item">
            <span class="label">部署环境：</span>
            <span>本地开发</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <span class="label">启动时间：</span>
            <span>{{ new Date().toLocaleString() }}</span>
          </div>
          <div class="info-item">
            <span class="label">运行状态：</span>
            <el-tag type="success">正常运行</el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Monitor, Search, Check } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const switching = ref(false)
const testing = ref(false)
const healthChecking = ref(false)
const rescanning = ref(false)
const refreshingStats = ref(false)

const databaseInfo = ref({
  current_databases: {
    city_db: '',
    asn_db: '',
    country_db: ''
  },
  available_databases: {},
  database_status: {
    city_db: false,
    asn_db: false,
    country_db: false
  },
  database_files: {
    city_databases: [],
    asn_databases: [],
    country_databases: []
  }
})

const detailedDatabaseInfo = ref({
  current_databases: {
    city_db: '',
    asn_db: '',
    country_db: ''
  },
  database_details: {},
  city_databases: {},
  asn_databases: {},
  country_databases: {}
})

const systemStats = ref({
  total_queries: 0,
  successful_queries: 0,
  failed_queries: 0,
  avg_query_time: 0,
  concurrent_limit: 0
})

const switchForm = ref({
  cityDb: '',
  asnDb: '',
  countryDb: ''
})

// 计算属性
const databaseTableData = computed(() => {
  const data = []
  const databases = databaseInfo.value.available_databases

  for (const [key, dbInfo] of Object.entries(databases)) {
    // 处理新的数据结构
    if (typeof dbInfo === 'object' && dbInfo !== null) {
      data.push({
        name: key,
        path: dbInfo.path || '',
        status: dbInfo.status || '未知'
      })
    } else {
      // 兼容旧的数据结构
      data.push({
        name: key,
        path: dbInfo,
        status: '可用'
      })
    }
  }

  return data
})

// 计算是否可以切换数据库
const canSwitchDatabase = computed(() => {
  const hasChanges = (
    (switchForm.value.cityDb && switchForm.value.cityDb !== databaseInfo.value.current_databases?.city_db) ||
    (switchForm.value.asnDb && switchForm.value.asnDb !== databaseInfo.value.current_databases?.asn_db) ||
    (switchForm.value.countryDb && switchForm.value.countryDb !== databaseInfo.value.current_databases?.country_db)
  )
  return hasChanges
})

// 计算数据库状态类型
const getDatabaseStatusType = () => {
  const { city_db, asn_db, country_db } = databaseInfo.value.database_status || {}
  const loadedCount = [city_db, asn_db, country_db].filter(Boolean).length

  if (loadedCount === 3) return 'success'
  if (loadedCount === 0) return 'danger'
  return 'warning'
}

// 计算数据库状态文本
const getDatabaseStatusText = () => {
  const { city_db, asn_db, country_db } = databaseInfo.value.database_status || {}
  const loadedCount = [city_db, asn_db, country_db].filter(Boolean).length

  if (loadedCount === 3) return '全部已加载'
  if (loadedCount === 0) return '未加载'
  return `部分已加载 (${loadedCount}/3)`
}

// 方法
const getSourceDisplayName = (source: string) => {
  const names = {
    'local': '本地数据库',
    'api': 'API目录数据库',
    'mixed': '混合模式'
  }
  return names[source] || source
}

const getSourceDescription = (source: string) => {
  const descriptions = {
    'local': '使用项目根目录数据库',
    'api': '使用API目录数据库',
    'mixed': '优先本地，回退API'
  }
  return descriptions[source] || ''
}

const getSourceTagType = (source: string) => {
  const types = {
    'local': 'success',
    'api': 'warning',
    'mixed': 'info'
  }
  return types[source] || 'info'
}

const getStatusTagType = (status: string) => {
  const types = {
    '已加载': 'success',
    '可用': 'info',
    '未加载': 'warning',
    '不存在': 'danger',
    '错误': 'danger'
  }
  return types[status] || 'info'
}

const fetchDetailedDatabaseInfo = async () => {
  try {
    console.log('🔍 获取详细数据库文件信息...')
    const response = await api.get('/admin/system/database/files/detailed')
    detailedDatabaseInfo.value = response.data
    console.log('✅ 详细数据库文件信息获取成功:', response.data)
  } catch (error) {
    console.error('❌ 获取详细数据库文件信息失败:', error)
    ElMessage.error('获取详细数据库文件信息失败')
  }
}

const refreshDatabaseInfo = async () => {
  loading.value = true
  try {
    console.log('🔍 开始获取数据库信息...')
    const response = await api.get('/admin/system/database/info')
    console.log('✅ 数据库信息获取成功:', response.data)
    databaseInfo.value = response.data

    // 同时获取详细数据库文件信息
    await fetchDetailedDatabaseInfo()
  } catch (error) {
    console.error('❌ 获取数据库信息失败:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers
      }
    })

    // 更详细的错误消息
    let errorMessage = '获取数据库信息失败'
    if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录'
    } else if (error.response?.status === 403) {
      errorMessage = '权限不足'
    } else if (error.response?.status === 404) {
      errorMessage = 'API端点不存在'
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器内部错误'
    } else if (error.code === 'NETWORK_ERROR') {
      errorMessage = '网络连接错误'
    }

    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const refreshStats = async () => {
  refreshingStats.value = true
  try {
    console.log('📊 开始获取系统统计...')
    const response = await api.get('/admin/system/stats')
    console.log('✅ 系统统计获取成功:', response.data)
    systemStats.value = response.data.geoip_stats
  } catch (error) {
    console.error('❌ 获取系统统计失败:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data
    })
    ElMessage.error('获取系统统计失败')
  } finally {
    refreshingStats.value = false
  }
}

const switchDatabase = async () => {
  if (!canSwitchDatabase.value) {
    ElMessage.warning('请选择要切换的数据库文件')
    return
  }

  try {
    const changes = []
    if (switchForm.value.cityDb && switchForm.value.cityDb !== databaseInfo.value.current_databases?.city_db) {
      const dbInfo = detailedDatabaseInfo.value.city_databases[switchForm.value.cityDb]
      changes.push(`城市数据库: ${dbInfo?.display_name}`)
    }
    if (switchForm.value.asnDb && switchForm.value.asnDb !== databaseInfo.value.current_databases?.asn_db) {
      const dbInfo = detailedDatabaseInfo.value.asn_databases[switchForm.value.asnDb]
      changes.push(`ASN数据库: ${dbInfo?.display_name}`)
    }
    if (switchForm.value.countryDb && switchForm.value.countryDb !== databaseInfo.value.current_databases?.country_db) {
      const dbInfo = detailedDatabaseInfo.value.country_databases[switchForm.value.countryDb]
      changes.push(`国家数据库: ${dbInfo?.display_name}`)
    }

    await ElMessageBox.confirm(
      `确定要切换以下数据库吗？\n${changes.join('\n')}`,
      '确认切换',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    switching.value = true

    const requestData = {}
    if (switchForm.value.cityDb && switchForm.value.cityDb !== databaseInfo.value.current_databases?.city_db) {
      requestData.city_db_key = switchForm.value.cityDb
    }
    if (switchForm.value.asnDb && switchForm.value.asnDb !== databaseInfo.value.current_databases?.asn_db) {
      requestData.asn_db_key = switchForm.value.asnDb
    }
    if (switchForm.value.countryDb && switchForm.value.countryDb !== databaseInfo.value.current_databases?.country_db) {
      requestData.country_db_key = switchForm.value.countryDb
    }

    const response = await api.post('/admin/system/database/switch', requestData)

    if (response.data.success) {
      ElMessage.success(response.data.message)
      await refreshDatabaseInfo()
      await refreshStats()
      // 重置表单
      switchForm.value.cityDb = ''
      switchForm.value.asnDb = ''
      switchForm.value.countryDb = ''
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换数据库文件失败:', error)
      ElMessage.error('切换数据库文件失败')
    }
  } finally {
    switching.value = false
  }
}

const testDatabase = async () => {
  testing.value = true
  try {
    const response = await api.get('/admin/system/database/test/current')

    if (response.data.success) {
      const result = response.data.test_result
      const currentDbs = response.data.current_databases
      ElMessage.success({
        message: `测试成功！当前配置 (城市: ${currentDbs.city_db || '未设置'}, ASN: ${currentDbs.asn_db || '未设置'}, 国家: ${currentDbs.country_db || '未设置'})，查询 ${result.ip}，结果：${result.country}，耗时：${(result.query_time * 1000).toFixed(2)}ms`,
        duration: 5000
      })
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('测试当前数据库配置失败:', error)
    ElMessage.error('测试当前数据库配置失败')
  } finally {
    testing.value = false
  }
}

const checkHealth = async () => {
  healthChecking.value = true
  try {
    const response = await api.get('/health')
    ElMessage.success(`系统状态：${response.data.message}`)
  } catch (error) {
    console.error('系统健康检查失败:', error)
    ElMessage.error('系统健康检查失败')
  } finally {
    healthChecking.value = false
  }
}

const rescanDatabases = async () => {
  rescanning.value = true
  try {
    const response = await api.post('/admin/system/database/rescan')

    if (response.data.success) {
      ElMessage.success(response.data.message)
      await refreshDatabaseInfo()
    } else {
      ElMessage.error('重新扫描失败')
    }
  } catch (error) {
    console.error('重新扫描数据库失败:', error)
    ElMessage.error('重新扫描数据库失败')
  } finally {
    rescanning.value = false
  }
}

// 生命周期
onMounted(async () => {
  await refreshDatabaseInfo()
  await refreshStats()
})
</script>

<style scoped>
.system {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.database-info,
.database-switch {
  padding: 10px 0;
}

.database-info h4,
.database-switch h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.label {
  color: #606266;
  font-weight: 500;
  min-width: 120px;
}

.system-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}

.value {
  font-weight: 600;
  color: #303133;
}

.value.success {
  color: #67c23a;
}

.value.error {
  color: #f56c6c;
}

.system-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.system-actions .el-button {
  justify-content: flex-start;
}

.el-table {
  margin-top: 15px;
}

.el-divider {
  margin: 20px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .system {
    padding: 0 10px;
  }

  .el-col {
    margin-bottom: 20px;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .label {
    min-width: auto;
    margin-bottom: 5px;
  }
}

/* 数据库文件下拉菜单样式 */
.db-option-content {
  width: 100%;
  padding: 8px 0;
}

.db-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.db-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.current-icon {
  color: #67c23a;
  font-size: 16px;
}

.current-tag {
  font-size: 11px;
  padding: 2px 6px;
}

.db-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.db-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #606266;
}

.db-path {
  flex: 1;
  color: #409eff;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.db-size {
  color: #909399;
  font-size: 11px;
}

.db-description {
  font-size: 12px;
  color: #909399;
  font-style: italic;
  margin-top: 4px;
}
</style>

<style>
/* 全局样式 - 数据库文件下拉菜单 */
.database-file-dropdown {
  max-width: 500px;
}

.database-file-dropdown .el-select-dropdown__item {
  height: auto;
  padding: 12px 20px;
  line-height: 1.4;
}

.database-file-dropdown .el-select-dropdown__item.is-disabled {
  background-color: #f5f7fa;
  border-left: 3px solid #67c23a;
}

.database-file-dropdown .el-select-dropdown__item:hover {
  background-color: #f0f9ff;
}

@media (max-width: 768px) {
  .database-file-dropdown {
    max-width: 90vw;
  }

  .database-file-dropdown .el-select-dropdown__item {
    padding: 8px 12px;
  }

  .db-option-content {
    padding: 6px 0;
  }

  .db-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .db-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .db-path {
    max-width: 100%;
    font-size: 10px;
  }

  .db-size {
    font-size: 10px;
  }
}
</style>
