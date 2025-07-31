<template>
  <div class="service-status">
    <el-alert
      v-if="!isBackendOnline"
      title="后端服务离线"
      type="error"
      :closable="false"
      show-icon
    >
      <template #default>
        <p>无法连接到后端服务 (http://localhost:8000)</p>
        <p>请确保后端服务已启动：</p>
        <ul>
          <li>运行 <code>cd backend-fastapi && python main.py</code></li>
          <li>或使用 <code>docker-compose up -d backend</code></li>
        </ul>
        <el-button 
          type="primary" 
          size="small" 
          @click="checkBackendStatus"
          :loading="checking"
          style="margin-top: 10px;"
        >
          重新检查
        </el-button>
      </template>
    </el-alert>
    
    <el-alert
      v-else
      title="服务状态正常"
      type="success"
      :closable="false"
      show-icon
    >
      后端服务运行正常
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElAlert, ElButton, ElMessage } from 'element-plus'
import api from '@/utils/api'

const isBackendOnline = ref(false)
const checking = ref(false)

const checkBackendStatus = async () => {
  checking.value = true
  try {
    // 使用较短的超时时间进行健康检查
    const response = await api.get('/health', { timeout: 5000 })
    isBackendOnline.value = response.status === 200
    if (isBackendOnline.value) {
      ElMessage.success('后端服务连接成功')
    }
  } catch (error) {
    isBackendOnline.value = false
    console.error('Backend health check failed:', error)
  } finally {
    checking.value = false
  }
}

onMounted(() => {
  checkBackendStatus()
})
</script>

<style scoped>
.service-status {
  margin-bottom: 20px;
}

code {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

ul {
  margin: 10px 0;
  padding-left: 20px;
}

li {
  margin: 5px 0;
}
</style>
