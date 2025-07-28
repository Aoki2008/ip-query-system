# IP查询系统 API 文档

## 概述

IP查询系统提供RESTful API接口，支持单个IP查询、批量查询等功能。所有API都支持JSON格式的请求和响应。

## 基础信息

- **Base URL**: `https://api.example.com`
- **API版本**: v1
- **认证方式**: API Key
- **请求格式**: JSON
- **响应格式**: JSON

## 认证

### API Key认证

在请求头中包含您的API密钥：

```http
X-API-Key: your_api_key_here
```

或者作为查询参数：

```http
GET /api/ip/query?ip=8.8.8.8&api_key=your_api_key_here
```

### 获取API密钥

1. 注册账号：`POST /api/auth/register`
2. 登录获取token：`POST /api/auth/login`
3. 在用户中心创建API密钥

## 限流规则

| 用户类型 | 每分钟请求数 | 每日请求数 |
|---------|-------------|-----------|
| 游客    | 无限制       | 20        |
| 免费用户 | 60          | 1000      |
| 付费用户 | 600         | 10000     |

## API接口

### 1. 单个IP查询

查询单个IP地址的详细信息。

**请求**

```http
GET /api/ip/query?ip={ip_address}
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| ip  | string | 是 | 要查询的IP地址 |

**响应示例**

```json
{
  "success": true,
  "data": {
    "ip": "8.8.8.8",
    "country": "United States",
    "country_code": "US",
    "region": "California",
    "region_code": "CA",
    "city": "Mountain View",
    "postal_code": "94043",
    "latitude": 37.4056,
    "longitude": -122.0775,
    "timezone": "America/Los_Angeles",
    "isp": "Google LLC",
    "organization": "Google Public DNS",
    "asn": 15169,
    "asn_organization": "GOOGLE",
    "is_eu": false,
    "accuracy_radius": 1000
  },
  "cached": false,
  "response_time": 150
}
```

### 2. 批量IP查询

同时查询多个IP地址，最多支持100个。

**请求**

```http
POST /api/ip/batch
Content-Type: application/json

{
  "ips": ["8.8.8.8", "114.114.114.114", "1.1.1.1"]
}
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| ips | array | 是 | IP地址数组，最多100个 |

**响应示例**

```json
{
  "success": true,
  "data": [
    {
      "ip": "8.8.8.8",
      "success": true,
      "data": {
        "ip": "8.8.8.8",
        "country": "United States",
        "city": "Mountain View",
        "isp": "Google LLC"
      },
      "cached": false
    },
    {
      "ip": "114.114.114.114",
      "success": true,
      "data": {
        "ip": "114.114.114.114",
        "country": "China",
        "city": "Beijing",
        "isp": "China Telecom"
      },
      "cached": true
    }
  ],
  "summary": {
    "total": 2,
    "success": 2,
    "errors": 0
  },
  "response_time": 280
}
```

### 3. 获取统计信息

获取API密钥的使用统计信息。

**请求**

```http
GET /api/ip/stats?timeRange=24h
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| timeRange | string | 否 | 时间范围：1h, 24h, 7d, 30d |

**响应示例**

```json
{
  "success": true,
  "data": {
    "total_calls": 1250,
    "success_calls": 1200,
    "error_calls": 50,
    "avg_response_time": 180
  },
  "timeRange": "24h"
}
```

### 4. 用户认证

#### 注册

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

#### 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

#### 获取用户信息

```http
GET /api/auth/me
Authorization: Bearer {jwt_token}
```

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "code": "ERROR_CODE",
  "details": {}
}
```

### 常见错误代码

| 错误代码 | HTTP状态码 | 说明 |
|---------|-----------|------|
| MISSING_API_KEY | 401 | 缺少API密钥 |
| INVALID_API_KEY | 401 | 无效的API密钥 |
| API_KEY_DISABLED | 401 | API密钥已禁用 |
| RATE_LIMIT_EXCEEDED | 429 | 超出限流限制 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| QUERY_FAILED | 500 | IP查询失败 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## 响应头

所有API响应都包含以下头部信息：

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 2024-01-01T12:00:00Z
X-API-RateLimit-Day-Limit: 1000
X-API-RateLimit-Day-Remaining: 999
```

## SDK和示例代码

### cURL示例

```bash
# 单个IP查询
curl -X GET "https://api.example.com/api/ip/query?ip=8.8.8.8" \
  -H "X-API-Key: your_api_key_here"

# 批量查询
curl -X POST "https://api.example.com/api/ip/batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"ips": ["8.8.8.8", "114.114.114.114"]}'
```

### JavaScript示例

```javascript
// 使用fetch API
const response = await fetch('https://api.example.com/api/ip/query?ip=8.8.8.8', {
  headers: {
    'X-API-Key': 'your_api_key_here'
  }
});

const data = await response.json();
console.log(data);
```

### Python示例

```python
import requests

# 单个IP查询
response = requests.get(
    'https://api.example.com/api/ip/query',
    params={'ip': '8.8.8.8'},
    headers={'X-API-Key': 'your_api_key_here'}
)

data = response.json()
print(data)
```

### PHP示例

```php
<?php
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'https://api.example.com/api/ip/query?ip=8.8.8.8');
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'X-API-Key: your_api_key_here'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$data = json_decode($response, true);
curl_close($ch);

print_r($data);
?>
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持单个IP查询
- 支持批量IP查询
- 支持用户认证和API密钥管理

## 支持

如有问题，请联系：
- 邮箱：support@example.com
- 文档：https://docs.example.com
- GitHub：https://github.com/example/ip-query-system
