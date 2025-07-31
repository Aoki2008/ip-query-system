/**
 * 认证相关类型定义
 */

// 用户信息
export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_premium: boolean
  created_at: string
  updated_at: string
  last_login_at?: string
}

// 登录请求
export interface LoginRequest {
  username_or_email: string
  password: string
  remember_me?: boolean
}

// 注册请求
export interface RegisterRequest {
  username: string
  email: string
  password: string
  confirm_password: string
  full_name?: string
}

// 登录响应
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

// 刷新令牌请求
export interface RefreshTokenRequest {
  refresh_token: string
}

// 通用认证响应
export interface AuthResponse {
  success: boolean
  message: string
  data?: any
}

// 密码重置请求
export interface PasswordResetRequest {
  email: string
}

// 密码重置确认
export interface PasswordResetConfirm {
  token: string
  new_password: string
  confirm_password: string
}

// 用户权限
export interface UserPermissions {
  can_query_ip: boolean
  can_batch_query: boolean
  can_export_data: boolean
  can_use_api: boolean
  daily_query_limit: number
  monthly_query_limit: number
}

// 用户统计
export interface UserStats {
  total_queries: number
  queries_today: number
  queries_this_month: number
  success_rate: number
  avg_response_time: number
  most_queried_ips: Array<{
    ip: string
    count: number
  }>
  query_trend: Array<{
    date: string
    count: number
  }>
}

// 用户设置
export interface UserSettings {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  email_notifications: boolean
  history_retention_days: number
}

// 表单验证规则
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  message: string
  validator?: (value: any) => boolean | string
}

// 表单字段
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'checkbox'
  placeholder?: string
  rules?: ValidationRule[]
  value?: any
}

// 认证表单状态
export interface AuthFormState {
  isLoading: boolean
  errors: Record<string, string>
  touched: Record<string, boolean>
  isValid: boolean
}
