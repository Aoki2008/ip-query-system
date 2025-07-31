# 🔧 管理后台技术规范文档

## 📋 技术架构详细设计

### 🏗️ 系统架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   管理员用户     │    │   普通用户       │    │   监控系统       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  管理后台前端    │    │  用户查询前端    │    │  监控告警系统    │
│   (Vue3 + TS)   │    │   (Vue3 + TS)   │    │ (Prometheus)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────┬───────────┴──────────────────────┘
                     ▼
          ┌─────────────────┐
          │   Nginx 反向代理  │
          └─────────┬───────┘
                    ▼
          ┌─────────────────┐
          │  FastAPI 后端    │
          │  (管理API +     │
          │   查询API)      │
          └─────────┬───────┘
                    ▼
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐  ┌─────────────┐  ┌─────────┐
│PostgreSQL│  │    Redis    │  │  GeoIP  │
│  数据库   │  │    缓存     │  │  数据库  │
└─────────┘  └─────────────┘  └─────────┘
```

### 🔌 API接口设计

#### 管理后台API端点

```
# 认证管理
POST   /api/admin/auth/login          # 管理员登录
POST   /api/admin/auth/logout         # 管理员登出
POST   /api/admin/auth/refresh        # 刷新令牌
GET    /api/admin/auth/profile        # 获取管理员信息

# 系统监控
GET    /api/admin/monitoring/system   # 系统状态监控
GET    /api/admin/monitoring/api      # API性能统计
GET    /api/admin/monitoring/logs     # 日志查询
POST   /api/admin/monitoring/alerts   # 告警配置

# 数据管理
GET    /api/admin/data/queries        # 查询记录管理
GET    /api/admin/data/statistics     # 数据统计分析
POST   /api/admin/data/export         # 数据导出
DELETE /api/admin/data/cleanup        # 数据清理

# 系统配置
GET    /api/admin/config/system       # 系统配置
PUT    /api/admin/config/system       # 更新配置
GET    /api/admin/config/cache        # 缓存配置
POST   /api/admin/config/backup       # 备份管理
```

#### 数据模型设计

```python
# 管理员模型
class AdminUser(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str  # 'super_admin', 'admin', 'readonly'
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

# 查询日志模型
class QueryLog(BaseModel):
    id: int
    ip_address: str
    query_ip: str
    result: Dict[str, Any]
    query_time: float
    created_at: datetime
    user_agent: Optional[str]
    source: str  # 'web', 'api', 'batch'

# 系统配置模型
class SystemConfig(BaseModel):
    id: int
    config_key: str
    config_value: str
    description: Optional[str]
    updated_at: datetime
    updated_by: int

# 监控指标模型
class MonitoringMetric(BaseModel):
    timestamp: datetime
    metric_name: str
    metric_value: float
    tags: Dict[str, str]
```

### 🎨 前端组件设计

#### 组件层次结构

```
AdminApp
├── Layout
│   ├── Header (顶部导航)
│   ├── Sidebar (侧边栏菜单)
│   └── Main (主内容区)
├── Dashboard (仪表板)
│   ├── SystemOverview (系统概览)
│   ├── QuickStats (快速统计)
│   └── RecentActivity (最近活动)
├── Monitoring (监控模块)
│   ├── SystemMonitor (系统监控)
│   ├── APIMetrics (API指标)
│   ├── LogViewer (日志查看)
│   └── AlertManager (告警管理)
├── DataManagement (数据管理)
│   ├── QueryHistory (查询历史)
│   ├── Statistics (统计分析)
│   ├── Reports (报表生成)
│   └── DataExport (数据导出)
└── SystemConfig (系统配置)
    ├── GeneralSettings (通用设置)
    ├── CacheConfig (缓存配置)
    ├── BackupManager (备份管理)
    └── UserManagement (用户管理)
```

#### 状态管理设计

```typescript
// Pinia Store 设计
interface AdminState {
  // 认证状态
  auth: {
    user: AdminUser | null
    token: string | null
    permissions: string[]
  }
  
  // 系统监控状态
  monitoring: {
    systemMetrics: SystemMetrics
    apiMetrics: APIMetrics
    alerts: Alert[]
    isRealTimeEnabled: boolean
  }
  
  // 数据管理状态
  data: {
    queryLogs: QueryLog[]
    statistics: Statistics
    currentPage: number
    filters: DataFilters
  }
  
  // 系统配置状态
  config: {
    systemConfig: SystemConfig
    cacheConfig: CacheConfig
    backupStatus: BackupStatus
  }
}
```

### 🔐 安全设计

#### 认证授权流程

```
1. 管理员登录
   ├── 用户名密码验证
   ├── 生成JWT访问令牌 (15分钟)
   ├── 生成刷新令牌 (7天)
   └── 返回用户信息和权限

2. API请求认证
   ├── 检查Authorization头部
   ├── 验证JWT令牌有效性
   ├── 检查用户权限
   └── 允许/拒绝访问

3. 令牌刷新
   ├── 使用刷新令牌
   ├── 验证令牌有效性
   ├── 生成新的访问令牌
   └── 返回新令牌
```

#### 权限控制矩阵

```
角色权限矩阵:
                    超级管理员  系统管理员  只读用户
系统监控查看           ✓         ✓         ✓
系统配置修改           ✓         ✓         ✗
数据导出              ✓         ✓         ✗
数据删除              ✓         ✗         ✗
用户管理              ✓         ✗         ✗
系统备份恢复           ✓         ✗         ✗
```

### 📊 监控指标设计

#### 系统监控指标

```python
# 系统资源指标
SYSTEM_METRICS = {
    'cpu_usage': 'CPU使用率 (%)',
    'memory_usage': '内存使用率 (%)',
    'disk_usage': '磁盘使用率 (%)',
    'network_io': '网络IO (bytes/s)',
    'load_average': '系统负载',
}

# API性能指标
API_METRICS = {
    'request_count': '请求总数',
    'response_time_avg': '平均响应时间 (ms)',
    'response_time_p95': '95%响应时间 (ms)',
    'error_rate': '错误率 (%)',
    'concurrent_users': '并发用户数',
}

# 业务指标
BUSINESS_METRICS = {
    'daily_queries': '日查询量',
    'unique_ips': '独立IP数',
    'cache_hit_rate': '缓存命中率 (%)',
    'top_countries': '热门国家/地区',
    'query_sources': '查询来源分布',
}
```

#### 告警规则配置

```yaml
# 告警规则示例
alert_rules:
  - name: "高CPU使用率"
    condition: "cpu_usage > 80"
    duration: "5m"
    severity: "warning"
    notification: ["email", "webhook"]
    
  - name: "API响应时间过长"
    condition: "response_time_avg > 2000"
    duration: "2m"
    severity: "critical"
    notification: ["email", "sms"]
    
  - name: "错误率过高"
    condition: "error_rate > 5"
    duration: "1m"
    severity: "critical"
    notification: ["email", "webhook"]
```

### 🗄️ 数据库设计

#### 表结构设计

```sql
-- 管理员用户表
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);

-- 查询日志表 (分区表)
CREATE TABLE query_logs (
    id BIGSERIAL PRIMARY KEY,
    ip_address INET NOT NULL,
    query_ip INET NOT NULL,
    result JSONB,
    query_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    source VARCHAR(20) DEFAULT 'web',
    response_size INTEGER,
    cache_hit BOOLEAN DEFAULT false
) PARTITION BY RANGE (created_at);

-- 系统配置表
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    is_sensitive BOOLEAN DEFAULT false,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES admin_users(id)
);

-- 监控指标表 (时序数据)
CREATE TABLE monitoring_metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 告警记录表
CREATE TABLE alert_logs (
    id BIGSERIAL PRIMARY KEY,
    alert_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    triggered_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    notification_sent BOOLEAN DEFAULT false
);
```

#### 索引优化

```sql
-- 查询日志表索引
CREATE INDEX idx_query_logs_created_at ON query_logs (created_at);
CREATE INDEX idx_query_logs_query_ip ON query_logs (query_ip);
CREATE INDEX idx_query_logs_source ON query_logs (source);

-- 监控指标表索引
CREATE INDEX idx_monitoring_metrics_timestamp ON monitoring_metrics (timestamp);
CREATE INDEX idx_monitoring_metrics_name_time ON monitoring_metrics (metric_name, timestamp);

-- 告警记录表索引
CREATE INDEX idx_alert_logs_triggered_at ON alert_logs (triggered_at);
CREATE INDEX idx_alert_logs_status ON alert_logs (status);
```

### 🚀 部署配置

#### Docker Compose 配置

```yaml
version: '3.8'
services:
  # 管理后台前端
  admin-frontend:
    build: ./frontend-admin
    ports:
      - "8081:80"
    depends_on:
      - admin-backend
    environment:
      - VUE_APP_API_URL=http://localhost:8000
      
  # 扩展的后端服务
  admin-backend:
    build: ./backend-fastapi
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/ipquery
      - REDIS_URL=redis://redis:6379/0
      - ADMIN_SECRET_KEY=your-secret-key
      
  # 监控服务
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 📈 性能优化策略

#### 数据库优化
- **分区表**: 按时间分区查询日志表
- **索引优化**: 针对查询模式优化索引
- **连接池**: 配置合适的数据库连接池
- **查询优化**: 使用EXPLAIN分析慢查询

#### 缓存策略
- **Redis缓存**: 缓存频繁查询的统计数据
- **应用缓存**: 缓存系统配置和权限信息
- **CDN缓存**: 静态资源CDN加速

#### 前端优化
- **代码分割**: 按路由分割代码包
- **懒加载**: 组件和图表懒加载
- **虚拟滚动**: 大数据列表虚拟滚动
- **缓存策略**: 合理的HTTP缓存策略

---

**🔧 技术规范文档** - 确保管理后台开发的技术标准和质量 ⚡
