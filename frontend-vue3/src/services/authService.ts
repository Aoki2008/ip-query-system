/**
 * 认证服务
 */
import axios, { type AxiosResponse } from 'axios'
import type {
  User,
  LoginRequest,
  RegisterRequest,
  LoginResponse,
  AuthResponse,
  PasswordResetRequest
} from '../types/auth'

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api'

// 创建axios实例
const authApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证令牌
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理认证错误
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 如果是401错误且不是刷新令牌请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken && !originalRequest.url?.includes('/auth/refresh')) {
          // 避免循环调用
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          })

          if (response.data.access_token) {
            localStorage.setItem('access_token', response.data.access_token)
            localStorage.setItem('refresh_token', response.data.refresh_token)

            // 重试原始请求
            originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
            return authApi(originalRequest)
          }
        }
      } catch (refreshError) {
        // 刷新失败，清除令牌
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        // 不自动跳转，让路由守卫处理
      }
    }

    return Promise.reject(error)
  }
)

export const authService = {
  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      const response: AxiosResponse<AuthResponse> = await authApi.post('/auth/register', data)
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '注册失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  },

  /**
   * 用户登录
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      const response: AxiosResponse<LoginResponse> = await authApi.post('/auth/login', data)
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '登录失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  },

  /**
   * 用户登出
   */
  async logout(): Promise<AuthResponse> {
    try {
      const response: AxiosResponse<AuthResponse> = await authApi.post('/auth/logout')
      return response.data
    } catch (error: any) {
      // 登出失败不抛出错误，因为本地清理更重要
      console.warn('登出请求失败:', error)
      return { success: true, message: '已登出' }
    }
  },

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response: AxiosResponse<User> = await authApi.get('/auth/me')
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '获取用户信息失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  },

  /**
   * 刷新访问令牌
   */
  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    try {
      const response: AxiosResponse<LoginResponse> = await authApi.post('/auth/refresh', {
        refresh_token: refreshToken
      })
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '刷新令牌失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  },

  /**
   * 检查用户名可用性
   */
  async checkUsername(username: string): Promise<AuthResponse> {
    try {
      const response: AxiosResponse<AuthResponse> = await authApi.get(`/auth/check-username/${username}`)
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '检查用户名失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  },

  /**
   * 检查邮箱可用性
   */
  async checkEmail(email: string): Promise<AuthResponse> {
    try {
      const response: AxiosResponse<AuthResponse> = await authApi.get(`/auth/check-email/${email}`)
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '检查邮箱失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  },

  /**
   * 请求密码重置
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<AuthResponse> {
    try {
      const response: AxiosResponse<AuthResponse> = await authApi.post('/auth/password-reset', data)
      return response.data
    } catch (error: any) {
      if (error.response?.data) {
        throw new Error(error.response.data.detail || error.response.data.message || '密码重置请求失败')
      }
      throw new Error('网络错误，请稍后重试')
    }
  }
}

export default authService
