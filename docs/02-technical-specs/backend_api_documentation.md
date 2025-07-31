# 管理后台后端API文档

## 📋 概述

管理后台后端API基于FastAPI构建，提供完整的管理功能接口，包括认证、权限、监控、分析、数据管理等功能。

## 🔐 认证方式

所有管理后台API都需要JWT令牌认证，在请求头中添加：
```
Authorization: Bearer <access_token>
```

## 📡 API接口列表

### 1. 管理员认证API (`/api/admin/auth`)

#### 登录
- **POST** `/api/admin/auth/login`
- **描述**: 管理员登录获取访问令牌
- **请求体**: 
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **响应**: 
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```

#### 获取管理员信息
- **GET** `/api/admin/auth/profile`
- **描述**: 获取当前登录管理员的信息
- **响应**: 
  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "super_admin",
    "is_active": true,
    "created_at": "2025-07-30T10:00:00Z"
  }
  ```

#### 注销
- **POST** `/api/admin/auth/logout`
- **描述**: 管理员注销，使令牌失效

#### 刷新令牌
- **POST** `/api/admin/auth/refresh`
- **描述**: 刷新访问令牌

### 2. 权限管理API (`/api/admin/permissions`)

#### 权限列表
- **GET** `/api/admin/permissions/permissions`
- **描述**: 获取系统权限列表
- **响应**: 返回27个系统权限的数组

#### 角色列表
- **GET** `/api/admin/permissions/roles`
- **描述**: 获取系统角色列表
- **响应**: 返回3个默认角色及其权限

#### 权限检查
- **POST** `/api/admin/permissions/check`
- **描述**: 检查用户是否具有特定权限
- **请求体**: 
  ```json
  {
    "resource": "system",
    "action": "read"
  }
  ```

#### 权限矩阵
- **GET** `/api/admin/permissions/matrix`
- **描述**: 获取权限矩阵，展示所有角色的权限分配

### 3. 系统监控API (`/api/admin/monitoring`)

#### 系统状态
- **GET** `/api/admin/monitoring/status`
- **描述**: 获取实时系统状态
- **响应**: 
  ```json
  {
    "cpu_percent": 15.2,
    "memory_percent": 56.9,
    "memory_used_mb": 2048,
    "memory_total_mb": 8192,
    "disk_percent": 45.3,
    "uptime_seconds": 86400,
    "process_count": 156,
    "timestamp": "2025-07-30T12:00:00Z"
  }
  ```

#### 系统健康
- **GET** `/api/admin/monitoring/health`
- **描述**: 获取系统健康评估
- **响应**: 
  ```json
  {
    "overall_status": "good",
    "score": 95,
    "cpu_status": "healthy",
    "memory_status": "healthy",
    "disk_status": "healthy",
    "issues": []
  }
  ```

### 4. API分析API (`/api/admin/analytics`)

#### 分析健康检查
- **GET** `/api/admin/analytics/health`
- **描述**: 获取API分析系统状态
- **响应**: 
  ```json
  {
    "status": "healthy",
    "total_api_logs": 1250,
    "recent_logs_1h": 45,
    "timestamp": "2025-07-30T12:00:00Z"
  }
  ```

#### API统计
- **GET** `/api/admin/analytics/stats`
- **描述**: 获取API调用统计
- **参数**: `hours` (默认24) - 统计时间范围
- **响应**: 
  ```json
  {
    "total_requests": 1250,
    "avg_response_time": 125.5,
    "error_rate": 2.4,
    "requests_per_hour": 52.1,
    "top_endpoints": []
  }
  ```

#### 收集示例数据
- **POST** `/api/admin/analytics/collect`
- **描述**: 生成示例API调用记录用于测试

### 5. 数据管理API (`/api/admin/data`)

#### 数据仪表板
- **GET** `/api/admin/data/dashboard`
- **描述**: 获取数据管理仪表板信息
- **响应**: 
  ```json
  {
    "total_queries": 5000,
    "recent_queries_24h": 120,
    "data_quality_score": 85.5,
    "storage_usage_mb": 125.8,
    "last_cleanup": "2025-07-30T10:00:00Z",
    "status": "healthy"
  }
  ```

#### 数据健康检查
- **GET** `/api/admin/data/health`
- **描述**: 获取数据系统健康状态
- **响应**: 
  ```json
  {
    "status": "healthy",
    "total_records": 5000,
    "recent_records_1h": 25,
    "data_quality_score": 85.5,
    "timestamp": "2025-07-30T12:00:00Z"
  }
  ```

### 6. 日志分析API (`/api/admin/logs`)

#### 日志仪表板
- **GET** `/api/admin/logs/dashboard`
- **描述**: 获取日志分析仪表板
- **响应**: 
  ```json
  {
    "total_logs": 10000,
    "error_logs": 240,
    "error_rate": 2.4,
    "log_levels": {
      "info": 9760,
      "warning": 0,
      "error": 240,
      "critical": 0
    },
    "recent_activity": {
      "last_hour": 45,
      "last_24h": 1080
    },
    "status": "healthy"
  }
  ```

### 7. 告警通知API (`/api/admin/notifications`)

#### 通知仪表板
- **GET** `/api/admin/notifications/dashboard`
- **描述**: 获取告警通知系统仪表板

#### 通知渠道管理
- **GET** `/api/admin/notifications/channels`
- **POST** `/api/admin/notifications/channels`
- **PUT** `/api/admin/notifications/channels/{id}`
- **DELETE** `/api/admin/notifications/channels/{id}`

#### 告警规则管理
- **GET** `/api/admin/notifications/rules`
- **POST** `/api/admin/notifications/rules`
- **PUT** `/api/admin/notifications/rules/{id}`
- **DELETE** `/api/admin/notifications/rules/{id}`

### 8. 系统优化API (`/api/admin/optimization`)

#### 优化仪表板
- **GET** `/api/admin/optimization/dashboard`
- **描述**: 获取系统优化综合仪表板

#### 缓存管理
- **GET** `/api/admin/optimization/cache/stats`
- **POST** `/api/admin/optimization/cache/clear`
- **GET** `/api/admin/optimization/cache/health`

#### 性能监控
- **GET** `/api/admin/optimization/performance/stats`
- **GET** `/api/admin/optimization/performance/recommendations`

#### 安全管理
- **GET** `/api/admin/optimization/security/status`
- **GET** `/api/admin/optimization/security/threats`

## 🔧 技术特性

### 异步处理
- 基于FastAPI的异步框架
- 支持高并发请求处理
- 异步数据库操作

### 安全特性
- JWT令牌认证
- RBAC权限控制
- 请求频率限制
- CORS跨域保护

### 性能优化
- Redis缓存支持
- 数据库查询优化
- 响应时间监控
- 自动性能分析

### 错误处理
- 统一错误响应格式
- 详细错误日志记录
- 异常自动捕获
- 优雅降级处理

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

## 🚀 使用示例

### Python示例
```python
import requests

# 登录获取令牌
login_response = requests.post('http://localhost:8000/api/admin/auth/login', 
                              json={'username': 'admin', 'password': 'admin123'})
token = login_response.json()['access_token']

# 使用令牌访问API
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/admin/monitoring/status', 
                       headers=headers)
print(response.json())
```

### JavaScript示例
```javascript
// 登录获取令牌
const loginResponse = await fetch('http://localhost:8000/api/admin/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { access_token } = await loginResponse.json();

// 使用令牌访问API
const response = await fetch('http://localhost:8000/api/admin/monitoring/status', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const data = await response.json();
console.log(data);
```

## 📚 API文档

完整的交互式API文档可通过以下地址访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
