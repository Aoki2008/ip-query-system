# IP查询工具 - 现代化网络工具

一个功能完整的IP地址查询工具，采用前后端分离架构设计，具有现代化UI界面和丰富的功能特性。

## 🌟 项目特色

- 🎨 **现代化设计** - 支持深色/浅色主题切换，玻璃拟态设计风格
- 🔍 **智能查询** - 单个IP查询和批量IP查询（最多100个）
- 📊 **数据导入导出** - 支持TXT/CSV导入，CSV/JSON/Excel导出
- 📱 **响应式设计** - 完美适配桌面、平板和移动设备
- 🚀 **前后端分离** - 清晰的架构，易于维护和扩展
- 🎯 **二级导航** - 层级化的下拉菜单导航系统
- ⚡ **实时反馈** - 查询进度显示和状态反馈

## 🏗️ 项目架构

```
ip-query-tool/
├── IP查询工具/              # 前端应用
│   ├── assets/             # 静态资源（图标、图片等）
│   ├── css/                # 样式文件
│   │   └── style.css       # 主样式文件
│   ├── js/                 # JavaScript文件
│   │   └── script.js       # 主逻辑文件
│   ├── index.html          # 首页
│   ├── ip-lookup.html      # IP查询页面
│   ├── guide.html          # 使用指南
│   ├── faq.html            # 常见问题
│   ├── about.html          # 关于我们
│   └── help.html           # 帮助页面
├── API/                    # 后端API服务
│   ├── api/                # API接口模块
│   │   └── ip_service.py   # IP查询服务
│   ├── utils/              # 工具类
│   │   └── validators.py   # 验证工具
│   ├── models/             # 数据模型
│   ├── app.py              # Flask应用主文件
│   ├── start.py            # 后端启动脚本
│   ├── requirements.txt    # Python依赖
│   └── GeoLite2-City.mmdb  # IP地理位置数据库
├── start_backend.bat       # Windows后端启动脚本
├── start_frontend.bat      # Windows前端启动脚本
├── start_backend.sh        # Linux/Mac后端启动脚本
├── start_frontend.sh       # Linux/Mac前端启动脚本
└── README.md               # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 现代浏览器（Chrome、Firefox、Safari、Edge等）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd ip-query-tool
   ```

2. **下载IP数据库文件**
   - 访问 [MaxMind官网](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
   - 下载 `GeoLite2-City.mmdb` 文件
   - 将文件放置在 `API/` 目录下

3. **启动后端服务**
   
   **Windows:**
   ```cmd
   双击运行 start_backend.bat
   ```
   
   **Linux/Mac:**
   ```bash
   ./start_backend.sh
   ```
   
   或手动启动：
   ```bash
   cd API
   pip install -r requirements.txt
   python start.py
   ```

4. **启动前端服务**
   
   **Windows:**
   ```cmd
   双击运行 start_frontend.bat
   ```
   
   **Linux/Mac:**
   ```bash
   ./start_frontend.sh
   ```
   
   或手动启动：
   ```bash
   cd IP查询工具
   python start.py
   ```

5. **访问应用**
   - 前端地址: http://localhost:3000
   - 后端API: http://localhost:5000/api
   - 浏览器会自动打开前端页面

## �📤 导入导出功能

### 数据导入
支持多种方式导入IP地址列表：

#### 支持格式
- **TXT格式**: 每行一个IP地址
- **CSV格式**: 第一列为IP地址，支持带标题行

#### 导入方式
1. **点击导入**: 点击"📁 导入文件"按钮选择文件
2. **拖拽上传**: 直接将文件拖拽到拖拽区域

#### 文件限制
- 文件大小: 最大5MB
- IP数量: 最多100个IP地址
- 编码格式: UTF-8

### 数据导出
查询结果支持多种格式导出：

#### 导出格式
1. **CSV格式** (.csv) - 适合Excel打开和数据分析
2. **JSON格式** (.json) - 适合程序处理和API集成
3. **Excel格式** (.xlsx) - 直接用Excel打开，支持中文

#### 导出字段
- IP地址、国家/地区、城市、邮编
- 纬度/经度、时区、ISP信息
- 查询时间、精度半径等

## �📡 API接口

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

## 🎨 功能特性

### 核心功能
- ✅ **单个IP查询** - 快速查询单个IP地址的详细信息
- ✅ **批量IP查询** - 支持最多100个IP地址同时查询
- ✅ **查询历史** - 自动保存查询记录，支持搜索和管理
- ✅ **数据导入** - 支持TXT/CSV文件导入，拖拽上传
- ✅ **数据导出** - 支持CSV/JSON/Excel格式导出

### 界面设计
- ✅ **现代化UI** - 玻璃拟态设计风格，视觉效果出色
- ✅ **主题切换** - 支持深色/浅色主题切换
- ✅ **二级导航** - 层级化下拉菜单导航系统
- ✅ **响应式设计** - 完美适配桌面、平板和移动设备
- ✅ **动画效果** - 丰富的交互动画和状态反馈

### 技术特性
- ✅ **前后端分离** - 清晰的架构，易于维护和扩展
- ✅ **RESTful API** - 标准化的API接口设计
- ✅ **CORS支持** - 支持跨域请求
- ✅ **错误处理** - 完善的错误提示和处理机制
- ✅ **性能优化** - 并发查询，实时进度显示

## 🎨 UI设计特色

### 视觉设计
- **玻璃拟态风格** - 现代化的半透明设计语言
- **渐变背景** - 多层次的颜色渐变效果
- **动画交互** - 丰富的悬停和点击动画
- **主题系统** - 深色/浅色主题无缝切换

### 导航系统
- **二级导航** - 层级化的下拉菜单结构
  ```
  *首页
  *工具箱
  **IP查询
  *使用帮助
  **使用指南
  **常见问题
  *关于我们
  ```
- **响应式交互** - 桌面端悬停，移动端点击
- **视觉指示** - 下拉箭头和状态反馈

### 美化区域
- **导入区域** - 渐变背景、3D按钮、拖拽反馈
- **导出区域** - 分色主题按钮、闪烁动画
- **查询结果** - 卡片式布局、状态图标
- **加载状态** - 旋转动画、进度指示

## 🛠️ 技术栈

### 前端技术
- **HTML5 + CSS3 + JavaScript (ES6+)**
- **CSS特性**: Flexbox、Grid、CSS变量、关键帧动画
- **设计风格**: 玻璃拟态、渐变背景、3D效果
- **响应式**: 移动优先设计，多断点适配
- **文件处理**: FileReader API、Drag & Drop API、Blob API

### 后端技术
- **Python 3.7+** - 主要编程语言
- **Flask 2.0+** - Web框架
- **Flask-CORS** - 跨域支持
- **GeoIP2** - IP地理位置查询
- **MaxMind GeoLite2** - IP地理位置数据库

### 架构特性
- **前后端分离** - 独立部署和扩展
- **RESTful API** - 标准化接口设计
- **模块化设计** - 清晰的代码组织
- **错误处理** - 完善的异常处理机制

## 🔧 开发说明

### 项目结构详解

#### 前端目录 (`IP查询工具/`)
- `assets/` - 静态资源（图标、图片）
- `css/style.css` - 主样式文件，包含所有UI美化效果
- `js/script.js` - 主逻辑文件，包含API调用和交互逻辑
- `*.html` - 页面文件，采用统一的导航结构

#### 后端目录 (`API/`)
- `api/ip_service.py` - IP查询核心服务类
- `utils/validators.py` - IP地址验证工具
- `models/` - 数据模型目录
- `app.py` - Flask应用主文件
- `start.py` - 后端服务启动脚本

### 开发环境配置

#### 端口配置
- **前端端口**: 默认3000，可在启动脚本中修改
- **后端端口**: 默认5000，可在 `API/app.py` 中修改

#### API配置
- **API地址**: 在 `js/script.js` 中的 `API_CONFIG.baseURL`
- **CORS设置**: 在 `API/app.py` 中配置允许的域名

#### 数据库配置
- **GeoLite2数据库**: 需要下载并放置在 `API/` 目录
- **更新频率**: 建议每月更新一次数据库文件

### 代码架构说明

#### 前端架构
- **模块化设计**: 功能分离，易于维护
- **API配置管理**: 集中的配置和环境管理
- **状态管理**: 统一的状态处理和反馈机制
- **错误处理**: 完善的网络错误处理

#### 后端架构
- **服务层**: IPService 负责核心业务逻辑
- **工具层**: 验证器和辅助工具
- **API层**: Flask路由和请求处理
- **数据层**: GeoIP2数据库访问

## 📝 注意事项

1. **数据库文件** - 必须下载并放置GeoLite2-City.mmdb文件
2. **端口占用** - 确保3000和5000端口未被占用
3. **网络访问** - 后端服务需要能够访问前端服务（CORS配置）
4. **Python版本** - 建议使用Python 3.7或更高版本

## 🐛 故障排除

### 常见问题及解决方案

#### 服务启动问题
1. **"数据库文件未找到"**
   - 确保已下载 `GeoLite2-City.mmdb` 文件
   - 检查文件是否放置在 `API/` 目录下
   - 验证文件权限是否正确

2. **"端口已被占用"**
   - 关闭占用端口的其他程序
   - 使用 `netstat -ano | findstr :3000` 查看端口占用
   - 修改启动脚本中的端口配置

3. **"API服务连接失败"**
   - 确保后端服务已启动（检查控制台输出）
   - 检查防火墙设置，允许5000端口访问
   - 确认API地址配置正确

#### 功能使用问题
4. **"导入文件失败"**
   - 检查文件格式是否为TXT或CSV
   - 确保文件编码为UTF-8
   - 验证文件大小不超过5MB

5. **"查询结果显示未知"**
   - 可能是私有IP地址（如192.168.x.x）
   - IP地址未被收录在数据库中
   - 网络连接问题导致查询失败

6. **"下拉菜单不显示"**
   - 刷新页面重新加载JavaScript
   - 检查浏览器控制台是否有错误
   - 确保使用现代浏览器

#### 界面显示问题
7. **"主题切换不生效"**
   - 清除浏览器缓存
   - 检查localStorage是否被禁用
   - 确保CSS文件正确加载

8. **"移动端显示异常"**
   - 检查viewport设置
   - 确保CSS媒体查询正确
   - 验证触摸事件是否正常

### 调试技巧

#### 前端调试
- 打开浏览器开发者工具（F12）
- 查看Console标签页的错误信息
- 检查Network标签页的API请求状态
- 验证Elements标签页的CSS样式

#### 后端调试
- 查看终端/命令行的输出日志
- 访问 `http://localhost:5000/api/health` 检查API状态
- 检查Python依赖是否正确安装
- 验证GeoIP2数据库文件是否可读

### 性能优化建议

1. **定期更新数据库** - 每月更新GeoLite2数据库
2. **清理查询历史** - 定期清理本地存储的历史记录
3. **优化网络** - 使用稳定的网络连接进行查询
4. **浏览器缓存** - 适当清理浏览器缓存

## � 项目发展历程

### 版本演进
- **v1.0** - 基础IP查询功能，单体架构
- **v2.0** - 前后端分离重构，RESTful API
- **v2.1** - 添加批量查询和导入导出功能
- **v2.2** - UI美化升级，现代化设计
- **v2.3** - 二级导航系统，用户体验优化

### 重构成果
- ✅ **架构优化** - 从单体应用到前后端分离
- ✅ **功能完善** - 从单一查询到完整工具集
- ✅ **设计升级** - 从基础界面到现代化UI
- ✅ **体验提升** - 从功能导向到用户体验导向

## 🤝 贡献指南

### 开发流程
1. Fork 项目到个人仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- **前端**: 遵循ES6+标准，使用现代JavaScript特性
- **后端**: 遵循PEP8规范，使用类型注解
- **CSS**: 使用BEM命名规范，模块化组织
- **文档**: 保持README和代码注释的更新

## 🔮 未来规划

### 功能扩展
- [ ] IPv6地址支持
- [ ] 地图可视化显示
- [ ] API密钥管理
- [ ] 用户账户系统
- [ ] 查询统计分析

### 技术升级
- [ ] 前端框架升级（Vue.js/React）
- [ ] 数据库集成（PostgreSQL/MongoDB）
- [ ] 容器化部署（Docker）
- [ ] 云服务集成（AWS/Azure）
- [ ] 性能监控和日志系统

## 📞 联系方式

- **项目地址**: [GitHub Repository]
- **问题反馈**: [Issues页面]
- **功能建议**: [Discussions页面]

## �📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **MaxMind** - 提供GeoLite2地理位置数据库
- **Flask** - 优秀的Python Web框架
- **开源社区** - 提供的各种工具和库支持

---

**IP查询工具** - 让IP地址查询变得简单而优雅 ✨
