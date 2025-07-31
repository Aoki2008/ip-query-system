<template>
  <el-form
    ref="formRef"
    :model="model"
    :rules="rules"
    :label-position="isMobile ? 'top' : 'right'"
    :label-width="isMobile ? 'auto' : '120px'"
    class="mobile-form"
    v-bind="$attrs"
  >
    <slot />
    
    <!-- 表单操作按钮 -->
    <el-form-item v-if="showActions" class="form-actions">
      <div class="action-buttons" :class="{ 'mobile-actions': isMobile }">
        <el-button
          v-if="showCancel"
          :size="isMobile ? 'default' : 'default'"
          @click="handleCancel"
        >
          {{ cancelText }}
        </el-button>
        
        <el-button
          type="primary"
          :size="isMobile ? 'default' : 'default'"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ submitText }}
        </el-button>
      </div>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  model: Record<string, any>
  rules?: FormRules
  loading?: boolean
  showActions?: boolean
  showCancel?: boolean
  submitText?: string
  cancelText?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showActions: true,
  showCancel: true,
  submitText: '确定',
  cancelText: '取消'
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref<FormInstance>()
const isMobile = ref(false)

// 检查是否为移动设备
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('submit', props.model)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 清除验证
const clearValidate = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 验证表单
const validate = () => {
  if (formRef.value) {
    return formRef.value.validate()
  }
  return Promise.resolve(false)
}

// 暴露方法
defineExpose({
  resetForm,
  clearValidate,
  validate
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.mobile-form {
  width: 100%;
}

.form-actions {
  margin-top: 24px;
  margin-bottom: 0;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.action-buttons.mobile-actions {
  flex-direction: column-reverse;
  gap: 8px;
}

.action-buttons.mobile-actions .el-button {
  width: 100%;
  margin-left: 0 !important;
}

/* 移动端表单优化 */
@media (max-width: 768px) {
  .mobile-form :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  .mobile-form :deep(.el-form-item__label) {
    font-size: 14px;
    font-weight: 600;
    color: #606266;
    padding-bottom: 6px;
  }
  
  .mobile-form :deep(.el-input__inner),
  .mobile-form :deep(.el-textarea__inner) {
    font-size: 16px; /* 防止iOS缩放 */
    padding: 12px;
  }
  
  .mobile-form :deep(.el-select) {
    width: 100%;
  }
  
  .mobile-form :deep(.el-select .el-input__inner) {
    font-size: 16px;
  }
  
  .mobile-form :deep(.el-date-editor) {
    width: 100%;
  }
  
  .mobile-form :deep(.el-date-editor .el-input__inner) {
    font-size: 16px;
  }
  
  .mobile-form :deep(.el-radio-group),
  .mobile-form :deep(.el-checkbox-group) {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .mobile-form :deep(.el-radio),
  .mobile-form :deep(.el-checkbox) {
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .mobile-form :deep(.el-upload) {
    width: 100%;
  }
  
  .mobile-form :deep(.el-upload-dragger) {
    width: 100%;
    height: 120px;
  }
}

@media (max-width: 480px) {
  .mobile-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
  
  .mobile-form :deep(.el-form-item__label) {
    font-size: 13px;
  }
  
  .mobile-form :deep(.el-input__inner),
  .mobile-form :deep(.el-textarea__inner) {
    font-size: 16px;
    padding: 10px;
  }
  
  .action-buttons {
    gap: 6px;
  }
}

/* 表单验证错误样式优化 */
.mobile-form :deep(.el-form-item.is-error .el-input__inner),
.mobile-form :deep(.el-form-item.is-error .el-textarea__inner) {
  border-color: #f56c6c;
}

.mobile-form :deep(.el-form-item__error) {
  font-size: 12px;
  color: #f56c6c;
  padding-top: 4px;
}

/* 焦点状态优化 */
.mobile-form :deep(.el-input__inner:focus),
.mobile-form :deep(.el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}
</style>
