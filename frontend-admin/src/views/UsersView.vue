<template>
  <div class="users">
    <div class="page-header">
      <h1>用户管理</h1>
      <p>管理系统管理员用户</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>管理员用户列表</span>
          <el-button type="primary" size="small">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>
      
      <MobileTable
        :data="users"
        v-loading="loading"
        :mobile-columns="mobileColumns"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录">
          <template #default="{ row }">
            {{ formatDate(row.last_login) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="text" size="small">编辑</el-button>
            <el-button type="text" size="small">角色</el-button>
            <el-button type="text" size="small" style="color: #f56c6c" v-if="row.username !== 'admin'">
              删除
            </el-button>
          </template>
        </el-table-column>

        <!-- 移动端卡片模板 -->
        <template #mobile-card="{ row }">
          <div class="user-card">
            <div class="user-header">
              <h4>{{ row.username }}</h4>
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </div>
            <div class="user-info">
              <p><strong>邮箱:</strong> {{ row.email }}</p>
              <p><strong>角色:</strong>
                <el-tag :type="getRoleType(row.role)" size="small">
                  {{ getRoleLabel(row.role) }}
                </el-tag>
              </p>
              <p><strong>创建时间:</strong> {{ formatDate(row.created_at) }}</p>
              <p v-if="row.last_login"><strong>最后登录:</strong> {{ formatDate(row.last_login) }}</p>
            </div>
          </div>
        </template>

        <!-- 移动端操作按钮 -->
        <template #actions="{ row }">
          <el-button type="primary" size="small">编辑</el-button>
          <el-button type="info" size="small">角色</el-button>
          <el-button
            v-if="row.username !== 'admin'"
            type="danger"
            size="small"
          >
            删除
          </el-button>
        </template>
      </MobileTable>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import MobileTable from '@/components/MobileTable.vue'

const loading = ref(false)
const users = ref([])

// 移动端表格列配置
const mobileColumns = [
  { prop: 'username', label: '用户名' },
  { prop: 'email', label: '邮箱' },
  {
    prop: 'role',
    label: '角色',
    formatter: (row: any) => getRoleLabel(row.role)
  },
  {
    prop: 'is_active',
    label: '状态',
    formatter: (row: any) => row.is_active ? '激活' : '禁用'
  },
  {
    prop: 'created_at',
    label: '创建时间',
    formatter: (row: any) => formatDate(row.created_at)
  }
]

const loadUsers = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/auth/users')
    users.value = response.data
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const getRoleType = (role: string) => {
  switch (role) {
    case 'super_admin': return 'danger'
    case 'admin': return 'warning'
    default: return 'info'
  }
}

const getRoleLabel = (role: string) => {
  switch (role) {
    case 'super_admin': return '超级管理员'
    case 'admin': return '管理员'
    default: return '普通用户'
  }
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users {
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

/* 移动端用户卡片样式 */
.user-card {
  width: 100%;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.user-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.user-info p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info strong {
  min-width: 70px;
  color: #303133;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .page-header {
    margin-bottom: 20px;
  }

  .page-header h1 {
    font-size: 20px;
  }

  .page-header p {
    font-size: 14px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .card-header span {
    font-size: 16px;
    font-weight: 600;
  }

  .user-header h4 {
    font-size: 15px;
  }

  .user-info p {
    font-size: 13px;
  }

  .user-info strong {
    min-width: 60px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 18px;
  }

  .user-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .user-info p {
    font-size: 12px;
  }

  .user-info strong {
    min-width: 55px;
    font-size: 12px;
  }
}
</style>
