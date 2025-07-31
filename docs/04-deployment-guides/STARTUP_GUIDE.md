# 🚀 IP查询系统启动指南

## 📋 快速启动概览

本指南提供多种启动方式，选择最适合您的方式：

1. **🐳 Docker启动** - 推荐，一键启动所有服务
2. **📜 脚本启动** - 使用预配置的启动脚本
3. **🔧 手动启动** - 逐个启动各个服务
4. **⚙️ 开发模式** - 开发环境启动

## 🎯 方式一：Docker启动（推荐）

### 环境要求
- Docker 24.0+
- Docker Compose 2.0+

### 快速启动
```bash
# 生产环境
docker-compose up -d

# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 停止服务
```bash
docker-compose down
```

## 🎯 方式二：脚本启动

### Windows用户

#### 一键启动所有服务
```cmd
scripts\start_all.bat
```

#### 分别启动各服务
```cmd
# 启动后端API
scripts\start_fastapi.bat

# 启动用户前端
scripts\start_frontend.bat

# 启动管理后台
scripts\start_admin.bat
```

### Linux/macOS用户

#### 启动后端服务
```bash
./scripts/start_fastapi.sh
```

#### 启动前端服务
```bash
# 用户前端
cd frontend-vue3
npm install
npm run dev

# 管理后台
cd frontend-admin
npm install
npm run dev
```

## 🎯 方式三：手动启动

### 1. 启动后端API服务

#### 环境准备
```bash
cd backend-fastapi
pip install -r requirements.txt
```

#### 下载IP数据库
1. 访问 [MaxMind官网](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
2. 下载 `GeoLite2-City.mmdb` 文件
3. 放置到 `backend-fastapi/data/` 目录

#### 启动服务
```bash
cd backend-fastapi
python main.py
```

### 2. 启动用户前端

#### 环境准备
```bash
cd frontend-vue3
npm install
```

#### 启动服务
```bash
npm run dev
```

### 3. 启动管理后台

#### 环境准备
```bash
cd frontend-admin
npm install
```

#### 启动服务
```bash
npm run dev
```

## 📊 服务地址和端口

| 服务名称 | 地址 | 端口 | 说明 |
|---------|------|------|------|
| **后端API** | http://localhost:8000 | 8000 | FastAPI服务 |
| **API文档** | http://localhost:8000/docs | 8000 | Swagger文档 |
| **用户前端** | http://localhost:5173 | 5173 | Vue3用户界面 |
| **管理后台** | http://localhost:5174 | 5174 | Vue3管理界面 |

## 🔐 默认账户信息

### 管理后台登录
- **用户名**: `admin`
- **密码**: `admin123`
- **权限**: 超级管理员

> ⚠️ **安全提示**: 生产环境请立即修改默认密码！

## 🛠️ 环境要求

### 基础环境
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最少4GB，推荐8GB+
- **磁盘空间**: 最少2GB可用空间

### 开发环境
- **Node.js**: 18.0+ (前端开发)
- **Python**: 3.11+ (后端开发)
- **Git**: 2.30+ (版本控制)

### 生产环境
- **Docker**: 24.0+ (容器化部署)
- **Docker Compose**: 2.0+ (服务编排)

## 🔍 启动验证

### 检查服务状态
```bash
# 检查后端API
curl http://localhost:8000/health

# 检查前端服务
curl http://localhost:5173

# 检查管理后台
curl http://localhost:5174
```

### 功能测试
1. **后端API测试**
   - 访问 http://localhost:8000/docs
   - 测试IP查询接口

2. **前端功能测试**
   - 访问 http://localhost:5173
   - 测试IP查询功能

3. **管理后台测试**
   - 访问 http://localhost:5174
   - 使用默认账户登录

## ⚠️ 常见问题

### 问题1: 端口被占用
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS

# 终止进程
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/macOS
```

### 问题2: Python依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 问题3: Node.js依赖安装失败
```bash
# 清理缓存
npm cache clean --force

# 使用国内镜像
npm install --registry https://registry.npmmirror.com
```

### 问题4: Docker启动失败
```bash
# 检查Docker状态
docker --version
docker-compose --version

# 重新构建镜像
docker-compose build --no-cache
```

## 🔧 开发模式启动

### 热重载开发
```bash
# 后端热重载
cd backend-fastapi
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端热重载
cd frontend-vue3
npm run dev

# 管理后台热重载
cd frontend-admin
npm run dev
```

### 调试模式
```bash
# Python调试模式
export DEBUG=True
python main.py

# Node.js调试模式
npm run dev -- --debug
```

## 📋 启动检查清单

- [ ] 环境要求满足
- [ ] 依赖包安装完成
- [ ] IP数据库文件就位
- [ ] 端口没有冲突
- [ ] 服务启动成功
- [ ] 功能测试通过
- [ ] 日志输出正常

---

**💡 提示**: 建议首次使用Docker方式启动，确保环境一致性。开发时可以使用脚本方式启动以便调试。
