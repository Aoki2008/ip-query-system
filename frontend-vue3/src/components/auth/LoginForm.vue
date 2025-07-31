<template>
  <div class="login-form">
    <div class="form-header">
      <h2>用户登录</h2>
      <p>登录您的账户以使用更多功能</p>
    </div>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <!-- 用户名/邮箱输入 -->
      <div class="form-group">
        <label for="username_or_email">用户名或邮箱</label>
        <input
          id="username_or_email"
          v-model="form.username_or_email"
          type="text"
          placeholder="请输入用户名或邮箱"
          :class="{ 'error': errors.username_or_email }"
          @blur="validateField('username_or_email')"
        />
        <span v-if="errors.username_or_email" class="error-message">
          {{ errors.username_or_email }}
        </span>
      </div>

      <!-- 密码输入 -->
      <div class="form-group">
        <label for="password">密码</label>
        <div class="password-input">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            :class="{ 'error': errors.password }"
            @blur="validateField('password')"
          />
          <button
            type="button"
            class="password-toggle"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>
        <span v-if="errors.password" class="error-message">
          {{ errors.password }}
        </span>
      </div>

      <!-- 记住我 -->
      <div class="form-group checkbox-group">
        <label class="checkbox-label">
          <input
            v-model="form.remember_me"
            type="checkbox"
          />
          <span class="checkmark"></span>
          记住我
        </label>
      </div>

      <!-- 错误信息 -->
      <div v-if="authStore.error" class="error-banner">
        {{ authStore.error }}
      </div>

      <!-- 提交按钮 -->
      <button
        type="submit"
        class="submit-btn"
        :disabled="authStore.isLoading || !isFormValid"
      >
        <span v-if="authStore.isLoading" class="loading-spinner"></span>
        {{ authStore.isLoading ? '登录中...' : '登录' }}
      </button>
    </form>

    <!-- 底部链接 -->
    <div class="form-footer">
      <p>
        还没有账户？
        <a href="#" @click="$emit('switch-to-register')">立即注册</a>
      </p>
      <p>
        <a href="#" @click="$emit('forgot-password')">忘记密码？</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import type { LoginRequest } from '../../types/auth'

// 事件定义
defineEmits<{
  'switch-to-register': []
  'forgot-password': []
}>()

// 路由和状态
const router = useRouter()
const authStore = useAuthStore()

// 表单数据
const form = ref<LoginRequest>({
  username_or_email: '',
  password: '',
  remember_me: false
})

// 表单状态
const showPassword = ref(false)
const errors = ref<Record<string, string>>({})
const touched = ref<Record<string, boolean>>({})

// 验证规则
const validateField = (field: string) => {
  touched.value[field] = true
  errors.value[field] = ''

  switch (field) {
    case 'username_or_email':
      if (!form.value.username_or_email) {
        errors.value[field] = '请输入用户名或邮箱'
      } else if (form.value.username_or_email.length < 3) {
        errors.value[field] = '用户名或邮箱至少3个字符'
      }
      break
    
    case 'password':
      if (!form.value.password) {
        errors.value[field] = '请输入密码'
      } else if (form.value.password.length < 6) {
        errors.value[field] = '密码至少6个字符'
      }
      break
  }
}

// 表单验证 - 简化逻辑，只检查必填字段
const isFormValid = computed(() => {
  return form.value.username_or_email.trim().length > 0 &&
         form.value.password.trim().length > 0
})

// 提交表单
const handleSubmit = async () => {
  // 验证所有字段
  Object.keys(form.value).forEach(field => {
    if (field !== 'remember_me') {
      validateField(field)
    }
  })

  if (!isFormValid.value) return

  // 清除之前的错误
  authStore.clearError()

  // 执行登录
  const success = await authStore.login(form.value)
  
  if (success) {
    // 登录成功，跳转到首页或之前的页面
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/')
  }
}

// 组件挂载时清除错误
onMounted(() => {
  authStore.clearError()
})
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-lg);
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.form-header p {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.75rem;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px var(--primary-color-alpha);
}

.form-group input.error {
  border-color: var(--error-color);
}

.password-input {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: var(--text-secondary);
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.error-message {
  color: var(--error-color);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.error-banner {
  padding: 0.75rem;
  background: var(--error-bg);
  color: var(--error-color);
  border-radius: 8px;
  font-size: 0.9rem;
  text-align: center;
}

.submit-btn {
  padding: 0.75rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.form-footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.form-footer p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.form-footer a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style>
