<template>
  <div class="mobile-table">
    <!-- 桌面端表格 -->
    <el-table
      v-if="!isMobile"
      :data="data"
      v-bind="$attrs"
      @selection-change="handleSelectionChange"
    >
      <slot />
    </el-table>
    
    <!-- 移动端卡片列表 -->
    <div v-else class="mobile-cards">
      <div
        v-for="(item, index) in data"
        :key="index"
        class="mobile-card"
        @click="handleRowClick(item, index)"
      >
        <slot name="mobile-card" :row="item" :index="index">
          <!-- 默认移动端卡片布局 -->
          <div class="card-content">
            <div v-for="column in mobileColumns" :key="column.prop" class="card-row">
              <span class="card-label">{{ column.label }}:</span>
              <span class="card-value">{{ getColumnValue(item, column) }}</span>
            </div>
          </div>
        </slot>
        
        <!-- 操作按钮 -->
        <div v-if="$slots.actions" class="card-actions">
          <slot name="actions" :row="item" :index="index" />
        </div>
      </div>
      
      <!-- 空数据提示 -->
      <div v-if="data.length === 0" class="empty-data">
        <el-empty description="暂无数据" />
      </div>
    </div>
    
    <!-- 分页 -->
    <div v-if="showPagination" class="pagination-wrapper">
      <el-pagination
        v-bind="paginationProps"
        :small="isMobile"
        layout="prev, pager, next"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Column {
  prop: string
  label: string
  formatter?: (row: any, column: any, cellValue: any) => string
}

interface Props {
  data: any[]
  mobileColumns?: Column[]
  showPagination?: boolean
  paginationProps?: any
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  mobileColumns: () => [],
  showPagination: false,
  paginationProps: () => ({})
})

const emit = defineEmits(['selection-change', 'row-click', 'current-change', 'size-change'])

const isMobile = ref(false)

// 检查是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// 获取列值
const getColumnValue = (row: any, column: Column) => {
  const value = row[column.prop]
  if (column.formatter) {
    return column.formatter(row, column, value)
  }
  return value
}

// 处理选择变化
const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}

// 处理行点击
const handleRowClick = (row: any, index: number) => {
  emit('row-click', row, index)
}

// 处理分页变化
const handleCurrentChange = (page: number) => {
  emit('current-change', page)
}

const handleSizeChange = (size: number) => {
  emit('size-change', size)
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.mobile-table {
  width: 100%;
}

.mobile-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s;
}

.mobile-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-content {
  margin-bottom: 12px;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 4px 0;
  border-bottom: 1px solid #f5f7fa;
}

.card-row:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.card-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
  min-width: 80px;
}

.card-value {
  color: #303133;
  font-size: 14px;
  text-align: right;
  flex: 1;
  word-break: break-all;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f5f7fa;
}

.card-actions :deep(.el-button) {
  padding: 6px 12px;
  font-size: 12px;
}

.empty-data {
  text-align: center;
  padding: 40px 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: center;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .mobile-cards {
    gap: 10px;
  }
  
  .mobile-card {
    padding: 12px;
  }
  
  .card-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .card-label {
    min-width: auto;
    font-size: 13px;
  }
  
  .card-value {
    text-align: left;
    font-size: 13px;
  }
  
  .card-actions {
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .pagination-wrapper {
    margin-top: 15px;
  }
}

@media (max-width: 480px) {
  .mobile-card {
    padding: 10px;
  }
  
  .card-label,
  .card-value {
    font-size: 12px;
  }
  
  .card-actions :deep(.el-button) {
    padding: 4px 8px;
    font-size: 11px;
  }
}
</style>
