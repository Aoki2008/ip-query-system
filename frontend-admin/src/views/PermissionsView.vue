<template>
  <div class="permissions">
    <div class="page-header">
      <h1>权限管理</h1>
      <p>管理系统权限和角色分配</p>
    </div>

    <el-tabs v-model="activeTab" class="permissions-tabs">
      <!-- 权限列表 -->
      <el-tab-pane label="权限列表" name="permissions">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统权限</span>
              <el-button type="primary" size="small">
                <el-icon><Plus /></el-icon>
                新增权限
              </el-button>
            </div>
          </template>
          
          <el-table :data="permissions" v-loading="loading">
            <el-table-column prop="name" label="权限名称" />
            <el-table-column prop="code" label="权限代码" />
            <el-table-column prop="resource" label="资源" />
            <el-table-column prop="action" label="操作" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="is_active" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="text" size="small">编辑</el-button>
                <el-button type="text" size="small" style="color: #f56c6c">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 角色管理 -->
      <el-tab-pane label="角色管理" name="roles">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统角色</span>
              <el-button type="primary" size="small">
                <el-icon><Plus /></el-icon>
                新增角色
              </el-button>
            </div>
          </template>
          
          <el-table :data="roles" v-loading="loading">
            <el-table-column prop="name" label="角色名称" />
            <el-table-column prop="code" label="角色代码" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="is_system" label="类型">
              <template #default="{ row }">
                <el-tag :type="row.is_system ? 'warning' : 'primary'">
                  {{ row.is_system ? '系统角色' : '自定义角色' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button type="text" size="small">查看权限</el-button>
                <el-button type="text" size="small" v-if="!row.is_system">编辑</el-button>
                <el-button type="text" size="small" style="color: #f56c6c" v-if="!row.is_system">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 权限矩阵 -->
      <el-tab-pane label="权限矩阵" name="matrix">
        <el-card>
          <template #header>
            <span>权限矩阵</span>
          </template>
          
          <div class="matrix-container" v-loading="loading">
            <p class="matrix-info">
              资源类型：{{ matrix.resources?.length || 0 }} 个 | 
              操作类型：{{ matrix.actions?.length || 0 }} 个 | 
              角色数量：{{ matrix.roles?.length || 0 }} 个
            </p>
            
            <div class="matrix-table" v-if="matrix.resources">
              <table class="permission-matrix">
                <thead>
                  <tr>
                    <th>角色 / 权限</th>
                    <th v-for="resource in matrix.resources" :key="resource">
                      {{ resource }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="role in matrix.roles" :key="role.id">
                    <td class="role-name">
                      <strong>{{ role.name }}</strong>
                      <br>
                      <small>{{ role.code }}</small>
                    </td>
                    <td v-for="resource in matrix.resources" :key="resource" class="permission-cell">
                      <div class="actions">
                        <span 
                          v-for="action in matrix.actions" 
                          :key="action"
                          :class="['action-badge', { 'has-permission': hasPermission(role, resource, action) }]"
                          :title="`${resource}:${action}`"
                        >
                          {{ action.charAt(0).toUpperCase() }}
                        </span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const activeTab = ref('permissions')
const loading = ref(false)

const permissions = ref([])
const roles = ref([])
const matrix = ref<any>({})

const loadPermissions = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/permissions/permissions')
    permissions.value = response.data
  } catch (error) {
    ElMessage.error('加载权限列表失败')
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/permissions/roles')
    roles.value = response.data
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

const loadMatrix = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/permissions/matrix')
    matrix.value = response.data
  } catch (error) {
    ElMessage.error('加载权限矩阵失败')
  } finally {
    loading.value = false
  }
}

const hasPermission = (role: any, resource: string, action: string) => {
  const permissionKey = `${resource}:${action}`
  return role.permissions && role.permissions[permissionKey]
}

onMounted(async () => {
  await Promise.all([
    loadPermissions(),
    loadRoles(),
    loadMatrix()
  ])
})
</script>

<style scoped>
.permissions {
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

.permissions-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.matrix-info {
  margin-bottom: 20px;
  color: #606266;
  font-size: 14px;
}

.matrix-container {
  overflow-x: auto;
}

.permission-matrix {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.permission-matrix th,
.permission-matrix td {
  border: 1px solid #ebeef5;
  padding: 8px;
  text-align: center;
}

.permission-matrix th {
  background-color: #f5f7fa;
  font-weight: 600;
}

.role-name {
  text-align: left !important;
  min-width: 120px;
}

.permission-cell {
  min-width: 80px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 2px;
}

.action-badge {
  display: inline-block;
  width: 16px;
  height: 16px;
  line-height: 16px;
  border-radius: 50%;
  background-color: #f5f7fa;
  color: #c0c4cc;
  font-size: 10px;
  font-weight: bold;
}

.action-badge.has-permission {
  background-color: #67c23a;
  color: white;
}
</style>
