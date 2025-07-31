# 阶段2: 系统监控与统计功能文档

## 📋 概述

阶段2系统监控与统计模块为管理后台提供了完整的系统监控、性能统计、日志分析和告警通知功能，实现了企业级的系统运维监控能力。

## 🎯 功能模块

### 1. 实时系统监控

#### 📊 系统状态监控
- **CPU监控**: 实时CPU使用率监控和历史趋势
- **内存监控**: 内存使用情况、可用内存、内存占用率
- **磁盘监控**: 磁盘使用率、可用空间、I/O统计
- **网络监控**: 网络流量、连接数、带宽使用
- **进程监控**: 系统进程数量、服务状态监控

#### 🔧 技术实现
- **psutil库**: 跨平台系统信息获取
- **实时数据**: 1秒间隔的实时数据更新
- **历史数据**: 系统指标历史数据存储
- **多平台支持**: Windows/Linux/macOS兼容

#### 📡 API接口
- `GET /api/admin/monitoring/status` - 获取系统状态
- `GET /api/admin/monitoring/health` - 系统健康检查
- `GET /api/admin/monitoring/realtime` - 实时监控数据

### 2. API性能统计

#### 📈 性能指标统计
- **请求统计**: API调用次数、频率分析
- **响应时间**: 平均响应时间、P95/P99延迟
- **错误率分析**: HTTP错误码统计、错误趋势
- **端点分析**: 热门API端点、性能瓶颈识别

#### 🔧 技术实现
- **中间件监控**: FastAPI中间件自动收集性能数据
- **数据库存储**: SQLAlchemy存储性能指标
- **实时计算**: 动态计算统计指标
- **趋势分析**: 时间序列数据分析

#### 📡 API接口
- `GET /api/admin/analytics/stats` - API统计数据
- `GET /api/admin/analytics/health` - 分析系统健康
- `POST /api/admin/analytics/collect` - 收集测试数据

### 3. 日志分析系统

#### 📝 日志管理功能
- **多级别日志**: INFO、WARNING、ERROR、CRITICAL
- **日志收集**: 自动日志收集和分类
- **日志搜索**: 关键词搜索、时间范围过滤
- **错误分析**: 错误日志统计和趋势分析

#### 🔧 技术实现
- **结构化日志**: JSON格式日志存储
- **日志轮转**: 自动日志清理和归档
- **实时分析**: 实时日志流分析
- **告警集成**: 错误日志自动告警

#### 📡 API接口
- `GET /api/admin/logs/dashboard` - 日志分析仪表板
- `GET /api/admin/logs/search` - 日志搜索
- `GET /api/admin/logs/stats` - 日志统计

### 4. 告警通知系统

#### 🚨 告警功能
- **阈值告警**: CPU、内存、磁盘使用率告警
- **错误告警**: API错误率、系统异常告警
- **自定义规则**: 灵活的告警规则配置
- **通知渠道**: 邮件、短信、Webhook通知

#### 🔧 技术实现
- **规则引擎**: 灵活的告警规则配置
- **通知队列**: 异步通知处理
- **告警升级**: 告警级别和升级机制
- **冷却期**: 防止告警风暴的冷却机制

#### 📡 API接口
- `GET /api/admin/notifications/dashboard` - 通知仪表板
- `GET /api/admin/notifications/rules` - 告警规则管理
- `GET /api/admin/notifications/channels` - 通知渠道配置

## 🎛️ 监控仪表板

### 综合监控视图
- **系统概览**: 系统状态、健康评分、关键指标
- **性能趋势**: API性能趋势、响应时间图表
- **告警中心**: 活跃告警、告警历史、处理状态
- **日志摘要**: 错误日志统计、日志级别分布

### 实时数据展示
- **实时图表**: 动态更新的监控图表
- **状态指示器**: 系统健康状态指示灯
- **关键指标**: 重要指标的实时显示
- **告警提醒**: 实时告警弹窗和通知

## 📊 数据模型

### 系统指标模型
```python
class SystemMetric(Base):
    id: int
    metric_type: str        # system, api, application
    metric_name: str        # cpu_percent, memory_percent
    metric_value: float     # 指标值
    metric_unit: str        # %, MB, count
    timestamp: datetime     # 记录时间
```

### API指标模型
```python
class APIMetric(Base):
    id: int
    endpoint: str           # API端点
    method: str            # HTTP方法
    status_code: int       # 响应状态码
    response_time: float   # 响应时间(ms)
    timestamp: datetime    # 请求时间
```

### 系统告警模型
```python
class SystemAlert(Base):
    id: int
    alert_type: str        # threshold, error, custom
    severity: str          # low, medium, high, critical
    title: str             # 告警标题
    message: str           # 告警消息
    status: str            # active, resolved, suppressed
    created_at: datetime   # 创建时间
```

## 🔧 技术架构

### 监控数据流
```
系统资源 → psutil → 监控服务 → 数据库存储 → API接口 → 前端展示
API请求 → 中间件 → 性能收集 → 统计分析 → 仪表板展示
应用日志 → 日志服务 → 结构化存储 → 分析引擎 → 告警系统
```

### 核心组件
- **SystemMonitorService**: 系统监控核心服务
- **APIAnalyticsService**: API性能分析服务
- **LogAnalysisService**: 日志分析服务
- **NotificationService**: 告警通知服务
- **MonitoringMiddleware**: 性能监控中间件

## ⚡ 性能特性

### 高效数据收集
- **异步处理**: 非阻塞的数据收集和处理
- **批量操作**: 批量数据库写入优化
- **内存缓存**: 热点数据内存缓存
- **数据压缩**: 历史数据压缩存储

### 实时性保障
- **1秒更新**: 系统状态1秒间隔更新
- **流式处理**: 实时数据流处理
- **推送通知**: WebSocket实时数据推送
- **缓存优化**: 多级缓存提升响应速度

## 🔒 安全特性

### 访问控制
- **JWT认证**: 所有监控API需要认证
- **权限控制**: 基于RBAC的功能权限
- **数据隔离**: 敏感监控数据访问控制
- **审计日志**: 监控操作审计记录

### 数据安全
- **数据加密**: 敏感监控数据加密存储
- **传输安全**: HTTPS加密数据传输
- **访问日志**: 详细的访问日志记录
- **异常检测**: 异常访问模式检测

## 📈 监控指标

### 系统指标
- **CPU使用率**: 0-100%，告警阈值80%
- **内存使用率**: 0-100%，告警阈值85%
- **磁盘使用率**: 0-100%，告警阈值90%
- **网络流量**: MB/s，异常流量检测
- **进程数量**: 系统进程总数监控

### API指标
- **请求QPS**: 每秒请求数
- **平均响应时间**: 毫秒级响应时间
- **错误率**: 4xx/5xx错误比例
- **P95延迟**: 95%请求的响应时间
- **并发连接数**: 活跃连接数量

### 业务指标
- **IP查询量**: 每日IP查询统计
- **用户活跃度**: 管理员活跃统计
- **系统可用性**: 系统正常运行时间
- **数据质量**: 数据完整性评分

## 🎯 告警策略

### 阈值告警
- **CPU > 80%**: 中等级别告警
- **内存 > 85%**: 高级别告警
- **磁盘 > 90%**: 严重级别告警
- **错误率 > 5%**: API错误告警

### 智能告警
- **异常检测**: 基于历史数据的异常检测
- **趋势告警**: 指标趋势异常告警
- **关联告警**: 多指标关联分析告警
- **预测告警**: 基于趋势的预测性告警

## 🚀 使用指南

### 监控配置
1. 配置监控参数和阈值
2. 设置告警规则和通知渠道
3. 启用自动数据收集
4. 配置数据保留策略

### 日常运维
1. 查看监控仪表板
2. 分析性能趋势
3. 处理告警事件
4. 定期数据清理

### 故障排查
1. 检查系统健康状态
2. 分析错误日志
3. 查看性能指标异常
4. 追踪问题根因

## 📚 相关文档

- **API文档**: `/docs/backend_api_documentation.md`
- **部署指南**: `/docs/deployment_guide.md`
- **运维手册**: `/docs/operations_manual.md`
- **故障排查**: `/docs/troubleshooting_guide.md`
