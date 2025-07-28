# 配置说明

本文档详细说明IP查询系统的各项配置选项。

## 环境变量配置

### 数据库配置

```bash
# MySQL数据库配置
DB_HOST=mysql                    # 数据库主机地址
DB_PORT=3306                     # 数据库端口
DB_NAME=ip_query_system          # 数据库名称
DB_USER=ip_query_user            # 数据库用户名
DB_PASSWORD=your_password        # 数据库密码

# Redis配置
REDIS_HOST=redis                 # Redis主机地址
REDIS_PORT=6379                  # Redis端口
REDIS_PASSWORD=your_password     # Redis密码
REDIS_DB=0                       # Redis数据库编号
```

### 应用配置

```bash
# Node.js API服务
NODE_ENV=production              # 运行环境：development/production
PORT=3001                        # API服务端口
LOG_LEVEL=info                   # 日志级别：debug/info/warn/error

# Laravel管理后台
APP_ENV=production               # Laravel环境
APP_DEBUG=false                  # 调试模式
APP_KEY=base64:your_app_key      # Laravel应用密钥
APP_URL=http://localhost:8080    # 应用URL

# Next.js前端
NEXT_PUBLIC_API_URL=http://localhost:3001  # API服务地址
NEXT_PUBLIC_SITE_NAME=IP查询系统            # 网站名称
NEXTAUTH_URL=http://localhost:3000          # NextAuth URL
NEXTAUTH_SECRET=your_secret                 # NextAuth密钥
```

### 安全配置

```bash
# JWT配置
JWT_SECRET=your_jwt_secret       # JWT签名密钥
JWT_EXPIRES_IN=24h               # JWT过期时间

# 密码加密
BCRYPT_ROUNDS=12                 # bcrypt加密轮数

# 会话配置
SESSION_SECRET=your_session_secret  # 会话密钥
SESSION_LIFETIME=120             # 会话生命周期（分钟）
```

### MaxMind配置

```bash
# MaxMind许可证配置
MAXMIND_LICENSE_KEY=your_license_key  # MaxMind许可证密钥
MAXMIND_USER_ID=your_user_id          # MaxMind用户ID
```

### 限流配置

```bash
# 全局限流
GLOBAL_RATE_LIMIT=1000           # 全局每15分钟请求限制

# API限流
API_RATE_LIMIT_MINUTE=60         # API每分钟请求限制
API_RATE_LIMIT_DAY=1000          # API每日请求限制

# 游客限流
GUEST_RATE_LIMIT_DAY=20          # 游客每日请求限制
```

### 缓存配置

```bash
# 缓存设置
CACHE_TTL=3600                   # 默认缓存时间（秒）
IP_CACHE_TTL=3600                # IP查询结果缓存时间（秒）
```

### 邮件配置

```bash
# SMTP配置
SMTP_HOST=smtp.gmail.com         # SMTP服务器地址
SMTP_PORT=587                    # SMTP端口
SMTP_USER=your_email@gmail.com   # SMTP用户名
SMTP_PASSWORD=your_password      # SMTP密码
SMTP_FROM=noreply@yourdomain.com # 发件人地址

# 邮件队列
MAIL_QUEUE_ENABLED=true          # 是否启用邮件队列
```

### 文件上传配置

```bash
# 上传限制
UPLOAD_MAX_SIZE=10485760         # 最大上传文件大小（字节）
UPLOAD_ALLOWED_TYPES=.mmdb,.csv,.json  # 允许的文件类型
```

## Docker Compose配置

### 服务配置

```yaml
# MySQL服务配置
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: root_password
    MYSQL_DATABASE: ip_query_system
    MYSQL_USER: ip_query_user
    MYSQL_PASSWORD: user_password
  command: --default-authentication-plugin=mysql_native_password
    --innodb-buffer-pool-size=1G
    --innodb-log-file-size=256M
    --max-connections=1000

# Redis服务配置
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes 
    --requirepass redis_password
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
```

### 资源限制

```yaml
# 为服务设置资源限制
api-service:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M

admin-panel:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

## Nginx配置

### 基础配置

```nginx
# nginx.conf
worker_processes auto;
worker_connections 2048;

# 客户端配置
client_max_body_size 10M;
client_body_buffer_size 128k;

# 超时配置
proxy_connect_timeout 30s;
proxy_send_timeout 30s;
proxy_read_timeout 30s;
```

### 限流配置

```nginx
# 限流区域定义
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# 应用限流
location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://api_backend;
}
```

### SSL配置

```nginx
# HTTPS配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

## 数据库配置

### MySQL优化

```sql
-- 配置参数
SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
SET GLOBAL innodb_log_file_size = 268435456;      -- 256MB
SET GLOBAL max_connections = 1000;
SET GLOBAL query_cache_size = 67108864;           -- 64MB

-- 索引优化
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX idx_api_logs_api_key_created ON api_logs(api_key_id, created_at);
```

### Redis优化

```bash
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 监控配置

### 日志配置

```bash
# 日志级别
LOG_LEVEL=info

# 日志轮转
/var/log/ip-query/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

### 健康检查

```yaml
# Docker健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 安全配置

### 防火墙规则

```bash
# UFW配置
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### IP白名单

```nginx
# 管理后台IP限制
location /admin {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://admin_backend;
}
```

### 安全头配置

```nginx
# 安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

## 性能配置

### 缓存策略

```nginx
# 静态文件缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
}

# API响应缓存
location /api/ip/query {
    proxy_cache api_cache;
    proxy_cache_valid 200 1h;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

### 压缩配置

```nginx
# Gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss;
```

## 备份配置

### 自动备份

```bash
# crontab配置
# 每天凌晨2点备份
0 2 * * * /opt/ip-query-system/deploy/backup.sh

# 每周日凌晨3点清理日志
0 3 * * 0 /opt/ip-query-system/deploy/cleanup.sh
```

### 备份保留策略

```bash
# 备份保留天数
RETENTION_DAYS=7

# 备份存储位置
BACKUP_DIR="/opt/ip-query-system/backups"

# 远程备份（可选）
REMOTE_BACKUP_HOST="backup.example.com"
REMOTE_BACKUP_PATH="/backups/ip-query-system"
```

## 开发环境配置

### 开发模式

```bash
# 开发环境变量
NODE_ENV=development
APP_DEBUG=true
LOG_LEVEL=debug

# 热重载
CHOKIDAR_USEPOLLING=true
WATCHPACK_POLLING=true
```

### 调试配置

```bash
# API调试
DEBUG=ip-query:*

# Laravel调试
APP_DEBUG=true
LOG_CHANNEL=single
LOG_LEVEL=debug
```

## 故障排除

### 常见配置问题

1. **数据库连接失败**
   - 检查数据库密码是否正确
   - 确认数据库服务是否启动
   - 验证网络连接

2. **Redis连接失败**
   - 检查Redis密码配置
   - 确认Redis服务状态
   - 验证端口配置

3. **API请求失败**
   - 检查CORS配置
   - 验证API密钥设置
   - 确认限流配置

### 配置验证

```bash
# 验证配置文件语法
docker-compose config

# 测试Nginx配置
docker-compose exec nginx nginx -t

# 检查环境变量
docker-compose exec api-service env | grep -E "(DB_|REDIS_|JWT_)"
```

## 配置模板

### 生产环境模板

```bash
# .env.production
NODE_ENV=production
APP_ENV=production
APP_DEBUG=false

# 使用强密码
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 64)

# 配置真实域名
FRONTEND_DOMAIN=ip.yourdomain.com
API_DOMAIN=api.yourdomain.com
ADMIN_DOMAIN=admin.yourdomain.com

# 启用安全功能
HTTPS_ONLY=true
SECURE_COOKIES=true
```

### 开发环境模板

```bash
# .env.development
NODE_ENV=development
APP_ENV=local
APP_DEBUG=true

# 使用简单密码（仅开发环境）
DB_PASSWORD=password
REDIS_PASSWORD=password
JWT_SECRET=development_secret

# 本地域名
FRONTEND_DOMAIN=localhost
API_DOMAIN=localhost
ADMIN_DOMAIN=localhost
```

通过合理配置这些参数，可以确保IP查询系统在不同环境下稳定、安全、高效地运行。
