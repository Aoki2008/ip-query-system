# 🚀 IP查询系统 API 使用指南

## 📋 快速开始

本指南将帮助您快速上手IP查询系统API，从基础查询到高级功能的完整使用流程。

## 🔗 API访问地址

- **开发环境**: `http://localhost:8000`
- **生产环境**: `https://your-domain.com`
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc文档**: `http://localhost:8000/redoc`

## 🌟 核心功能概览

### 1. 🔍 单个IP查询
最基础的功能，查询单个IP地址的地理位置信息。

```bash
curl "http://localhost:8000/api/query?ip=8.8.8.8"
```

### 2. 📊 批量IP查询
一次性查询多个IP地址，提高查询效率。

```bash
curl -X POST "http://localhost:8000/api/batch-query" \
  -H "Content-Type: application/json" \
  -d '{"ips": ["8.8.8.8", "1.1.1.1"]}'
```

### 3. ✅ IP地址验证
验证IP地址格式和类型。

```bash
curl "http://localhost:8000/api/validate/192.168.1.1"
```

### 4. 📈 系统监控
检查系统健康状态和性能指标。

```bash
curl "http://localhost:8000/health"
```

---

## 📚 详细使用教程

### 🎯 场景1: 网站访客地理位置分析

**需求**: 分析网站访客的地理分布

**解决方案**:
```javascript
// 获取访客IP并查询地理位置
async function analyzeVisitorLocation(visitorIP) {
    try {
        const response = await fetch(`/api/query/${visitorIP}?lang=zh-CN`);
        const data = await response.json();
        
        if (data.success) {
            const location = data.data;
            console.log(`访客来自: ${location.country} ${location.region} ${location.city}`);
            
            // 存储到数据库或分析系统
            await saveVisitorAnalytics({
                ip: visitorIP,
                country: location.country,
                city: location.city,
                isp: location.isp,
                coordinates: [location.latitude, location.longitude]
            });
        }
    } catch (error) {
        console.error('地理位置查询失败:', error);
    }
}
```

### 🎯 场景2: 安全监控和风险评估

**需求**: 检测可疑IP地址和潜在威胁

**解决方案**:
```python
import requests
from typing import List, Dict

class SecurityMonitor:
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
    
    def analyze_suspicious_ips(self, ip_list: List[str]) -> Dict:
        """分析可疑IP列表"""
        # 批量查询IP信息
        response = requests.post(f"{self.api_base}/api/query/batch", json={
            "ips": ip_list,
            "db_type": "city",
            "include_details": True
        })
        
        if response.status_code == 200:
            data = response.json()
            risk_analysis = []
            
            for result in data['results']:
                if result['success']:
                    ip_data = result['data']
                    risk_score = self.calculate_risk_score(ip_data)
                    
                    risk_analysis.append({
                        'ip': result['ip'],
                        'country': ip_data['country'],
                        'isp': ip_data['isp'],
                        'is_proxy': ip_data.get('is_proxy', False),
                        'risk_score': risk_score,
                        'risk_level': self.get_risk_level(risk_score)
                    })
            
            return {
                'total_analyzed': len(risk_analysis),
                'high_risk_count': len([r for r in risk_analysis if r['risk_level'] == 'high']),
                'analysis': risk_analysis
            }
    
    def calculate_risk_score(self, ip_data: Dict) -> int:
        """计算风险评分 (0-100)"""
        score = 0
        
        # 代理/VPN检测
        if ip_data.get('is_proxy', False):
            score += 30
        
        # 高风险国家/地区
        high_risk_countries = ['CN', 'RU', 'KP', 'IR']
        if ip_data.get('country_code') in high_risk_countries:
            score += 20
        
        # 云服务提供商
        cloud_providers = ['Amazon', 'Google', 'Microsoft', 'Alibaba']
        if any(provider in ip_data.get('isp', '') for provider in cloud_providers):
            score += 15
        
        return min(score, 100)
    
    def get_risk_level(self, score: int) -> str:
        """获取风险等级"""
        if score >= 70:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'

# 使用示例
monitor = SecurityMonitor()
suspicious_ips = ['1.2.3.4', '5.6.7.8', '9.10.11.12']
analysis = monitor.analyze_suspicious_ips(suspicious_ips)
print(f"发现 {analysis['high_risk_count']} 个高风险IP")
```

### 🎯 场景3: 内容本地化和CDN优化

**需求**: 根据用户地理位置提供本地化内容

**解决方案**:
```php
<?php
class ContentLocalizer {
    private $apiBase;
    
    public function __construct($apiBase = 'http://localhost:8000') {
        $this->apiBase = $apiBase;
    }
    
    public function getLocalizedContent($userIP) {
        // 查询用户地理位置
        $response = file_get_contents($this->apiBase . "/api/query/{$userIP}?lang=en");
        $data = json_decode($response, true);
        
        if ($data['success']) {
            $location = $data['data'];
            
            return [
                'language' => $this->getLanguageByCountry($location['country_code']),
                'currency' => $this->getCurrencyByCountry($location['country_code']),
                'timezone' => $location['timezone'],
                'cdn_region' => $this->getCDNRegion($location['country_code']),
                'local_content' => $this->getLocalContent($location['country_code'])
            ];
        }
        
        return $this->getDefaultContent();
    }
    
    private function getLanguageByCountry($countryCode) {
        $languages = [
            'CN' => 'zh-CN',
            'US' => 'en-US',
            'JP' => 'ja-JP',
            'DE' => 'de-DE',
            'FR' => 'fr-FR'
        ];
        
        return $languages[$countryCode] ?? 'en-US';
    }
    
    private function getCDNRegion($countryCode) {
        $regions = [
            'CN' => 'asia-east',
            'JP' => 'asia-east',
            'US' => 'us-west',
            'DE' => 'europe-west',
            'AU' => 'asia-pacific'
        ];
        
        return $regions[$countryCode] ?? 'global';
    }
}

// 使用示例
$localizer = new ContentLocalizer();
$userIP = $_SERVER['REMOTE_ADDR'];
$localizedContent = $localizer->getLocalizedContent($userIP);

echo "用户语言: " . $localizedContent['language'] . "\n";
echo "CDN区域: " . $localizedContent['cdn_region'] . "\n";
?>
```

### 🎯 场景4: 数据分析和报表生成

**需求**: 生成IP访问统计报表

**解决方案**:
```java
import java.util.*;
import java.util.stream.Collectors;

public class IPAnalyticsReporter {
    private IPQueryClient client;
    
    public IPAnalyticsReporter() {
        this.client = new IPQueryClient("http://localhost:8000");
    }
    
    public Map<String, Object> generateAccessReport(List<String> accessLogs) {
        // 提取IP地址
        List<String> uniqueIPs = accessLogs.stream()
            .map(this::extractIPFromLog)
            .distinct()
            .collect(Collectors.toList());
        
        try {
            // 批量查询IP信息
            JsonObject batchResult = client.batchQuery(uniqueIPs, "city", "zh-CN");
            
            if (batchResult.get("success").getAsBoolean()) {
                return analyzeResults(batchResult.getAsJsonArray("results"));
            }
        } catch (Exception e) {
            System.err.println("查询失败: " + e.getMessage());
        }
        
        return Collections.emptyMap();
    }
    
    private Map<String, Object> analyzeResults(JsonArray results) {
        Map<String, Integer> countryStats = new HashMap<>();
        Map<String, Integer> cityStats = new HashMap<>();
        Map<String, Integer> ispStats = new HashMap<>();
        
        for (var element : results) {
            var result = element.getAsJsonObject();
            if (result.get("success").getAsBoolean()) {
                var data = result.getAsJsonObject("data");
                
                // 统计国家分布
                String country = data.get("country").getAsString();
                countryStats.merge(country, 1, Integer::sum);
                
                // 统计城市分布
                String city = data.get("city").getAsString();
                cityStats.merge(city, 1, Integer::sum);
                
                // 统计ISP分布
                String isp = data.get("isp").getAsString();
                ispStats.merge(isp, 1, Integer::sum);
            }
        }
        
        Map<String, Object> report = new HashMap<>();
        report.put("total_unique_ips", results.size());
        report.put("country_distribution", getTopEntries(countryStats, 10));
        report.put("city_distribution", getTopEntries(cityStats, 10));
        report.put("isp_distribution", getTopEntries(ispStats, 10));
        report.put("generated_at", new Date().toString());
        
        return report;
    }
    
    private String extractIPFromLog(String logEntry) {
        // 简单的IP提取逻辑，实际应用中需要更复杂的解析
        return logEntry.split(" ")[0];
    }
    
    private List<Map<String, Object>> getTopEntries(Map<String, Integer> stats, int limit) {
        return stats.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(limit)
            .map(entry -> {
                Map<String, Object> item = new HashMap<>();
                item.put("name", entry.getKey());
                item.put("count", entry.getValue());
                return item;
            })
            .collect(Collectors.toList());
    }
}
```

---

## 🔧 高级功能和最佳实践

### 1. 🚀 性能优化

#### 缓存策略
```javascript
class CachedIPQuery {
    constructor(cacheSize = 1000, cacheTTL = 3600000) { // 1小时
        this.cache = new Map();
        this.cacheSize = cacheSize;
        this.cacheTTL = cacheTTL;
    }
    
    async queryIP(ip) {
        const cacheKey = ip;
        const cached = this.cache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
            return cached.data;
        }
        
        const result = await fetch(`/api/query/${ip}`);
        const data = await result.json();
        
        // 缓存结果
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });
        
        // 清理过期缓存
        if (this.cache.size > this.cacheSize) {
            this.cleanupCache();
        }
        
        return data;
    }
    
    cleanupCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > this.cacheTTL) {
                this.cache.delete(key);
            }
        }
    }
}
```

#### 批量处理优化
```python
async def process_large_ip_list(ip_list, batch_size=50):
    """处理大量IP地址的优化方案"""
    results = []
    
    # 分批处理
    for i in range(0, len(ip_list), batch_size):
        batch = ip_list[i:i + batch_size]
        
        try:
            # 异步批量查询
            response = await asyncio.create_task(
                query_batch_async(batch)
            )
            results.extend(response['results'])
            
            # 避免请求过于频繁
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"批次 {i//batch_size + 1} 处理失败: {e}")
            continue
    
    return results
```

### 2. 🛡️ 错误处理和重试机制

```python
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1):
    """指数退避重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"重试 {attempt + 1}/{max_retries}，等待 {delay:.2f} 秒")
                    time.sleep(delay)
            
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=1)
def query_ip_with_retry(ip):
    """带重试机制的IP查询"""
    response = requests.get(f"http://localhost:8000/api/query/{ip}")
    response.raise_for_status()
    return response.json()
```

### 3. 📊 监控和日志

```javascript
class APIMonitor {
    constructor() {
        this.metrics = {
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            averageResponseTime: 0,
            responseTimeHistory: []
        };
    }
    
    async monitoredQuery(ip) {
        const startTime = Date.now();
        this.metrics.totalRequests++;
        
        try {
            const response = await fetch(`/api/query/${ip}`);
            const data = await response.json();
            
            if (data.success) {
                this.metrics.successfulRequests++;
            } else {
                this.metrics.failedRequests++;
            }
            
            const responseTime = Date.now() - startTime;
            this.updateResponseTime(responseTime);
            
            // 记录日志
            console.log(`IP查询: ${ip}, 响应时间: ${responseTime}ms, 状态: ${data.success ? '成功' : '失败'}`);
            
            return data;
            
        } catch (error) {
            this.metrics.failedRequests++;
            console.error(`IP查询失败: ${ip}, 错误: ${error.message}`);
            throw error;
        }
    }
    
    updateResponseTime(responseTime) {
        this.metrics.responseTimeHistory.push(responseTime);
        
        // 保持最近100次请求的记录
        if (this.metrics.responseTimeHistory.length > 100) {
            this.metrics.responseTimeHistory.shift();
        }
        
        // 计算平均响应时间
        this.metrics.averageResponseTime = 
            this.metrics.responseTimeHistory.reduce((a, b) => a + b, 0) / 
            this.metrics.responseTimeHistory.length;
    }
    
    getMetrics() {
        return {
            ...this.metrics,
            successRate: (this.metrics.successfulRequests / this.metrics.totalRequests * 100).toFixed(2) + '%'
        };
    }
}
```

---

## 📞 技术支持和资源

### 🔗 相关链接
- **GitHub仓库**: https://github.com/Aoki2008/ip-query-system
- **API文档**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **SDK示例**: [SDK_EXAMPLES.md](./SDK_EXAMPLES.md)
- **Postman集合**: [IP_Query_System.postman_collection.json](./IP_Query_System.postman_collection.json)

### 🆘 常见问题

**Q: API有请求频率限制吗？**
A: 是的，默认限制为每分钟100次请求。如需更高频率，请联系管理员。

**Q: 支持IPv6地址查询吗？**
A: 是的，系统完全支持IPv4和IPv6地址查询。

**Q: 查询结果的准确性如何？**
A: 城市级精度约为80-90%，国家级精度超过99%。

**Q: 可以查询私有IP地址吗？**
A: 可以验证私有IP格式，但无法提供地理位置信息。

### 📧 联系我们
如有问题或建议，请通过以下方式联系：
- **GitHub Issues**: https://github.com/Aoki2008/ip-query-system/issues
- **邮箱**: support@ip-query-system.com

---

*最后更新: 2025-07-31 | 版本: v4.2.0*
