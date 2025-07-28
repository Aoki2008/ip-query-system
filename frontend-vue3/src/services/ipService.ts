import axios, { type AxiosResponse } from 'axios'
import type {
  SingleIpResponse,
  BatchIpResponse,
  HealthResponse,
  IpQueryResult,
  BatchIpRequest,
  ApiErrorResponse
} from '../types/api'

// API配置
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 10000
}

// 创建axios实例
const apiClient = axios.create(API_CONFIG)

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('收到响应:', response.data)
    return response
  },
  (error) => {
    console.error('响应错误:', error)
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response
      const errorData = data as ApiErrorResponse
      throw new Error(`API错误 ${status}: ${errorData.message || '未知错误'}`)
    } else if (error.request) {
      // 请求发送失败
      throw new Error('网络连接失败，请检查网络设置')
    } else {
      // 其他错误
      throw new Error('请求配置错误')
    }
  }
)

// IP查询服务
export const ipService = {
  // 健康检查
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await apiClient.get<HealthResponse>('/health')
      return response.data
    } catch (error) {
      console.error('健康检查失败:', error)
      throw error
    }
  },

  // 单个IP查询
  async queryIp(ip: string): Promise<IpQueryResult> {
    try {
      const response = await apiClient.get<SingleIpResponse>(`/query-ip?ip=${encodeURIComponent(ip)}`)
      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.message || 'IP查询失败')
      }
    } catch (error) {
      console.error('IP查询失败:', error)
      throw error
    }
  },

  // 批量IP查询
  async queryBatch(ips: string[]): Promise<IpQueryResult[]> {
    try {
      const requestData: BatchIpRequest = { ips }
      const response = await apiClient.post<BatchIpResponse>('/query-batch', requestData)

      if (response.data.success && response.data.data) {
        return response.data.data.results
      } else {
        throw new Error(response.data.message || '批量查询失败')
      }
    } catch (error) {
      console.error('批量查询失败:', error)
      throw error
    }
  },

  // 获取当前IP
  async getCurrentIp(): Promise<IpQueryResult> {
    try {
      // 使用第三方服务获取当前IP
      const response = await axios.get<{ ip: string }>('https://api.ipify.org?format=json')
      const currentIp = response.data.ip

      // 查询当前IP的详细信息
      const ipInfo = await this.queryIp(currentIp)
      return ipInfo
    } catch (error) {
      console.error('获取当前IP失败:', error)
      throw error
    }
  }
}

// 文件处理服务
export const fileService = {
  // 读取文件内容
  readFile(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        resolve(content)
      }
      reader.onerror = () => {
        reject(new Error('文件读取失败'))
      }
      reader.readAsText(file, 'UTF-8')
    })
  },

  // 解析IP列表
  parseIpList(content: string): string[] {
    const lines = content.split('\n')
    const ips: string[] = []
    
    for (const line of lines) {
      const trimmed = line.trim()
      if (trimmed && this.isValidIp(trimmed)) {
        ips.push(trimmed)
      }
    }
    
    return ips
  },

  // 验证IP地址格式
  isValidIp(ip: string): boolean {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    return ipRegex.test(ip)
  },

  // 导出为CSV
  exportToCsv(data: any[], filename: string = 'ip_query_results.csv') {
    const headers = ['IP地址', '国家', '地区', '城市', 'ISP', '纬度', '经度', '时区']
    const csvContent = [
      headers.join(','),
      ...data.map(item => [
        item.ip,
        item.country || '',
        item.region || '',
        item.city || '',
        item.isp || '',
        item.latitude || '',
        item.longitude || '',
        item.timezone || ''
      ].map(field => `"${field}"`).join(','))
    ].join('\n')

    this.downloadFile(csvContent, filename, 'text/csv')
  },

  // 导出为JSON
  exportToJson(data: any[], filename: string = 'ip_query_results.json') {
    const jsonContent = JSON.stringify(data, null, 2)
    this.downloadFile(jsonContent, filename, 'application/json')
  },

  // 下载文件
  downloadFile(content: string, filename: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}

// 本地类型定义已移至 types/api.ts
