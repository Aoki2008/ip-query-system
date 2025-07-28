# IP查询工具 - 容器化部署指南

## 📋 概述

本项目支持完整的Docker容器化部署，包括前端、后端、缓存和反向代理服务。

## 🏗️ 架构图

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   用户请求   │───▶│    Nginx    │───▶│   前端Vue3   │
└─────────────┘    │  (反向代理)  │    │  (静态资源)  │
                   └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  FastAPI    │───▶│    Redis    │
                   │  (主后端)    │    │   (缓存)    │
                   └─────────────┘    └─────────────┘
                          │
                   ┌─────────────┐
                   │  Flask API  │
                   │  (兼容后端)  │
                   └─────────────┘
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 一键部署

#### Linux/Mac
```bash
# 克隆项目
git clone <repository-url>
cd ip-query-tool

# 启动生产环境
chmod +x deploy.sh
./deploy.sh start prod

# 启动开发环境
./deploy.sh start dev
```

#### Windows
```cmd
# 克隆项目
git clone <repository-url>
cd ip-query-tool

# 启动生产环境
deploy.bat start prod

# 启动开发环境
deploy.bat start dev
```

### 手动部署

#### 1. 构建镜像
```bash
# 生产环境
docker-compose build

# 开发环境
docker-compose -f docker-compose.dev.yml build
```

#### 2. 启动服务
```bash
# 生产环境
docker-compose up -d

# 开发环境
docker-compose -f docker-compose.dev.yml up -d
```

#### 3. 验证部署
```bash
# 运行测试脚本
python test_deployment.py

# 或手动检查
curl http://localhost/health
```

## 📊 服务端口

### 生产环境
- **主入口**: http://localhost (Nginx反向代理)
- **前端**: http://localhost:8080 (Vue3应用)
- **FastAPI**: http://localhost:8000 (主后端API)
- **Flask API**: http://localhost:5000 (兼容后端)
- **Redis**: localhost:6379 (缓存服务)
- **Nginx状态**: http://localhost:8081/nginx_status
- **API文档**: http://localhost:8082/docs

### 开发环境
- **前端**: http://localhost:8080
- **FastAPI**: http://localhost:8000 (开发模式，支持热重载)
- **Redis**: localhost:6379
- **API文档**: http://localhost:8000/docs

## 🔧 配置说明

### 环境变量

#### FastAPI后端
```env
HOST=0.0.0.0
PORT=8000
DEBUG=false
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_ENABLED=true
LOG_LEVEL=INFO
GEOIP_DB_PATH=/app/data/GeoLite2-City.mmdb
```

#### Flask后端
```env
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
LOG_LEVEL=INFO
```

### 数据卷

- `redis_data`: Redis数据持久化
- `nginx_logs`: Nginx日志
- `./API/logs`: Flask API日志
- `./backend-fastapi/data`: GeoIP数据库

## 🛠️ 管理命令

### 部署脚本命令

```bash
# 启动服务
./deploy.sh start [prod|dev]

# 停止服务
./deploy.sh stop [prod|dev]

# 重启服务
./deploy.sh restart [prod|dev]

# 构建镜像
./deploy.sh build [prod|dev]

# 查看日志
./deploy.sh logs [prod|dev]

# 健康检查
./deploy.sh health [prod|dev]

# 清理资源
./deploy.sh cleanup [prod|dev]
```

### Docker Compose命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启特定服务
docker-compose restart [service_name]

# 扩展服务
docker-compose up -d --scale backend-fastapi=3

# 更新服务
docker-compose pull
docker-compose up -d
```

## 📈 监控和日志

### 服务监控

1. **Nginx状态**: http://localhost:8081/nginx_status
2. **容器状态**: `docker-compose ps`
3. **资源使用**: `docker stats`

### 日志查看

```bash
# 所有服务日志
docker-compose logs -f

# 特定服务日志
docker-compose logs -f backend-fastapi
docker-compose logs -f nginx

# 实时日志
docker-compose logs -f --tail=100
```

### 健康检查

所有服务都配置了健康检查：

```bash
# 检查所有服务健康状态
docker-compose ps

# 运行完整测试
python test_deployment.py
```

## 🔒 安全配置

### 生产环境安全

1. **SSL/TLS**: 编辑 `nginx/conf.d/ssl.conf` 启用HTTPS
2. **防火墙**: 限制不必要的端口访问
3. **用户权限**: 所有容器使用非root用户运行
4. **安全头**: Nginx配置了安全响应头

### 网络安全

- 使用Docker内部网络通信
- 限制外部访问端口
- 配置了请求频率限制

## 🚨 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :8000

# 修改端口映射
# 编辑 docker-compose.yml 中的 ports 配置
```

#### 2. 内存不足
```bash
# 检查内存使用
docker stats

# 清理未使用的镜像
docker system prune -a
```

#### 3. 服务启动失败
```bash
# 查看详细日志
docker-compose logs [service_name]

# 重新构建镜像
docker-compose build --no-cache [service_name]
```

#### 4. 数据库连接失败
```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping

# 重启Redis
docker-compose restart redis
```

### 调试模式

```bash
# 开发环境调试
docker-compose -f docker-compose.dev.yml up

# 进入容器调试
docker-compose exec backend-fastapi bash
docker-compose exec frontend sh
```

## 📦 备份和恢复

### 数据备份

```bash
# 备份Redis数据
docker-compose exec redis redis-cli BGSAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup/

# 备份日志
tar -czf logs_backup.tar.gz API/logs/ nginx_logs/
```

### 数据恢复

```bash
# 恢复Redis数据
docker-compose down
docker cp ./backup/dump.rdb $(docker-compose ps -q redis):/data/
docker-compose up -d
```

## 🔄 更新部署

### 滚动更新

```bash
# 拉取最新代码
git pull

# 重新构建并部署
./deploy.sh restart prod

# 验证更新
python test_deployment.py
```

### 零停机更新

```bash
# 使用蓝绿部署
docker-compose -f docker-compose.blue.yml up -d
# 切换流量
# 停止旧版本
docker-compose -f docker-compose.green.yml down
```

## 📞 支持

如遇到问题，请：

1. 查看日志: `docker-compose logs -f`
2. 运行测试: `python test_deployment.py`
3. 检查文档: 本文件和各服务的README
4. 提交Issue: 包含详细的错误信息和环境描述
