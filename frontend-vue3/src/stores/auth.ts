/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest } from '../types/auth'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const isPremium = computed(() => user.value?.is_premium || false)

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  // 设置令牌
  const setTokens = (accessToken: string, refreshTokenValue: string) => {
    token.value = accessToken
    refreshToken.value = refreshTokenValue
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshTokenValue)
  }

  // 清除令牌
  const clearTokens = () => {
    token.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // 用户注册
  const register = async (registerData: RegisterRequest): Promise<boolean> => {
    try {
      isLoading.value = true
      clearError()
      
      const response = await authService.register(registerData)
      
      if (response.success) {
        return true
      } else {
        error.value = response.message || '注册失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '注册过程中发生错误'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 用户登录
  const login = async (loginData: LoginRequest): Promise<boolean> => {
    try {
      isLoading.value = true
      clearError()
      
      const response = await authService.login(loginData)
      
      if (response.access_token) {
        setTokens(response.access_token, response.refresh_token)
        user.value = response.user
        return true
      } else {
        error.value = '登录失败'
        return false
      }
    } catch (err: any) {
      error.value = err.message || '登录过程中发生错误'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 用户登出
  const logout = async () => {
    try {
      if (token.value) {
        await authService.logout()
      }
    } catch (err) {
      console.warn('登出请求失败:', err)
    } finally {
      user.value = null
      clearTokens()
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async (): Promise<boolean> => {
    if (!token.value) return false

    try {
      isLoading.value = true
      const userData = await authService.getCurrentUser()
      
      if (userData) {
        user.value = userData
        return true
      } else {
        // 令牌可能已过期
        await logout()
        return false
      }
    } catch (err) {
      console.warn('获取用户信息失败:', err)
      await logout()
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 刷新令牌
  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken.value) return false

    try {
      const response = await authService.refreshToken(refreshToken.value)
      
      if (response.access_token) {
        setTokens(response.access_token, response.refresh_token)
        return true
      } else {
        await logout()
        return false
      }
    } catch (err) {
      console.warn('刷新令牌失败:', err)
      await logout()
      return false
    }
  }

  // 检查用户名可用性
  const checkUsernameAvailability = async (username: string): Promise<boolean> => {
    try {
      const response = await authService.checkUsername(username)
      return response.data?.available || false
    } catch (err) {
      return false
    }
  }

  // 检查邮箱可用性
  const checkEmailAvailability = async (email: string): Promise<boolean> => {
    try {
      const response = await authService.checkEmail(email)
      return response.data?.available || false
    } catch (err) {
      return false
    }
  }

  // 初始化认证状态
  const initAuth = async () => {
    if (token.value) {
      await fetchCurrentUser()
    }
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    error,
    
    // 计算属性
    isAuthenticated,
    isPremium,
    
    // 方法
    clearError,
    register,
    login,
    logout,
    fetchCurrentUser,
    refreshAccessToken,
    checkUsernameAvailability,
    checkEmailAvailability,
    initAuth
  }
})
