import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  last_login: string | null
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('admin_refresh_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  // API实例已经在拦截器中处理了token

  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      const response = await api.post<LoginResponse>('/admin/auth/login', {
        username,
        password
      })

      const { access_token, refresh_token, user: userData } = response.data

      token.value = access_token
      refreshToken.value = refresh_token
      user.value = userData

      localStorage.setItem('admin_token', access_token)
      localStorage.setItem('admin_refresh_token', refresh_token)

      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await api.post('/admin/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = null
      refreshToken.value = null
      user.value = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_refresh_token')
    }
  }

  const getProfile = async () => {
    try {
      const response = await api.get<User>('/admin/auth/profile')
      user.value = response.data
      return true
    } catch (error) {
      console.error('Get profile failed:', error)
      return false
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) return false

    try {
      const response = await api.post('/admin/auth/refresh', {
        refresh_token: refreshToken.value
      })

      const { access_token } = response.data
      token.value = access_token
      localStorage.setItem('admin_token', access_token)

      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      await logout()
      return false
    }
  }

  return {
    token,
    refreshToken,
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    getProfile,
    refreshAccessToken
  }
})
