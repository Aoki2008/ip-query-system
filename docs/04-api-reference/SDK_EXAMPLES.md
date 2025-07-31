# 🛠️ IP查询系统 SDK 示例和集成指南

## 📋 概览

本文档提供了各种编程语言的SDK示例和集成指南，帮助开发者快速集成IP查询系统API。

## 🌐 支持的编程语言

- [JavaScript/Node.js](#javascript--nodejs)
- [Python](#python)
- [PHP](#php)
- [Java](#java)
- [C#/.NET](#c--net)
- [Go](#go)
- [Ruby](#ruby)
- [Swift](#swift)

---

## 🟨 JavaScript / Node.js

### 安装依赖

```bash
npm install axios
```

### 完整SDK实现

```javascript
// ip-query-client.js
const axios = require('axios');

class IPQueryClient {
    constructor(baseURL = 'http://localhost:8000', options = {}) {
        this.baseURL = baseURL;
        this.timeout = options.timeout || 10000;
        this.retries = options.retries || 3;
        
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'IPQueryClient-JS/1.0.0'
            }
        });
        
        // 请求拦截器
        this.client.interceptors.request.use(
            config => {
                console.log(`[${new Date().toISOString()}] ${config.method.toUpperCase()} ${config.url}`);
                return config;
            },
            error => Promise.reject(error)
        );
        
        // 响应拦截器
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error(`API请求失败: ${error.message}`);
                return Promise.reject(error);
            }
        );
    }
    
    /**
     * 查询单个IP地址
     * @param {string} ip - IP地址
     * @param {Object} options - 查询选项
     * @returns {Promise<Object>} 查询结果
     */
    async queryIP(ip, options = {}) {
        try {
            const params = {
                db_type: options.dbType || 'auto',
                lang: options.lang || 'zh-CN',
                format: options.format || 'json'
            };
            
            const response = await this.client.get(`/api/query/${ip}`, { params });
            return response.data;
        } catch (error) {
            throw new Error(`IP查询失败: ${error.message}`);
        }
    }
    
    /**
     * 批量查询IP地址
     * @param {Array<string>} ips - IP地址数组
     * @param {Object} options - 查询选项
     * @returns {Promise<Object>} 批量查询结果
     */
    async batchQuery(ips, options = {}) {
        try {
            if (!Array.isArray(ips) || ips.length === 0) {
                throw new Error('IP地址数组不能为空');
            }
            
            if (ips.length > 100) {
                throw new Error('单次批量查询最多支持100个IP地址');
            }
            
            const data = {
                ips: ips,
                db_type: options.dbType || 'city',
                lang: options.lang || 'zh-CN',
                include_details: options.includeDetails !== false
            };
            
            const response = await this.client.post('/api/query/batch', data);
            return response.data;
        } catch (error) {
            throw new Error(`批量查询失败: ${error.message}`);
        }
    }
    
    /**
     * 验证IP地址格式
     * @param {string} ip - IP地址
     * @returns {Promise<Object>} 验证结果
     */
    async validateIP(ip) {
        try {
            const response = await this.client.get(`/api/validate/${ip}`);
            return response.data;
        } catch (error) {
            throw new Error(`IP验证失败: ${error.message}`);
        }
    }
    
    /**
     * 获取数据库信息
     * @returns {Promise<Object>} 数据库信息
     */
    async getDatabaseInfo() {
        try {
            const response = await this.client.get('/api/database/info');
            return response.data;
        } catch (error) {
            throw new Error(`获取数据库信息失败: ${error.message}`);
        }
    }
    
    /**
     * 检查系统健康状态
     * @returns {Promise<Object>} 健康状态
     */
    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            throw new Error(`健康检查失败: ${error.message}`);
        }
    }
}

module.exports = IPQueryClient;
```

### 使用示例

```javascript
// example.js
const IPQueryClient = require('./ip-query-client');

async function main() {
    const client = new IPQueryClient('http://localhost:8000', {
        timeout: 5000,
        retries: 3
    });
    
    try {
        // 1. 健康检查
        console.log('=== 健康检查 ===');
        const health = await client.healthCheck();
        console.log('系统状态:', health.status);
        
        // 2. 单个IP查询
        console.log('\n=== 单个IP查询 ===');
        const result = await client.queryIP('8.8.8.8', {
            dbType: 'city',
            lang: 'zh-CN'
        });
        
        if (result.success) {
            const data = result.data;
            console.log(`IP: ${data.ip}`);
            console.log(`位置: ${data.country} ${data.region} ${data.city}`);
            console.log(`ISP: ${data.isp}`);
            console.log(`坐标: ${data.latitude}, ${data.longitude}`);
        }
        
        // 3. 批量查询
        console.log('\n=== 批量查询 ===');
        const batchResult = await client.batchQuery([
            '8.8.8.8',
            '1.1.1.1',
            '114.114.114.114'
        ], {
            dbType: 'city',
            lang: 'zh-CN'
        });
        
        if (batchResult.success) {
            console.log(`成功查询 ${batchResult.processed} 个IP地址:`);
            batchResult.results.forEach(item => {
                if (item.success) {
                    console.log(`- ${item.ip}: ${item.data.country} ${item.data.city}`);
                } else {
                    console.log(`- ${item.ip}: 查询失败`);
                }
            });
        }
        
        // 4. IP验证
        console.log('\n=== IP验证 ===');
        const validation = await client.validateIP('192.168.1.1');
        console.log(`IP: ${validation.ip}`);
        console.log(`有效: ${validation.valid}`);
        console.log(`类型: ${validation.type}`);
        console.log(`私有地址: ${validation.is_private}`);
        
    } catch (error) {
        console.error('错误:', error.message);
    }
}

main();
```

---

## 🐍 Python

### 安装依赖

```bash
pip install requests
```

### 完整SDK实现

```python
# ip_query_client.py
import requests
import json
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

class IPQueryClient:
    """IP查询系统Python客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 timeout: int = 10, retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'IPQueryClient-Python/1.0.0'
        })
    
    def _make_request(self, method: str, endpoint: str, 
                     params: Optional[Dict] = None, 
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        for attempt in range(self.retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, params=params, timeout=self.timeout)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retries - 1:
                    raise Exception(f"请求失败 (尝试 {attempt + 1}/{self.retries}): {str(e)}")
                time.sleep(2 ** attempt)  # 指数退避
    
    def query_ip(self, ip: str, db_type: str = "auto", 
                 lang: str = "zh-CN", format_type: str = "json") -> Dict[str, Any]:
        """
        查询单个IP地址
        
        Args:
            ip: IP地址
            db_type: 数据库类型 (auto/city/country/asn)
            lang: 语言 (zh-CN/en/ja)
            format_type: 响应格式 (json/xml/csv)
            
        Returns:
            查询结果字典
        """
        params = {
            'db_type': db_type,
            'lang': lang,
            'format': format_type
        }
        
        return self._make_request('GET', f'/api/query/{ip}', params=params)
    
    def batch_query(self, ips: List[str], db_type: str = "city", 
                   lang: str = "zh-CN", include_details: bool = True) -> Dict[str, Any]:
        """
        批量查询IP地址
        
        Args:
            ips: IP地址列表
            db_type: 数据库类型
            lang: 语言
            include_details: 是否包含详细信息
            
        Returns:
            批量查询结果字典
        """
        if not isinstance(ips, list) or len(ips) == 0:
            raise ValueError("IP地址列表不能为空")
        
        if len(ips) > 100:
            raise ValueError("单次批量查询最多支持100个IP地址")
        
        data = {
            'ips': ips,
            'db_type': db_type,
            'lang': lang,
            'include_details': include_details
        }
        
        return self._make_request('POST', '/api/query/batch', data=data)
    
    def validate_ip(self, ip: str) -> Dict[str, Any]:
        """验证IP地址格式"""
        return self._make_request('GET', f'/api/validate/{ip}')
    
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        return self._make_request('GET', '/api/database/info')
    
    def health_check(self) -> Dict[str, Any]:
        """检查系统健康状态"""
        return self._make_request('GET', '/health')
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
```

### 使用示例

```python
# example.py
from ip_query_client import IPQueryClient

def main():
    # 使用上下文管理器确保资源正确释放
    with IPQueryClient('http://localhost:8000') as client:
        try:
            # 1. 健康检查
            print("=== 健康检查 ===")
            health = client.health_check()
            print(f"系统状态: {health['status']}")
            
            # 2. 单个IP查询
            print("\n=== 单个IP查询 ===")
            result = client.query_ip('8.8.8.8', db_type='city', lang='zh-CN')
            
            if result['success']:
                data = result['data']
                print(f"IP: {data['ip']}")
                print(f"位置: {data['country']} {data.get('region', '')} {data.get('city', '')}")
                print(f"ISP: {data.get('isp', 'N/A')}")
                print(f"坐标: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}")
            
            # 3. 批量查询
            print("\n=== 批量查询 ===")
            ips = ['8.8.8.8', '1.1.1.1', '114.114.114.114']
            batch_result = client.batch_query(ips, db_type='city', lang='zh-CN')
            
            if batch_result['success']:
                print(f"成功查询 {batch_result['processed']} 个IP地址:")
                for item in batch_result['results']:
                    if item['success']:
                        data = item['data']
                        print(f"- {item['ip']}: {data['country']} {data.get('city', '')}")
                    else:
                        print(f"- {item['ip']}: 查询失败")
            
            # 4. IP验证
            print("\n=== IP验证 ===")
            validation = client.validate_ip('192.168.1.1')
            print(f"IP: {validation['ip']}")
            print(f"有效: {validation['valid']}")
            print(f"类型: {validation['type']}")
            print(f"私有地址: {validation['is_private']}")
            
            # 5. 数据库信息
            print("\n=== 数据库信息 ===")
            db_info = client.get_database_info()
            print(f"可用数据库: {db_info['total_databases']} 个")
            for db in db_info['databases']:
                print(f"- {db['name']}: {db['description']}")
                
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()
```

---

## 🐘 PHP

### 完整SDK实现

```php
<?php
// IPQueryClient.php

class IPQueryClient {
    private $baseUrl;
    private $timeout;
    private $retries;
    private $userAgent;
    
    public function __construct($baseUrl = 'http://localhost:8000', $options = []) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $options['timeout'] ?? 10;
        $this->retries = $options['retries'] ?? 3;
        $this->userAgent = 'IPQueryClient-PHP/1.0.0';
    }
    
    /**
     * 发送HTTP请求
     */
    private function makeRequest($method, $endpoint, $params = null, $data = null) {
        $url = $this->baseUrl . '/' . ltrim($endpoint, '/');
        
        if ($method === 'GET' && $params) {
            $url .= '?' . http_build_query($params);
        }
        
        $context = stream_context_create([
            'http' => [
                'method' => $method,
                'header' => [
                    'Content-Type: application/json',
                    'User-Agent: ' . $this->userAgent
                ],
                'timeout' => $this->timeout,
                'content' => $data ? json_encode($data) : null
            ]
        ]);
        
        for ($attempt = 0; $attempt < $this->retries; $attempt++) {
            $response = @file_get_contents($url, false, $context);
            
            if ($response !== false) {
                $result = json_decode($response, true);
                if (json_last_error() === JSON_ERROR_NONE) {
                    return $result;
                }
            }
            
            if ($attempt < $this->retries - 1) {
                sleep(pow(2, $attempt)); // 指数退避
            }
        }
        
        throw new Exception("请求失败，已重试 {$this->retries} 次");
    }
    
    /**
     * 查询单个IP地址
     */
    public function queryIP($ip, $options = []) {
        $params = [
            'db_type' => $options['dbType'] ?? 'auto',
            'lang' => $options['lang'] ?? 'zh-CN',
            'format' => $options['format'] ?? 'json'
        ];
        
        return $this->makeRequest('GET', "/api/query/{$ip}", $params);
    }
    
    /**
     * 批量查询IP地址
     */
    public function batchQuery($ips, $options = []) {
        if (!is_array($ips) || empty($ips)) {
            throw new InvalidArgumentException('IP地址数组不能为空');
        }
        
        if (count($ips) > 100) {
            throw new InvalidArgumentException('单次批量查询最多支持100个IP地址');
        }
        
        $data = [
            'ips' => $ips,
            'db_type' => $options['dbType'] ?? 'city',
            'lang' => $options['lang'] ?? 'zh-CN',
            'include_details' => $options['includeDetails'] ?? true
        ];
        
        return $this->makeRequest('POST', '/api/query/batch', null, $data);
    }
    
    /**
     * 验证IP地址格式
     */
    public function validateIP($ip) {
        return $this->makeRequest('GET', "/api/validate/{$ip}");
    }
    
    /**
     * 获取数据库信息
     */
    public function getDatabaseInfo() {
        return $this->makeRequest('GET', '/api/database/info');
    }
    
    /**
     * 检查系统健康状态
     */
    public function healthCheck() {
        return $this->makeRequest('GET', '/health');
    }
}
```

### 使用示例

```php
<?php
// example.php
require_once 'IPQueryClient.php';

try {
    $client = new IPQueryClient('http://localhost:8000', [
        'timeout' => 5,
        'retries' => 3
    ]);
    
    // 1. 健康检查
    echo "=== 健康检查 ===\n";
    $health = $client->healthCheck();
    echo "系统状态: " . $health['status'] . "\n";
    
    // 2. 单个IP查询
    echo "\n=== 单个IP查询 ===\n";
    $result = $client->queryIP('8.8.8.8', [
        'dbType' => 'city',
        'lang' => 'zh-CN'
    ]);
    
    if ($result['success']) {
        $data = $result['data'];
        echo "IP: " . $data['ip'] . "\n";
        echo "位置: " . $data['country'] . " " . ($data['region'] ?? '') . " " . ($data['city'] ?? '') . "\n";
        echo "ISP: " . ($data['isp'] ?? 'N/A') . "\n";
    }
    
    // 3. 批量查询
    echo "\n=== 批量查询 ===\n";
    $ips = ['8.8.8.8', '1.1.1.1', '114.114.114.114'];
    $batchResult = $client->batchQuery($ips, [
        'dbType' => 'city',
        'lang' => 'zh-CN'
    ]);
    
    if ($batchResult['success']) {
        echo "成功查询 " . $batchResult['processed'] . " 个IP地址:\n";
        foreach ($batchResult['results'] as $item) {
            if ($item['success']) {
                $data = $item['data'];
                echo "- " . $item['ip'] . ": " . $data['country'] . " " . ($data['city'] ?? '') . "\n";
            } else {
                echo "- " . $item['ip'] . ": 查询失败\n";
            }
        }
    }
    
    // 4. IP验证
    echo "\n=== IP验证 ===\n";
    $validation = $client->validateIP('192.168.1.1');
    echo "IP: " . $validation['ip'] . "\n";
    echo "有效: " . ($validation['valid'] ? '是' : '否') . "\n";
    echo "类型: " . $validation['type'] . "\n";
    echo "私有地址: " . ($validation['is_private'] ? '是' : '否') . "\n";
    
} catch (Exception $e) {
    echo "错误: " . $e->getMessage() . "\n";
}
?>
```

---

## ☕ Java

### Maven依赖

```xml
<dependencies>
    <dependency>
        <groupId>com.squareup.okhttp3</groupId>
        <artifactId>okhttp</artifactId>
        <version>4.12.0</version>
    </dependency>
    <dependency>
        <groupId>com.google.code.gson</groupId>
        <artifactId>gson</artifactId>
        <version>2.10.1</version>
    </dependency>
</dependencies>
```

### 完整SDK实现

```java
// IPQueryClient.java
import okhttp3.*;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.TimeUnit;

public class IPQueryClient {
    private final String baseUrl;
    private final OkHttpClient client;
    private final Gson gson;
    
    public IPQueryClient(String baseUrl) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.client = new OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .addInterceptor(new UserAgentInterceptor())
            .build();
        this.gson = new Gson();
    }
    
    // 用户代理拦截器
    private static class UserAgentInterceptor implements Interceptor {
        @Override
        public Response intercept(Chain chain) throws IOException {
            Request request = chain.request().newBuilder()
                .addHeader("User-Agent", "IPQueryClient-Java/1.0.0")
                .build();
            return chain.proceed(request);
        }
    }
    
    /**
     * 查询单个IP地址
     */
    public JsonObject queryIP(String ip, String dbType, String lang) throws IOException {
        HttpUrl.Builder urlBuilder = HttpUrl.parse(baseUrl + "/api/query/" + ip).newBuilder();
        if (dbType != null) urlBuilder.addQueryParameter("db_type", dbType);
        if (lang != null) urlBuilder.addQueryParameter("lang", lang);
        
        Request request = new Request.Builder()
            .url(urlBuilder.build())
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("请求失败: " + response);
            }
            return gson.fromJson(response.body().string(), JsonObject.class);
        }
    }
    
    /**
     * 批量查询IP地址
     */
    public JsonObject batchQuery(List<String> ips, String dbType, String lang) throws IOException {
        if (ips == null || ips.isEmpty()) {
            throw new IllegalArgumentException("IP地址列表不能为空");
        }
        
        if (ips.size() > 100) {
            throw new IllegalArgumentException("单次批量查询最多支持100个IP地址");
        }
        
        Map<String, Object> requestData = new HashMap<>();
        requestData.put("ips", ips);
        requestData.put("db_type", dbType != null ? dbType : "city");
        requestData.put("lang", lang != null ? lang : "zh-CN");
        requestData.put("include_details", true);
        
        RequestBody body = RequestBody.create(
            gson.toJson(requestData),
            MediaType.get("application/json; charset=utf-8")
        );
        
        Request request = new Request.Builder()
            .url(baseUrl + "/api/query/batch")
            .post(body)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("批量查询失败: " + response);
            }
            return gson.fromJson(response.body().string(), JsonObject.class);
        }
    }
    
    /**
     * 验证IP地址格式
     */
    public JsonObject validateIP(String ip) throws IOException {
        Request request = new Request.Builder()
            .url(baseUrl + "/api/validate/" + ip)
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("IP验证失败: " + response);
            }
            return gson.fromJson(response.body().string(), JsonObject.class);
        }
    }
    
    /**
     * 检查系统健康状态
     */
    public JsonObject healthCheck() throws IOException {
        Request request = new Request.Builder()
            .url(baseUrl + "/health")
            .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("健康检查失败: " + response);
            }
            return gson.fromJson(response.body().string(), JsonObject.class);
        }
    }
    
    public void close() {
        client.dispatcher().executorService().shutdown();
        client.connectionPool().evictAll();
    }
}
```

### 使用示例

```java
// Example.java
import java.util.Arrays;
import java.util.List;

public class Example {
    public static void main(String[] args) {
        IPQueryClient client = new IPQueryClient("http://localhost:8000");
        
        try {
            // 1. 健康检查
            System.out.println("=== 健康检查 ===");
            var health = client.healthCheck();
            System.out.println("系统状态: " + health.get("status").getAsString());
            
            // 2. 单个IP查询
            System.out.println("\n=== 单个IP查询 ===");
            var result = client.queryIP("8.8.8.8", "city", "zh-CN");
            
            if (result.get("success").getAsBoolean()) {
                var data = result.getAsJsonObject("data");
                System.out.println("IP: " + data.get("ip").getAsString());
                System.out.println("位置: " + data.get("country").getAsString() + 
                                 " " + data.get("city").getAsString());
                System.out.println("ISP: " + data.get("isp").getAsString());
            }
            
            // 3. 批量查询
            System.out.println("\n=== 批量查询 ===");
            List<String> ips = Arrays.asList("8.8.8.8", "1.1.1.1", "114.114.114.114");
            var batchResult = client.batchQuery(ips, "city", "zh-CN");
            
            if (batchResult.get("success").getAsBoolean()) {
                var results = batchResult.getAsJsonArray("results");
                System.out.println("成功查询 " + batchResult.get("processed").getAsInt() + " 个IP地址:");
                
                for (var element : results) {
                    var item = element.getAsJsonObject();
                    if (item.get("success").getAsBoolean()) {
                        var data = item.getAsJsonObject("data");
                        System.out.println("- " + item.get("ip").getAsString() + 
                                         ": " + data.get("country").getAsString() + 
                                         " " + data.get("city").getAsString());
                    }
                }
            }
            
        } catch (Exception e) {
            System.err.println("错误: " + e.getMessage());
        } finally {
            client.close();
        }
    }
}
```

---

## 🔧 集成最佳实践

### 1. 错误处理

```javascript
// 统一错误处理
class APIError extends Error {
    constructor(message, statusCode, response) {
        super(message);
        this.statusCode = statusCode;
        this.response = response;
    }
}

// 在客户端中使用
try {
    const result = await client.queryIP('8.8.8.8');
} catch (error) {
    if (error instanceof APIError) {
        console.error(`API错误 ${error.statusCode}: ${error.message}`);
    } else {
        console.error('网络错误:', error.message);
    }
}
```

### 2. 缓存策略

```python
import time
from functools import lru_cache

class CachedIPQueryClient(IPQueryClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._cache_ttl = 3600  # 1小时缓存
    
    def query_ip_cached(self, ip, **kwargs):
        cache_key = f"{ip}:{hash(frozenset(kwargs.items()))}"
        
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return cached_data
        
        result = self.query_ip(ip, **kwargs)
        self._cache[cache_key] = (result, time.time())
        return result
```

### 3. 重试机制

```java
// 指数退避重试
public class RetryableIPQueryClient extends IPQueryClient {
    private static final int MAX_RETRIES = 3;
    private static final long INITIAL_DELAY = 1000; // 1秒
    
    public JsonObject queryIPWithRetry(String ip, String dbType, String lang) {
        Exception lastException = null;
        
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                return queryIP(ip, dbType, lang);
            } catch (Exception e) {
                lastException = e;
                if (attempt < MAX_RETRIES - 1) {
                    try {
                        Thread.sleep(INITIAL_DELAY * (1L << attempt));
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException("重试被中断", ie);
                    }
                }
            }
        }
        
        throw new RuntimeException("重试失败", lastException);
    }
}
```

### 4. 批量处理优化

```php
class OptimizedIPQueryClient extends IPQueryClient {
    /**
     * 分批处理大量IP查询
     */
    public function queryLargeIPList($ips, $batchSize = 50, $options = []) {
        $results = [];
        $batches = array_chunk($ips, $batchSize);
        
        foreach ($batches as $batch) {
            try {
                $batchResult = $this->batchQuery($batch, $options);
                if ($batchResult['success']) {
                    $results = array_merge($results, $batchResult['results']);
                }
                
                // 避免请求过于频繁
                usleep(100000); // 100ms延迟
                
            } catch (Exception $e) {
                error_log("批次查询失败: " . $e->getMessage());
                // 继续处理下一批
            }
        }
        
        return $results;
    }
}
```

---

## 📞 技术支持

如需更多帮助或有问题反馈，请访问：

- **GitHub仓库**: https://github.com/Aoki2008/ip-query-system
- **API文档**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **交互式文档**: [API_EXAMPLES.html](./API_EXAMPLES.html)

---

*最后更新: 2025-07-31 | 版本: v4.2.0*
