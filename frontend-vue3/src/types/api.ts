/**
 * API相关类型定义
 */

// 基础API响应类型
export interface BaseApiResponse {
  success: boolean
  error?: boolean
  message?: string
  error_code?: string
}

// IP查询结果类型
export interface IpQueryResult {
  ip: string
  country: string
  region: string
  city: string
  latitude: number
  longitude: number
  timezone: string
  isp: string
  error?: string
}

// 单个IP查询响应
export interface SingleIpResponse extends BaseApiResponse {
  data: IpQueryResult
}

// 批量IP查询响应
export interface BatchIpResponse extends BaseApiResponse {
  data: {
    total: number
    success_count: number
    results: IpQueryResult[]
  }
}

// 健康检查响应
export interface HealthResponse {
  status: string
  message: string
}

// API错误响应
export interface ApiErrorResponse extends BaseApiResponse {
  error: true
  message: string
  error_code: string
}

// 请求参数类型
export interface BatchIpRequest {
  ips: string[]
}

// 文件导入导出相关类型
export interface ImportResult {
  success: boolean
  total: number
  valid: number
  invalid: number
  ips: string[]
  errors?: string[]
}

export interface ExportOptions {
  format: 'csv' | 'json' | 'excel'
  filename?: string
  data: IpQueryResult[]
}

// 查询历史类型
export interface QueryHistoryItem extends IpQueryResult {
  timestamp: number
  query_type: 'single' | 'batch'
}

// 应用状态类型
export interface AppState {
  loading: boolean
  error: string | null
  currentIp: IpQueryResult | null
  queryResults: IpQueryResult[]
  queryHistory: QueryHistoryItem[]
}

// 主题类型
export type Theme = 'light' | 'dark'

// 导航菜单类型
export interface MenuItem {
  id: string
  label: string
  icon: string
  path: string
  children?: MenuItem[]
}

// 表单验证类型
export interface ValidationResult {
  valid: boolean
  errors: string[]
}

// 文件上传类型
export interface FileUploadResult {
  success: boolean
  filename: string
  size: number
  content: string
  error?: string
}
