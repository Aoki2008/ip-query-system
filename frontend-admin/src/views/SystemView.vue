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
              <span class="label">当前数据源：</span>
              <el-tag :type="getSourceTagType(databaseInfo.current_source)">
                {{ getSourceDisplayName(databaseInfo.current_source) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">城市数据库：</span>
              <el-tag :type="databaseInfo.database_status?.city_db ? 'success' : 'danger'">
                {{ databaseInfo.database_status?.city_db ? '已加载' : '未加载' }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">ASN数据库：</span>
              <el-tag :type="databaseInfo.database_status?.asn_db ? 'success' : 'danger'">
                {{ databaseInfo.database_status?.asn_db ? '已加载' : '未加载' }}
              </el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="database-switch">
            <h4>切换数据源</h4>
            <el-form :model="switchForm" label-width="100px">
              <el-form-item label="数据源">
                <el-select
                  v-model="switchForm.source"
                  placeholder="选择数据源"
                  style="width: 100%"
                >
                  <el-option
                    v-for="source in databaseInfo.available_sources"
                    :key="source"
                    :label="getSourceDisplayName(source)"
                    :value="source"
                    :disabled="source === databaseInfo.current_source"
                  >
                    <span>{{ getSourceDisplayName(source) }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ getSourceDescription(source) }}
                    </span>
                  </el-option>
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="switchDatabase"
                  :loading="switching"
                  :disabled="!switchForm.source || switchForm.source === databaseInfo.current_source"
                >
                  切换数据源
                </el-button>
                <el-button
                  type="success"
                  @click="testDatabase"
                  :loading="testing"
                  :disabled="!switchForm.source"
                >
                  测试数据源
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
import { Refresh, Monitor, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

// 响应式数据
const loading = ref(false)
const switching = ref(false)
const testing = ref(false)
const healthChecking = ref(false)
const rescanning = ref(false)
const refreshingStats = ref(false)

const databaseInfo = ref({
  current_source: '',
  available_sources: [],
  available_databases: {},
  database_status: {
    city_db: false,
    asn_db: false
  }
})

const systemStats = ref({
  total_queries: 0,
  successful_queries: 0,
  failed_queries: 0,
  avg_query_time: 0,
  concurrent_limit: 0
})

const switchForm = ref({
  source: ''
})

// 计算属性
const databaseTableData = computed(() => {
  const data = []
  const databases = databaseInfo.value.available_databases

  for (const [key, path] of Object.entries(databases)) {
    data.push({
      name: key,
      path: path,
      status: '可用'
    })
  }

  return data
})

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

const refreshDatabaseInfo = async () => {
  loading.value = true
  try {
    console.log('🔍 开始获取数据库信息...')
    const response = await api.get('/admin/system/database/info')
    console.log('✅ 数据库信息获取成功:', response.data)
    databaseInfo.value = response.data
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
  if (!switchForm.value.source) {
    ElMessage.warning('请选择要切换的数据源')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要切换到 ${getSourceDisplayName(switchForm.value.source)} 吗？`,
      '确认切换',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    switching.value = true

    const response = await api.post('/admin/system/database/switch', {
      source: switchForm.value.source
    })

    if (response.data.success) {
      ElMessage.success(response.data.message)
      await refreshDatabaseInfo()
      await refreshStats()
      switchForm.value.source = ''
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换数据库失败:', error)
      ElMessage.error('切换数据库失败')
    }
  } finally {
    switching.value = false
  }
}

const testDatabase = async () => {
  if (!switchForm.value.source) {
    ElMessage.warning('请选择要测试的数据源')
    return
  }

  testing.value = true
  try {
    const response = await api.get(`/admin/system/database/test/${switchForm.value.source}`)

    if (response.data.success) {
      const result = response.data.test_result
      ElMessage.success({
        message: `测试成功！查询 ${result.ip}，结果：${result.country}，耗时：${(result.query_time * 1000).toFixed(2)}ms`,
        duration: 5000
      })
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('测试数据库失败:', error)
    ElMessage.error('测试数据库失败')
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
</style>
