<template>
  <div class="register-form">
    <div class="form-header">
      <h2>用户注册</h2>
      <p>创建您的账户，开始使用IP查询工具</p>
    </div>

    <form @submit.prevent="handleSubmit" class="auth-form">
      <!-- 用户名输入 -->
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          placeholder="请输入用户名（3-50字符）"
          :class="{ 'error': errors.username, 'success': validations.username }"
          @blur="validateField('username')"
          @input="debounceCheckUsername"
        />
        <span v-if="errors.username" class="error-message">
          {{ errors.username }}
        </span>
        <span v-else-if="validations.username" class="success-message">
          用户名可用
        </span>
      </div>

      <!-- 邮箱输入 -->
      <div class="form-group">
        <label for="email">邮箱地址</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          placeholder="请输入邮箱地址"
          :class="{ 'error': errors.email, 'success': validations.email }"
          @blur="validateField('email')"
          @input="debounceCheckEmail"
        />
        <span v-if="errors.email" class="error-message">
          {{ errors.email }}
        </span>
        <span v-else-if="validations.email" class="success-message">
          邮箱可用
        </span>
      </div>

      <!-- 真实姓名输入 -->
      <div class="form-group">
        <label for="full_name">真实姓名（可选）</label>
        <input
          id="full_name"
          v-model="form.full_name"
          type="text"
          placeholder="请输入真实姓名"
          @blur="validateField('full_name')"
        />
      </div>

      <!-- 密码输入 -->
      <div class="form-group">
        <label for="password">密码</label>
        <div class="password-input">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码（至少6个字符）"
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
        <div class="password-strength">
          <div class="strength-bar">
            <div 
              class="strength-fill" 
              :class="passwordStrength.class"
              :style="{ width: passwordStrength.width }"
            ></div>
          </div>
          <span class="strength-text">{{ passwordStrength.text }}</span>
        </div>
      </div>

      <!-- 确认密码输入 -->
      <div class="form-group">
        <label for="confirm_password">确认密码</label>
        <div class="password-input">
          <input
            id="confirm_password"
            v-model="form.confirm_password"
            :type="showConfirmPassword ? 'text' : 'password'"
            placeholder="请再次输入密码"
            :class="{ 'error': errors.confirm_password }"
            @blur="validateField('confirm_password')"
          />
          <button
            type="button"
            class="password-toggle"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
          </button>
        </div>
        <span v-if="errors.confirm_password" class="error-message">
          {{ errors.confirm_password }}
        </span>
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
        {{ authStore.isLoading ? '注册中...' : '注册账户' }}
      </button>
    </form>

    <!-- 底部链接 -->
    <div class="form-footer">
      <p>
        已有账户？
        <a href="#" @click="$emit('switch-to-login')">立即登录</a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import type { RegisterRequest } from '../../types/auth'

// 事件定义
const emit = defineEmits<{
  'switch-to-login': []
}>()

// 状态
const authStore = useAuthStore()

// 表单数据
const form = ref<RegisterRequest>({
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  full_name: ''
})

// 表单状态
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const errors = ref<Record<string, string>>({})
const validations = ref<Record<string, boolean>>({})
const touched = ref<Record<string, boolean>>({})

// 防抖定时器
let usernameTimer: number
let emailTimer: number

// 密码强度计算
const passwordStrength = computed(() => {
  const password = form.value.password
  if (!password) return { width: '0%', class: '', text: '' }

  let score = 0
  if (password.length >= 6) score += 1
  if (password.length >= 8) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[a-z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^A-Za-z0-9]/.test(password)) score += 1

  if (score <= 2) return { width: '33%', class: 'weak', text: '弱' }
  if (score <= 4) return { width: '66%', class: 'medium', text: '中等' }
  return { width: '100%', class: 'strong', text: '强' }
})

// 验证规则
const validateField = async (field: string) => {
  touched.value[field] = true
  errors.value[field] = ''

  switch (field) {
    case 'username':
      if (!form.value.username) {
        errors.value[field] = '请输入用户名'
      } else if (form.value.username.length < 3) {
        errors.value[field] = '用户名至少3个字符'
      } else if (form.value.username.length > 50) {
        errors.value[field] = '用户名最多50个字符'
      } else if (!/^[a-zA-Z0-9_-]+$/.test(form.value.username)) {
        errors.value[field] = '用户名只能包含字母、数字、下划线和连字符'
      }
      break
    
    case 'email':
      if (!form.value.email) {
        errors.value[field] = '请输入邮箱地址'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
        errors.value[field] = '请输入有效的邮箱地址'
      }
      break
    
    case 'password':
      if (!form.value.password) {
        errors.value[field] = '请输入密码'
      } else if (form.value.password.length < 6) {
        errors.value[field] = '密码至少6个字符'
      }
      // 重新验证确认密码
      if (form.value.confirm_password) {
        validateField('confirm_password')
      }
      break
    
    case 'confirm_password':
      if (!form.value.confirm_password) {
        errors.value[field] = '请确认密码'
      } else if (form.value.password !== form.value.confirm_password) {
        errors.value[field] = '两次输入的密码不一致'
      }
      break
  }
}

// 防抖检查用户名
const debounceCheckUsername = () => {
  clearTimeout(usernameTimer)
  validations.value.username = false
  
  if (form.value.username && !errors.value.username) {
    usernameTimer = setTimeout(async () => {
      try {
        const available = await authStore.checkUsernameAvailability(form.value.username)
        if (available) {
          validations.value.username = true
        } else {
          errors.value.username = '用户名已被使用'
        }
      } catch (error) {
        console.warn('检查用户名失败:', error)
      }
    }, 500)
  }
}

// 防抖检查邮箱
const debounceCheckEmail = () => {
  clearTimeout(emailTimer)
  validations.value.email = false
  
  if (form.value.email && !errors.value.email) {
    emailTimer = setTimeout(async () => {
      try {
        const available = await authStore.checkEmailAvailability(form.value.email)
        if (available) {
          validations.value.email = true
        } else {
          errors.value.email = '邮箱已被注册'
        }
      } catch (error) {
        console.warn('检查邮箱失败:', error)
      }
    }, 500)
  }
}

// 表单验证 - 简化逻辑，只检查必填字段
const isFormValid = computed(() => {
  return form.value.username.trim().length > 0 &&
         form.value.email.trim().length > 0 &&
         form.value.password.trim().length > 0 &&
         form.value.confirm_password.trim().length > 0 &&
         form.value.password === form.value.confirm_password
})

// 提交表单
const handleSubmit = async () => {
  // 验证所有字段
  await Promise.all([
    validateField('username'),
    validateField('email'),
    validateField('password'),
    validateField('confirm_password')
  ])

  if (!isFormValid.value) return

  // 清除之前的错误
  authStore.clearError()

  // 执行注册
  const success = await authStore.register(form.value)
  
  if (success) {
    // 注册成功，切换到登录表单
    emit('switch-to-login')
  }
}

// 组件挂载时清除错误
onMounted(() => {
  authStore.clearError()
})
</script>

<style scoped>
/* 继承LoginForm的样式 */
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-lg);
}

/* 密码强度指示器 */
.password-strength {
  margin-top: 0.5rem;
}

.strength-bar {
  width: 100%;
  height: 4px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  background: var(--error-color);
}

.strength-fill.medium {
  background: var(--warning-color);
}

.strength-fill.strong {
  background: var(--success-color);
}

.strength-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
  display: block;
}

.success-message {
  color: var(--success-color);
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

/* 继承LoginForm的基础样式 */
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

.form-group input.success {
  border-color: var(--success-color);
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
