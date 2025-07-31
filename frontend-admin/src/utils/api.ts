import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000, // 增加超时时间到30秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_refresh_token')

      // 只有在不是登录页面时才显示错误消息和跳转
      if (window.location.pathname !== '/login') {
        ElMessage.error('登录已过期，请重新登录')

        // 延迟跳转，避免在响应拦截器中直接操作路由
        setTimeout(() => {
          window.location.href = '/login'
        }, 1000)
      }

      return Promise.reject(error)
    }

    // 其他错误处理
    const message = error.response?.data?.detail || error.response?.data?.message || error.message || '请求失败'
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

export default api
