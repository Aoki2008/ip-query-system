# IP查询系统 - 企业级解决方案

一个完整的IP地址查询系统，包含API服务、管理后台和用户界面，支持高并发、多用户、API密钥管理等企业级功能。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IP查询工具     │    │    API系统      │    │   管理后台      │
│   (Next.js)     │◄──►│  (Node.js)      │◄──►│  (Laravel)      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MySQL + Redis │
                    │                 │
                    └─────────────────┘
```

## 📁 项目结构

```
ip-query-system/
├── api-system/          # Node.js API服务
├── admin-panel/         # Laravel管理后台
├── ip-tool/            # Next.js前端应用
├── database/           # 数据库文件
├── docs/              # 文档和配置
├── docker/            # Docker配置
└── deploy/            # 部署脚本
```

## 🚀 快速开始

### 环境要求
- Node.js 18+
- PHP 8.1+
- MySQL 8.0+
- Redis 7.0+
- Nginx 1.22+

### 一键部署（推荐）
```bash
# 克隆项目
git clone <repository-url>
cd ip-query-system

# 使用Docker Compose部署
docker-compose up -d

# 或使用部署脚本
chmod +x deploy/install.sh
./deploy/install.sh
```

### GitHub部署

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?style=for-the-badge&logo=github)](https://github.com/your-username/ip-query-system)

```bash
# 1. 克隆或Fork项目
git clone https://github.com/your-username/ip-query-system.git
cd ip-query-system

# 2. 一键上传到您的GitHub仓库
chmod +x upload-to-github.sh
./upload-to-github.sh

# 3. 使用Docker部署
docker-compose up -d
```

### 手动部署
详见 [部署文档](docs/deployment.md)

## 🔧 核心功能

### API系统
- ✅ IP地址查询接口
- ✅ API密钥认证
- ✅ 请求限流控制
- ✅ 调用统计记录
- ✅ 缓存优化

### 管理后台
- ✅ API密钥管理
- ✅ 用户管理
- ✅ 实时监控
- ✅ 调用统计
- ✅ 系统配置

### 用户界面
- ✅ 现代化UI设计
- ✅ 用户注册/登录
- ✅ API密钥申请
- ✅ 使用统计
- ✅ 批量查询

## 📊 性能特性

- **高并发**: 支持1000+ QPS
- **缓存优化**: Redis缓存热点数据
- **负载均衡**: 支持多实例部署
- **监控告警**: 实时性能监控

## 🔐 安全特性

- **API密钥认证**: 防止未授权访问
- **请求限流**: 防止恶意攻击
- **HTTPS强制**: 数据传输加密
- **IP白名单**: 管理后台访问控制

## 📖 文档

- [API文档](docs/api.md) - 完整的API接口说明
- [部署指南](docs/deployment.md) - 详细的部署步骤
- [配置说明](docs/configuration.md) - 系统配置参数
- [贡献指南](CONTRIBUTING.md) - 如何参与项目开发

## 🔄 CI/CD状态

![CI](https://github.com/your-username/ip-query-system/workflows/CI/CD%20Pipeline/badge.svg)

## 📦 快速开始

### 上传到GitHub

```bash
# 给脚本添加执行权限
chmod +x upload-to-github.sh

# 运行上传脚本
./upload-to-github.sh
```

脚本会自动：
- ✅ 初始化Git仓库
- ✅ 配置GitHub远程仓库
- ✅ 提交并推送代码
- ✅ 提供详细的操作指导

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与。

### 如何贡献

1. Fork 这个仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 🐛 问题反馈

如果您发现了Bug或有功能建议：

1. 查看 [现有Issues](https://github.com/your-username/ip-query-system/issues)
2. 创建 [新Issue](https://github.com/your-username/ip-query-system/issues/new)
3. 发送邮件到 support@example.com

## 📄 许可证

本项目采用 [MIT许可证](LICENSE) - 查看LICENSE文件了解详情。