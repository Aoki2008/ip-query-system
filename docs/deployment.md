# 部署指南

本文档详细介绍如何部署IP查询系统到生产环境。

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB | 50GB+ |
| 网络 | 10Mbps | 100Mbps+ |

### 软件要求

- **操作系统**: CentOS 7+, Ubuntu 18.04+, Debian 9+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **域名**: 建议使用独立域名
- **SSL证书**: 生产环境必须

## 快速部署

### 1. 一键安装脚本

```bash
# 下载安装脚本
wget https://raw.githubusercontent.com/example/ip-query-system/main/deploy/install.sh

# 赋予执行权限
chmod +x install.sh

# 运行安装脚本
sudo ./install.sh
```

### 2. 手动部署

#### 2.1 克隆项目

```bash
git clone https://github.com/example/ip-query-system.git
cd ip-query-system
```

#### 2.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env
```

重要配置项：

```bash
# 数据库密码（自动生成）
DB_PASSWORD=your_secure_password

# Redis密码（自动生成）
REDIS_PASSWORD=your_redis_password

# JWT密钥（自动生成）
JWT_SECRET=your_jwt_secret

# 域名配置
FRONTEND_DOMAIN=ip.yourdomain.com
API_DOMAIN=api.yourdomain.com
ADMIN_DOMAIN=admin.yourdomain.com

# MaxMind许可证密钥
MAXMIND_LICENSE_KEY=your_license_key
```

#### 2.3 下载MaxMind数据库

```bash
# 创建数据目录
mkdir -p data

# 下载GeoLite2-City数据库
# 需要在MaxMind官网注册并获取许可证密钥
wget "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=YOUR_LICENSE_KEY&suffix=tar.gz" -O GeoLite2-City.tar.gz

# 解压并移动到指定位置
tar -xzf GeoLite2-City.tar.gz
mv GeoLite2-City_*/GeoLite2-City.mmdb data/
```

#### 2.4 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 2.5 初始化数据库

```bash
# 等待MySQL启动完成
sleep 30

# 运行数据库迁移
docker-compose exec admin-panel php artisan migrate --force

# 运行数据填充
docker-compose exec admin-panel php artisan db:seed --force
```

## 域名和SSL配置

### 1. 域名解析

将以下域名解析到服务器IP：

- `ip.yourdomain.com` - 前端应用
- `api.yourdomain.com` - API服务
- `admin.yourdomain.com` - 管理后台

### 2. SSL证书配置

#### 使用Let's Encrypt（推荐）

```bash
# 安装certbot
sudo apt-get install certbot

# 申请证书
sudo certbot certonly --standalone -d ip.yourdomain.com -d api.yourdomain.com -d admin.yourdomain.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/ip.yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/ip.yourdomain.com/privkey.pem nginx/ssl/key.pem

# 设置权限
sudo chown root:root nginx/ssl/*.pem
sudo chmod 600 nginx/ssl/*.pem
```

#### 配置自动续期

```bash
# 添加crontab任务
sudo crontab -e

# 添加以下行（每月1号凌晨2点检查续期）
0 2 1 * * /usr/bin/certbot renew --quiet && docker-compose restart nginx
```

### 3. 启用HTTPS

编辑 `nginx/conf.d/default.conf`，取消HTTPS配置的注释：

```nginx
# 取消注释HTTPS重定向
server {
    listen 80;
    server_name ip.yourdomain.com api.yourdomain.com admin.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# 取消注释HTTPS配置
server {
    listen 443 ssl http2;
    server_name ip.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... 其他配置
}
```

重启Nginx：

```bash
docker-compose restart nginx
```

## 性能优化

### 1. 数据库优化

编辑 `docker-compose.yml` 中的MySQL配置：

```yaml
mysql:
  command: --default-authentication-plugin=mysql_native_password
    --innodb-buffer-pool-size=1G
    --innodb-log-file-size=256M
    --max-connections=1000
    --query-cache-size=64M
```

### 2. Redis优化

```yaml
redis:
  command: redis-server --appendonly yes 
    --requirepass redis_pass_123
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
```

### 3. Nginx优化

编辑 `nginx/nginx.conf`：

```nginx
worker_processes auto;
worker_connections 2048;

# 启用HTTP/2
listen 443 ssl http2;

# 启用Brotli压缩（如果支持）
brotli on;
brotli_comp_level 6;
```

## 监控和日志

### 1. 日志管理

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api-service
docker-compose logs -f admin-panel
docker-compose logs -f frontend

# 日志轮转配置
sudo vim /etc/logrotate.d/docker-compose
```

### 2. 监控配置

#### 系统监控

```bash
# 安装htop
sudo apt-get install htop

# 监控系统资源
htop

# 监控磁盘使用
df -h

# 监控网络连接
netstat -tulpn
```

#### 应用监控

```bash
# 监控Docker容器
docker stats

# 监控数据库连接
docker-compose exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 监控Redis状态
docker-compose exec redis redis-cli info
```

### 3. 健康检查

创建健康检查脚本：

```bash
#!/bin/bash
# health-check.sh

# 检查前端应用
curl -f http://localhost:3000/api/health || exit 1

# 检查API服务
curl -f http://localhost:3001/health || exit 1

# 检查管理后台
curl -f http://localhost:8080/health || exit 1

echo "All services are healthy"
```

## 备份和恢复

### 1. 数据库备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/ip-query-system/backups"

# 备份MySQL数据库
docker-compose exec mysql mysqldump -u root -p$DB_PASSWORD ip_query_system > $BACKUP_DIR/mysql_$DATE.sql

# 备份Redis数据
docker-compose exec redis redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh
```

### 2. 自动备份

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/ip-query-system/backup.sh
```

### 3. 数据恢复

```bash
# 恢复MySQL数据库
docker-compose exec mysql mysql -u root -p$DB_PASSWORD ip_query_system < backups/mysql_20240101_020000.sql

# 恢复Redis数据
docker-compose stop redis
cp backups/redis_20240101_020000.rdb redis_data/dump.rdb
docker-compose start redis
```

## 安全配置

### 1. 防火墙配置

```bash
# 安装ufw
sudo apt-get install ufw

# 默认策略
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许SSH
sudo ufw allow ssh

# 允许HTTP和HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 启用防火墙
sudo ufw enable
```

### 2. 安全加固

```bash
# 修改默认密码
docker-compose exec admin-panel php artisan tinker
# 在tinker中执行：
# User::where('email', 'admin@example.com')->first()->update(['password' => Hash::make('new_password')]);

# 禁用不必要的端口
# 编辑docker-compose.yml，移除不需要暴露的端口

# 配置IP白名单（管理后台）
# 编辑nginx/conf.d/default.conf
```

## 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 查看详细日志
   docker-compose logs service_name
   
   # 检查端口占用
   netstat -tulpn | grep :port
   ```

2. **数据库连接失败**
   ```bash
   # 检查MySQL状态
   docker-compose exec mysql mysql -u root -p
   
   # 重置数据库密码
   docker-compose exec mysql mysql -u root -p -e "ALTER USER 'root'@'%' IDENTIFIED BY 'new_password';"
   ```

3. **API请求失败**
   ```bash
   # 检查API服务日志
   docker-compose logs api-service
   
   # 测试API连接
   curl -X GET "http://localhost:3001/health"
   ```

### 性能问题

1. **响应时间慢**
   - 检查数据库查询性能
   - 优化Redis缓存配置
   - 增加服务器资源

2. **内存使用过高**
   - 调整Docker容器内存限制
   - 优化应用程序内存使用
   - 配置swap空间

## 更新升级

### 1. 应用更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build --no-cache

# 滚动更新
docker-compose up -d
```

### 2. 数据库迁移

```bash
# 运行新的迁移
docker-compose exec admin-panel php artisan migrate
```

### 3. 零停机更新

```bash
# 使用蓝绿部署
# 1. 部署新版本到备用环境
# 2. 切换负载均衡器
# 3. 停止旧版本
```

## 联系支持

如遇到部署问题，请联系：

- **技术支持**: support@example.com
- **文档**: https://docs.example.com
- **GitHub Issues**: https://github.com/example/ip-query-system/issues
