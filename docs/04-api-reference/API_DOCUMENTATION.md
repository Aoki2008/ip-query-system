# 📚 IP查询系统 API 文档

## 📋 API概览

**基础URL**: `http://localhost:8000` (开发环境) / `https://your-domain.com` (生产环境)  
**API版本**: v1  
**认证方式**: JWT Bearer Token (管理接口)  
**数据格式**: JSON  
**字符编码**: UTF-8  

## 🔗 快速导航

- [🌐 公共API接口](#公共api接口)
- [🔐 管理API接口](#管理api接口)
- [📊 数据模型](#数据模型)
- [⚠️ 错误处理](#错误处理)
- [🔧 使用示例](#使用示例)

---

## 🌐 公共API接口

### 1. 系统健康检查

**接口**: `GET /health`  
**描述**: 检查系统运行状态  
**认证**: 无需认证  

#### 请求示例
```bash
curl -X GET "http://localhost:8000/health"
```

#### 响应示例
```json
{
  "status": "healthy",
  "timestamp": "2025-07-31T14:30:00Z",
  "version": "4.2.0",
  "uptime": "2 days, 3 hours, 45 minutes"
}
```

### 2. 单个IP查询

**接口**: `GET /api/query`
**描述**: 查询单个IP地址的详细信息
**认证**: 无需认证

#### 查询参数
| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|-------|------|
| ip | string | 是 | - | 要查询的IP地址 |
| db_type | string | 否 | auto | 数据库类型 (auto/city/country/asn) |
| lang | string | 否 | zh-CN | 语言 (zh-CN/en/ja) |
| format | string | 否 | json | 响应格式 (json/xml/csv) |

#### 请求示例
```bash
# 基础查询
curl -X GET "http://localhost:8000/api/query?ip=8.8.8.8"

# 指定数据库类型和语言
curl -X GET "http://localhost:8000/api/query?ip=8.8.8.8&db_type=city&lang=en"

# XML格式响应
curl -X GET "http://localhost:8000/api/query?ip=8.8.8.8&format=xml"
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "ip": "8.8.8.8",
    "country": "美国",
    "country_code": "US",
    "region": "加利福尼亚州",
    "city": "山景城",
    "latitude": 37.4056,
    "longitude": -122.0775,
    "timezone": "America/Los_Angeles",
    "isp": "Google LLC",
    "organization": "Google Public DNS",
    "asn": "AS15169",
    "is_proxy": false,
    "is_satellite": false,
    "accuracy_radius": 1000
  },
  "query_time": "2025-07-31T14:30:00Z",
  "response_time_ms": 15,
  "database_info": {
    "type": "city",
    "version": "2024.01",
    "build_date": "2024-01-15"
  }
}
```

### 3. 批量IP查询

**接口**: `POST /api/query/batch`  
**描述**: 批量查询多个IP地址  
**认证**: 无需认证  
**限制**: 单次最多100个IP  

#### 请求体
```json
{
  "ips": ["8.8.8.8", "1.1.1.1", "114.114.114.114"],
  "db_type": "city",
  "lang": "zh-CN",
  "include_details": true
}
```

#### 请求示例
```bash
curl -X POST "http://localhost:8000/api/query/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "ips": ["8.8.8.8", "1.1.1.1"],
    "db_type": "city",
    "lang": "zh-CN"
  }'
```

#### 响应示例
```json
{
  "success": true,
  "total": 2,
  "processed": 2,
  "failed": 0,
  "results": [
    {
      "ip": "8.8.8.8",
      "success": true,
      "data": {
        "country": "美国",
        "city": "山景城",
        "isp": "Google LLC"
      }
    },
    {
      "ip": "1.1.1.1",
      "success": true,
      "data": {
        "country": "美国",
        "city": "旧金山",
        "isp": "Cloudflare"
      }
    }
  ],
  "query_time": "2025-07-31T14:30:00Z",
  "response_time_ms": 45
}
```

### 4. IP地址验证

**接口**: `GET /api/validate/{ip}`  
**描述**: 验证IP地址格式是否正确  
**认证**: 无需认证  

#### 请求示例
```bash
curl -X GET "http://localhost:8000/api/validate/8.8.8.8"
```

#### 响应示例
```json
{
  "ip": "8.8.8.8",
  "valid": true,
  "type": "ipv4",
  "is_private": false,
  "is_loopback": false,
  "is_multicast": false,
  "is_reserved": false
}
```

### 5. 数据库信息查询

**接口**: `GET /api/database/info`  
**描述**: 获取可用数据库信息  
**认证**: 无需认证  

#### 请求示例
```bash
curl -X GET "http://localhost:8000/api/database/info"
```

#### 响应示例
```json
{
  "databases": [
    {
      "type": "city",
      "name": "GeoLite2-City",
      "version": "2024.01.15",
      "description": "城市级IP地理位置数据库",
      "record_count": 3500000,
      "last_updated": "2024-01-15T00:00:00Z",
      "file_size": "65MB"
    },
    {
      "type": "country",
      "name": "GeoLite2-Country", 
      "version": "2024.01.15",
      "description": "国家级IP地理位置数据库",
      "record_count": 400000,
      "last_updated": "2024-01-15T00:00:00Z",
      "file_size": "5MB"
    }
  ],
  "total_databases": 2,
  "default_database": "city"
}
```

---

## 🔐 管理API接口

### 认证说明

管理接口需要JWT认证，请在请求头中包含：
```
Authorization: Bearer <your_jwt_token>
```

### 1. 管理员登录

**接口**: `POST /admin/auth/login`  
**描述**: 管理员登录获取JWT令牌  
**认证**: 无需认证  

#### 请求体
```json
{
  "username": "admin",
  "password": "your_password"
}
```

#### 请求示例
```bash
curl -X POST "http://localhost:8000/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

#### 响应示例
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user_info": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "last_login": "2025-07-31T14:30:00Z"
  }
}
```

### 2. 查询历史记录

**接口**: `GET /admin/queries`  
**描述**: 获取查询历史记录  
**认证**: 需要JWT认证  

#### 查询参数
| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|-------|------|
| page | integer | 否 | 1 | 页码 |
| size | integer | 否 | 20 | 每页数量 |
| start_date | string | 否 | - | 开始日期 (YYYY-MM-DD) |
| end_date | string | 否 | - | 结束日期 (YYYY-MM-DD) |
| ip | string | 否 | - | 筛选IP地址 |

#### 请求示例
```bash
curl -X GET "http://localhost:8000/admin/queries?page=1&size=10" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "total": 1250,
    "page": 1,
    "size": 10,
    "pages": 125,
    "items": [
      {
        "id": 1250,
        "ip": "8.8.8.8",
        "query_time": "2025-07-31T14:30:00Z",
        "response_time_ms": 15,
        "database_type": "city",
        "client_ip": "192.168.1.100",
        "user_agent": "curl/7.68.0",
        "success": true
      }
    ]
  }
}
```

### 3. 系统统计信息

**接口**: `GET /admin/stats`  
**描述**: 获取系统统计信息  
**认证**: 需要JWT认证  

#### 请求示例
```bash
curl -X GET "http://localhost:8000/admin/stats" \
  -H "Authorization: Bearer <your_jwt_token>"
```

#### 响应示例
```json
{
  "success": true,
  "data": {
    "total_queries": 125000,
    "queries_today": 1250,
    "queries_this_month": 35000,
    "average_response_time": 18.5,
    "success_rate": 99.8,
    "top_queried_ips": [
      {"ip": "8.8.8.8", "count": 150},
      {"ip": "1.1.1.1", "count": 120}
    ],
    "database_usage": {
      "city": 85.2,
      "country": 12.8,
      "asn": 2.0
    },
    "system_info": {
      "uptime": "2 days, 3 hours",
      "memory_usage": "45.2%",
      "cpu_usage": "12.5%",
      "disk_usage": "68.3%"
    }
  }
}
```

### 4. 数据库管理

**接口**: `POST /admin/database/update`  
**描述**: 更新数据库文件  
**认证**: 需要JWT认证  

#### 请求体
```json
{
  "database_type": "city",
  "auto_backup": true,
  "force_update": false
}
```

#### 请求示例
```bash
curl -X POST "http://localhost:8000/admin/database/update" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "database_type": "city",
    "auto_backup": true
  }'
```

#### 响应示例
```json
{
  "success": true,
  "message": "数据库更新成功",
  "data": {
    "database_type": "city",
    "old_version": "2024.01.01",
    "new_version": "2024.01.15",
    "update_time": "2025-07-31T14:30:00Z",
    "backup_created": true,
    "backup_path": "/backups/city_2024.01.01.mmdb"
  }
}
```

---

## 📊 数据模型

### IP查询结果模型

```json
{
  "ip": "string",                    // IP地址
  "country": "string",               // 国家名称
  "country_code": "string",          // 国家代码 (ISO 3166-1)
  "region": "string",                // 地区/州/省
  "city": "string",                  // 城市
  "latitude": "number",              // 纬度
  "longitude": "number",             // 经度
  "timezone": "string",              // 时区
  "isp": "string",                   // ISP提供商
  "organization": "string",          // 组织名称
  "asn": "string",                   // 自治系统号
  "is_proxy": "boolean",             // 是否为代理
  "is_satellite": "boolean",         // 是否为卫星连接
  "accuracy_radius": "number"        // 精度半径(公里)
}
```

### 错误响应模型

```json
{
  "error": true,
  "error_type": "string",            // 错误类型
  "status_code": "number",           // HTTP状态码
  "message": "string",               // 错误消息
  "user_message": "string",          // 用户友好消息
  "timestamp": "string",             // 时间戳
  "request_id": "string"             // 请求ID
}
```

---

## ⚠️ 错误处理

### HTTP状态码

| 状态码 | 含义 | 描述 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权，需要登录 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求频率过高 |
| 500 | Internal Server Error | 服务器内部错误 |

### 错误响应示例

```json
{
  "error": true,
  "error_type": "validation_error",
  "status_code": 422,
  "message": "无效的IP地址格式",
  "user_message": "请输入有效的IP地址",
  "timestamp": "2025-07-31T14:30:00Z",
  "request_id": "req_12345678"
}
```

---

## 🔧 使用示例

### JavaScript/Node.js

```javascript
// 单个IP查询
async function queryIP(ip) {
  try {
    const response = await fetch(`http://localhost:8000/api/query?ip=${ip}`);
    const data = await response.json();

    if (data.success) {
      console.log('查询结果:', data.data);
      return data.data;
    } else {
      console.error('查询失败:', data.message);
    }
  } catch (error) {
    console.error('网络错误:', error);
  }
}

// 批量查询
async function batchQuery(ips) {
  try {
    const response = await fetch('http://localhost:8000/api/batch-query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ips: ips,
        db_type: 'city',
        lang: 'zh-CN'
      })
    });

    const data = await response.json();
    return data.results;
  } catch (error) {
    console.error('批量查询失败:', error);
  }
}

// 使用示例
queryIP('8.8.8.8');
batchQuery(['8.8.8.8', '1.1.1.1']);
```

### Python

```python
import requests
import json

class IPQueryClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def query_ip(self, ip, db_type="auto", lang="zh-CN"):
        """查询单个IP"""
        url = f"{self.base_url}/api/query"
        params = {"ip": ip, "db_type": db_type, "lang": lang}

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"查询失败: {e}")
            return None

    def batch_query(self, ips, db_type="city", lang="zh-CN"):
        """批量查询IP"""
        url = f"{self.base_url}/api/batch-query"
        data = {
            "ips": ips,
            "db_type": db_type,
            "lang": lang
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"批量查询失败: {e}")
            return None

# 使用示例
client = IPQueryClient()

# 单个查询
result = client.query_ip("8.8.8.8")
if result and result.get("success"):
    print("查询结果:", result["data"])

# 批量查询
results = client.batch_query(["8.8.8.8", "1.1.1.1"])
if results and results.get("success"):
    for item in results["results"]:
        print(f"IP: {item['ip']}, 位置: {item['data']['city']}")
```

### PHP

```php
<?php
class IPQueryClient {
    private $baseUrl;
    
    public function __construct($baseUrl = "http://localhost:8000") {
        $this->baseUrl = $baseUrl;
    }
    
    public function queryIP($ip, $dbType = "auto", $lang = "zh-CN") {
        $url = $this->baseUrl . "/api/query/" . urlencode($ip);
        $params = http_build_query([
            'db_type' => $dbType,
            'lang' => $lang
        ]);
        
        $response = file_get_contents($url . "?" . $params);
        return json_decode($response, true);
    }
    
    public function batchQuery($ips, $dbType = "city", $lang = "zh-CN") {
        $url = $this->baseUrl . "/api/query/batch";
        $data = json_encode([
            'ips' => $ips,
            'db_type' => $dbType,
            'lang' => $lang
        ]);
        
        $context = stream_context_create([
            'http' => [
                'method' => 'POST',
                'header' => 'Content-Type: application/json',
                'content' => $data
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        return json_decode($response, true);
    }
}

// 使用示例
$client = new IPQueryClient();

// 单个查询
$result = $client->queryIP("8.8.8.8");
if ($result['success']) {
    echo "查询结果: " . json_encode($result['data'], JSON_UNESCAPED_UNICODE);
}

// 批量查询
$results = $client->batchQuery(["8.8.8.8", "1.1.1.1"]);
if ($results['success']) {
    foreach ($results['results'] as $item) {
        echo "IP: " . $item['ip'] . ", 城市: " . $item['data']['city'] . "\n";
    }
}
?>
```

---

## 📝 更新日志

### v4.2.0 (2025-07-31)
- ✅ 完善API文档和使用示例
- ✅ 添加多语言支持
- ✅ 增强错误处理和响应格式
- ✅ 提供多种编程语言的SDK示例

### v4.1.0 (2025-07-30)
- ✅ 实施全面安全加固
- ✅ 添加JWT认证和权限控制
- ✅ 优化查询性能和响应时间

---

## 📞 技术支持

如有问题或建议，请联系：
- **GitHub**: https://github.com/Aoki2008/ip-query-system
- **Issues**: https://github.com/Aoki2008/ip-query-system/issues
- **文档**: https://github.com/Aoki2008/ip-query-system/docs

---

*最后更新: 2025-07-31 | 版本: v4.2.0*
