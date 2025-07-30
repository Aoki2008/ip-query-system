# 🌐 IP查询工具 - 纯净高效的网络工具

一个专注于IP地址查询的轻量级工具，采用现代化的Vue3 + FastAPI技术栈，提供简洁高效的IP地理位置查询服务。

## 🎯 项目定位

**专业的IP地理位置查询工具** - 无需注册，即查即用，专注核心功能。

## 🌟 核心特色

- 🔍 **专业查询** - 单个IP查询和批量IP查询（最多100个）
- ⚡ **高性能** - FastAPI异步架构，支持高并发查询
- 🎨 **现代化UI** - Vue3响应式设计，支持深色/浅色主题切换
- 📱 **全设备适配** - 完美适配桌面、平板和移动设备
- 🚀 **轻量化** - 纯净架构，专注IP查询核心功能
- 📊 **数据导入导出** - 支持TXT/CSV导入，多格式导出
- 🐳 **容器化部署** - Docker一键部署，生产环境就绪

## 🏗️ 项目架构

```
ip-query-system/
├── frontend-vue3/          # Vue3前端应用
│   ├── src/                # 源代码
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── assets/         # 静态资源
│   │   └── App.vue         # 根组件
│   ├── dist/               # 构建输出
│   ├── package.json        # 前端依赖
│   └── vite.config.ts      # Vite配置
├── backend-fastapi/        # FastAPI后端服务
│   ├── app/                # 应用代码
│   │   ├── api/            # API路由
│   │   ├── services/       # 业务服务
│   │   ├── models/         # 数据模型
│   │   └── main.py         # 应用入口
│   ├── main.py             # 服务启动文件
│   └── requirements.txt    # Python依赖
├── API/                    # IP地理位置数据库
│   └── GeoLite2-City.mmdb  # MaxMind数据库文件
├── docs/                   # 项目文档
│   ├── README.md           # 项目说明
│   ├── log.md              # 开发日志
│   └── Aotd.md             # 任务跟踪
├── docker-compose.yml      # Docker编排配置
├── Dockerfile.frontend     # 前端Docker配置
├── Dockerfile.backend      # 后端Docker配置
└── .gitignore              # Git忽略配置
```

## 🚀 快速开始

### 环境要求

- **Node.js** 16+ (前端开发)
- **Python** 3.8+ (后端服务)
- **现代浏览器** (Chrome、Firefox、Safari、Edge等)

### 方式一：Docker部署（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/Aoki2008/ip-query-system.git
   cd ip-query-system
   ```

2. **下载IP数据库文件**
   - 访问 [MaxMind官网](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
   - 下载 `GeoLite2-City.mmdb` 文件
   - 将文件放置在 `API/` 目录下

3. **一键启动**
   ```bash
   docker-compose up -d
   ```

4. **访问应用**
   - 前端地址: http://localhost:8080
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

### 方式二：本地开发

1. **启动后端服务**
   ```bash
   cd backend-fastapi
   pip install -r requirements.txt
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **启动前端服务**
   ```bash
   cd frontend-vue3
   npm install
   npm run dev
   # 或构建后启动
   npm run build
   cd dist && python -m http.server 8080
   ```

3. **访问应用**
   - 开发模式: http://localhost:5173 (Vite开发服务器)
   - 生产模式: http://localhost:8080 (构建后的静态文件)

## 📊 核心功能

### IP查询服务
- **单个查询**: 快速查询单个IP地址的详细地理信息
- **批量查询**: 支持最多100个IP地址的批量查询
- **实时反馈**: 查询进度显示和状态反馈
- **高性能**: FastAPI异步架构，支持高并发

### 数据导入导出
- **导入格式**: 支持TXT/CSV文件导入，拖拽上传
- **导出格式**: 支持CSV/JSON/Excel多种格式导出
- **文件限制**: 最大5MB，最多100个IP地址
- **编码支持**: UTF-8编码，完美支持中文

### 地理信息展示
- **基础信息**: 国家/地区、城市、邮编
- **位置坐标**: 纬度/经度、时区信息
- **网络信息**: ISP提供商、精度半径
- **查询记录**: 自动保存查询历史

## 📡 API接口

### 健康检查
```http
GET /api/health
Response: {"status": "healthy", "message": "IP查询API服务运行正常"}
```

### 单个IP查询
```http
GET /api/query-ip?ip=8.8.8.8
Response: {
  "ip": "8.8.8.8",
  "country": "United States",
  "region": "未知",
  "city": "未知",
  "latitude": 37.751,
  "longitude": -97.822,
  "timezone": "America/Chicago",
  "isp": "未知"
}
```

### 批量IP查询
```http
POST /api/query-batch
Content-Type: application/json
Body: {"ips": ["8.8.8.8", "114.114.114.114"]}

Response: {
  "total": 2,
  "results": [...]
}
```

## 🛠️ 技术栈

### 前端技术
- **Vue 3** - 现代化的渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript超集
- **Vite** - 快速的前端构建工具
- **Vue Router** - 官方路由管理器
- **CSS3** - 现代化样式，支持深色/浅色主题

### 后端技术
- **FastAPI** - 现代化的Python Web框架
- **Python 3.8+** - 主要编程语言
- **Uvicorn** - ASGI服务器
- **GeoIP2** - IP地理位置查询库
- **MaxMind GeoLite2** - IP地理位置数据库

### 部署技术
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排
- **Nginx** - 反向代理和静态文件服务

## 🎨 界面特色

### 现代化设计
- **响应式布局** - 完美适配各种设备尺寸
- **主题切换** - 支持深色/浅色主题无缝切换
- **动画效果** - 丰富的交互动画和状态反馈
- **玻璃拟态** - 现代化的半透明设计语言

### 用户体验
- **直观操作** - 简洁明了的操作界面
- **实时反馈** - 查询进度和状态实时显示
- **错误处理** - 友好的错误提示和处理机制
- **无障碍访问** - 支持键盘导航和屏幕阅读器

## 🔧 开发说明

### 项目结构

#### 前端 (frontend-vue3/)
- `src/components/` - 可复用的Vue组件
- `src/views/` - 页面级组件
- `src/router/` - 路由配置
- `src/assets/` - 静态资源文件

#### 后端 (backend-fastapi/)
- `app/api/` - API路由定义
- `app/services/` - 业务逻辑服务
- `app/models/` - 数据模型定义
- `main.py` - 应用入口文件

### 开发环境配置

1. **前端开发**
   ```bash
   cd frontend-vue3
   npm install
   npm run dev
   ```

2. **后端开发**
   ```bash
   cd backend-fastapi
   pip install -r requirements.txt
   python -m uvicorn main:app --reload
   ```

### API配置
- 前端API地址配置在 `frontend-vue3/src/config/api.ts`
- 后端CORS配置在 `backend-fastapi/app/main.py`

## 📝 注意事项

1. **数据库文件** - 必须下载并放置GeoLite2-City.mmdb文件
2. **端口配置** - 确保8000和8080端口未被占用
3. **网络访问** - 确保前后端服务可以正常通信
4. **浏览器兼容** - 建议使用现代浏览器以获得最佳体验

## 🐛 故障排除

### 常见问题

1. **服务启动失败**
   - 检查端口是否被占用
   - 确认依赖是否正确安装
   - 验证数据库文件是否存在

2. **API连接失败**
   - 检查后端服务是否正常启动
   - 确认防火墙设置
   - 验证API地址配置

3. **查询结果异常**
   - 可能是私有IP地址
   - 数据库中未收录该IP
   - 网络连接问题

### 调试技巧
- 查看浏览器开发者工具的Console和Network标签
- 检查后端服务的日志输出
- 访问 `/api/health` 端点检查API状态

## 🔮 项目历程

### 回溯说明
本项目已回溯到用户中心开发前的纯净状态，专注于IP查询核心功能：

- ✅ **移除功能**: 用户注册、登录、认证系统
- ✅ **保留功能**: IP查询、批量查询、数据导入导出
- ✅ **技术升级**: 从Flask升级到FastAPI，从原生JS升级到Vue3
- ✅ **架构优化**: 前后端分离，容器化部署

### 技术演进
- **v1.0** - 基础IP查询功能
- **v2.0** - 前后端分离重构
- **v3.0** - Vue3 + FastAPI现代化重构
- **v3.1** - 项目回溯，专注核心功能

## 🤝 贡献指南

1. Fork 项目到个人仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系方式

- **项目地址**: https://github.com/Aoki2008/ip-query-system
- **问题反馈**: [Issues页面](https://github.com/Aoki2008/ip-query-system/issues)
- **功能建议**: [Discussions页面](https://github.com/Aoki2008/ip-query-system/discussions)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **MaxMind** - 提供GeoLite2地理位置数据库
- **FastAPI** - 现代化的Python Web框架
- **Vue.js** - 渐进式JavaScript框架
- **开源社区** - 提供的各种工具和库支持

---

**🌐 IP查询工具** - 专注IP查询，简洁高效 ✨
