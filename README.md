# 🌐 IP查询系统 - 现代化企业级解决方案

[![Version](https://img.shields.io/badge/version-v4.0-blue.svg)](https://github.com/Aoki2008/ip-query-system)
[![Tech Stack](https://img.shields.io/badge/tech-Vue3%2BFastAPI-green.svg)](#技术栈)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-生产就绪-brightgreen.svg)](#项目状态)

> 一个现代化的企业级IP地址查询系统，采用Vue3+FastAPI技术栈，提供高性能的IP地理位置查询服务和完整的管理后台。

## 🎯 项目特色

- **🚀 现代化技术栈**: Vue3 + TypeScript + FastAPI + Docker
- **⚡ 高性能**: 异步处理，Redis缓存，毫秒级响应
- **🛡️ 企业级安全**: JWT认证，RBAC权限，多层防护
- **📊 完整管理**: 用户管理，系统监控，数据分析
- **🎨 优秀体验**: 响应式设计，玻璃拟态风格，主题切换
- **🐳 容器化部署**: Docker一键部署，生产环境就绪

## 📋 功能概览

### 🔍 IP查询功能
- **单个查询**: 输入IP地址获取详细地理位置信息
- **批量查询**: 支持文件导入，批量处理大量IP地址
- **查询历史**: 保存查询记录，支持历史查看和管理
- **数据导出**: 支持CSV、JSON、Excel多种格式导出
- **实时查询**: 毫秒级响应，支持高并发访问

### 🛡️ 管理后台
- **用户管理**: 管理员账户管理，权限分配
- **系统监控**: 实时性能监控，资源使用统计
- **数据分析**: 查询统计，热门IP分析，地理分布
- **日志管理**: 系统日志查看，操作审计
- **通知系统**: 告警通知，邮件提醒
- **系统配置**: 参数配置，缓存管理，性能优化

## 🛠️ 技术栈

### 前端技术
- **框架**: Vue 3.4+ + TypeScript 5.0+
- **构建**: Vite 5.0+ (热更新、快速构建)
- **UI库**: Element Plus (管理后台)
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP**: Axios
- **样式**: CSS3 + 玻璃拟态设计

### 后端技术
- **框架**: FastAPI 0.115+ + Python 3.11+
- **异步**: asyncio + uvicorn
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0
- **缓存**: Redis 7.0+
- **认证**: JWT + bcrypt
- **地理数据**: MaxMind GeoLite2

### 基础设施
- **容器**: Docker + Docker Compose
- **代理**: Nginx (反向代理、负载均衡)
- **监控**: 自建监控系统
- **日志**: 结构化日志 + 聚合分析

## 🚀 快速开始

### 环境要求
- **Node.js** 18+ (前端开发)
- **Python** 3.11+ (后端服务)
- **Docker** 24.0+ (容器部署)
- **Redis** 7.0+ (缓存服务)

### 方式一：Docker部署（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/Aoki2008/ip-query-system.git
   cd ip-query-system
   ```

2. **下载IP数据库**
   - 访问 [MaxMind官网](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
   - 下载 `GeoLite2-City.mmdb` 文件
   - 将文件放置在 `backend-fastapi/data/` 目录下

3. **启动服务**
   ```bash
   # 生产环境
   docker-compose up -d
   
   # 开发环境
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **访问应用**
   - **用户前端**: http://localhost:5173
   - **管理后台**: http://localhost:5174
   - **API文档**: http://localhost:8000/docs

### 方式二：本地开发

1. **启动后端服务**
   ```bash
   cd backend-fastapi
   pip install -r requirements.txt
   python main.py
   ```

2. **启动用户前端**
   ```bash
   cd frontend-vue3
   npm install
   npm run dev
   ```

3. **启动管理后台**
   ```bash
   cd frontend-admin
   npm install
   npm run dev
   ```

## 📊 服务地址

| 服务名称 | 地址 | 端口 | 说明 |
|---------|------|------|------|
| **用户前端** | http://localhost:5173 | 5173 | IP查询主界面 |
| **管理后台** | http://localhost:5174 | 5174 | 系统管理界面 |
| **后端API** | http://localhost:8000 | 8000 | RESTful API服务 |
| **API文档** | http://localhost:8000/docs | 8000 | Swagger文档 |

## 🔐 默认账户

### 管理后台登录
- **用户名**: `admin`
- **密码**: `admin123`
- **权限**: 超级管理员

> ⚠️ **安全提示**: 生产环境请立即修改默认密码！

## 📁 项目结构

```
📦 IP查询系统
├── 🌐 frontend-vue3/          # 用户前端 (Vue3+TS)
├── 🛡️ frontend-admin/         # 管理后台 (Vue3+Element Plus)
├── 🔧 backend-fastapi/        # 后端API (FastAPI)
├── ⚙️ config/                # 配置文件
├── 🛠️ scripts/               # 工具脚本
│   ├── auto-backup.ps1       # 自动备份脚本
│   ├── smart-backup.ps1      # 智能备份脚本
│   ├── schedule-backup.ps1   # 定时备份脚本
│   └── backup-config.json    # 备份配置文件
├── 📚 docs/                  # 项目文档
│   └── backup-guide.md       # 备份使用指南
├── 💾 data/                  # 数据文件
├── 📋 配置文件
└── backup.bat                # 快速备份批处理
```

## 📦 自动备份功能

### 🚀 快速备份
```bash
# 使用批处理文件（推荐）
backup.bat

# 使用PowerShell脚本
powershell -ExecutionPolicy Bypass -File "scripts\auto-backup.ps1"
```

### ⏰ 定时备份
```powershell
# 设置每天23:00自动备份
powershell -ExecutionPolicy Bypass -File "scripts\schedule-backup.ps1"
```

### 🤖 智能备份
```powershell
# 基于配置文件的智能备份
powershell -ExecutionPolicy Bypass -File "scripts\smart-backup.ps1"
```

详细使用说明请查看：[备份使用指南](docs/backup-guide.md)

## 📚 文档资源

- **📖 项目架构**: [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)
- **📋 任务跟踪**: [docs/01-project-overview/Aotd.md](docs/01-project-overview/Aotd.md)
- **🔧 部署指南**: [docs/04-deployment-guides/DEPLOYMENT.md](docs/04-deployment-guides/DEPLOYMENT.md)
- **📦 备份指南**: [docs/backup-guide.md](docs/backup-guide.md)
- **📝 开发日志**: [log.md](log.md)
- **🔗 API文档**: http://localhost:8000/docs (启动后访问)

## 🎯 项目状态

- **✅ 开发状态**: 100% 完成
- **✅ 功能测试**: 全部通过
- **✅ 生产部署**: 就绪可用
- **✅ 文档完整**: 齐全详细
- **🚀 版本**: v4.0 (现代化重构版)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **项目地址**: https://github.com/Aoki2008/ip-query-system
- **问题反馈**: [GitHub Issues](https://github.com/Aoki2008/ip-query-system/issues)
- **开发者**: Aoki2008

---

**🎉 感谢使用IP查询系统！如果觉得有用，请给个 ⭐ Star！**

*最后更新: 2025-07-31 | 版本: v4.0 | 状态: 生产就绪 ✅*
