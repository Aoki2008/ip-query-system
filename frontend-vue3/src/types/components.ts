/**
 * Vue组件相关类型定义
 */

// 玻璃容器组件属性
export interface GlassContainerProps {
  variant?: 'card' | 'input' | 'button'
  animated?: boolean
}

// 导航组件状态
export interface NavigationState {
  toolsDropdownOpen: boolean
  helpDropdownOpen: boolean
  isMobile: boolean
}

// 主题切换组件状态
export interface ThemeToggleState {
  isDark: boolean
}

// 查询表单状态
export interface QueryFormState {
  activeTab: 'single' | 'batch' | 'history'
  singleIp: string
  batchIps: string
  loading: boolean
}

// 结果显示组件属性
export interface ResultsDisplayProps {
  results: IpQueryResult[]
  loading?: boolean
  showActions?: boolean
}

// 文件导入组件状态
export interface FileImportState {
  dragOver: boolean
  uploading: boolean
  progress: number
}

// 历史记录组件状态
export interface HistoryState {
  searchTerm: string
  sortBy: 'timestamp' | 'ip' | 'country'
  sortOrder: 'asc' | 'desc'
  filteredHistory: QueryHistoryItem[]
}

// 错误提示组件属性
export interface ErrorAlertProps {
  message: string
  type?: 'error' | 'warning' | 'info' | 'success'
  dismissible?: boolean
}

// 加载状态组件属性
export interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  text?: string
}

// 分页组件属性
export interface PaginationProps {
  currentPage: number
  totalPages: number
  pageSize: number
  totalItems: number
}

// 搜索框组件属性
export interface SearchBoxProps {
  placeholder?: string
  value: string
  loading?: boolean
}

// 统计卡片组件属性
export interface StatsCardProps {
  title: string
  value: string | number
  icon: string
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
}

// 表格组件属性
export interface DataTableProps {
  columns: TableColumn[]
  data: any[]
  loading?: boolean
  sortable?: boolean
  pagination?: boolean
}

export interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  formatter?: (value: any, row: any) => string
}

// 模态框组件属性
export interface ModalProps {
  visible: boolean
  title?: string
  width?: string
  closable?: boolean
  maskClosable?: boolean
}

// 下拉菜单组件属性
export interface DropdownProps {
  options: DropdownOption[]
  value?: string | number
  placeholder?: string
  disabled?: boolean
}

export interface DropdownOption {
  label: string
  value: string | number
  disabled?: boolean
}

// 表单项组件属性
export interface FormItemProps {
  label?: string
  required?: boolean
  error?: string
  help?: string
}

// 按钮组件属性
export interface ButtonProps {
  type?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
  size?: 'small' | 'medium' | 'large'
  loading?: boolean
  disabled?: boolean
  icon?: string
}

// 输入框组件属性
export interface InputProps {
  type?: 'text' | 'password' | 'email' | 'number' | 'textarea'
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  maxlength?: number
  rows?: number
}

import type { IpQueryResult, QueryHistoryItem } from './api'
