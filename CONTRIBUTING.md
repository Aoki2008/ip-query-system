# 贡献指南

感谢您对IP查询系统项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 报告Bug

如果您发现了Bug，请：

1. 检查现有Issues确保该Bug尚未被报告
2. 创建新的Issue并提供详细信息
3. 包含复现步骤和环境信息
4. 如果可能，请提供最小复现示例

### 建议新功能

如果您有新功能的想法：

1. 检查现有Issues确保该功能尚未被建议
2. 创建新的Issue描述功能需求
3. 详细说明功能的用途和价值
4. 如果可能，提供设计草图或原型

### 提交代码

#### 开发环境设置

1. Fork这个仓库
2. 克隆您的Fork到本地：
   ```bash
   git clone https://github.com/your-username/ip-query-system.git
   cd ip-query-system
   ```

3. 安装依赖：
   ```bash
   # API服务
   cd api-system && npm install
   
   # 前端应用
   cd ../ip-tool && npm install
   
   # 管理后台
   cd ../admin-panel && composer install
   ```

4. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入必要的配置
   ```

5. 启动开发环境：
   ```bash
   docker-compose up -d
   ```

#### 代码规范

**JavaScript/TypeScript:**
- 使用ESLint和Prettier进行代码格式化
- 遵循Airbnb JavaScript风格指南
- 使用TypeScript进行类型检查

**PHP:**
- 遵循PSR-12编码标准
- 使用PHP CS Fixer进行代码格式化

**提交信息规范:**
使用Conventional Commits格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### Pull Request流程

1. 创建功能分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 进行开发并提交：
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. 推送到您的Fork：
   ```bash
   git push origin feature/your-feature-name
   ```

4. 创建Pull Request：
   - 提供清晰的描述
   - 链接相关的Issue
   - 确保所有检查通过

#### 测试

在提交PR之前，请确保：

1. 所有现有测试通过
2. 为新功能添加测试
3. 测试覆盖率不降低

## 开发指南

### 项目结构

```
ip-query-system/
├── api-system/          # Node.js API服务
├── admin-panel/         # Laravel管理后台
├── ip-tool/            # Next.js前端应用
├── database/           # 数据库文件
├── docs/               # 文档
└── deploy/             # 部署脚本
```

### 技术栈

- **前端**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **API**: Node.js, Express, TypeScript
- **后端**: Laravel 10, PHP 8.1
- **数据库**: MySQL 8.0, Redis 7.0
- **部署**: Docker, Docker Compose, Nginx

## 社区准则

### 行为准则

我们致力于为每个人提供友好、安全和欢迎的环境。请：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 专注于对社区最有利的事情
- 对其他社区成员表示同理心

### 沟通渠道

- **Issues**: 用于Bug报告和功能请求
- **Discussions**: 用于一般讨论和问题
- **Email**: support@example.com

## 许可证

通过贡献代码，您同意您的贡献将在MIT许可证下获得许可。

## 问题和支持

如果您有任何问题：

1. 查看文档
2. 搜索现有Issues
3. 创建新的Issue
4. 发送邮件到support@example.com

感谢您的贡献！🎉
