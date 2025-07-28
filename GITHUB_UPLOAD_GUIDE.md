# 🚀 GitHub上传指南

本指南将帮助您将IP查询系统代码上传到GitHub仓库。

## 📋 准备工作

### 1. 确保已安装Git

```bash
# 检查Git是否已安装
git --version

# 如果未安装，请根据您的操作系统安装Git：
# Ubuntu/Debian: sudo apt-get install git
# CentOS/RHEL: sudo yum install git  
# macOS: brew install git
# Windows: https://git-scm.com/download/win
```

### 2. 配置Git用户信息（如果未配置）

```bash
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱@example.com"
```

### 3. 在GitHub上创建仓库

1. 访问 [GitHub](https://github.com) 并登录
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `ip-query-system`
   - **Description**: `企业级IP查询系统`
   - **Visibility**: 选择 Public 或 Private
   - **不要勾选** "Initialize this repository with a README"
   - **不要添加** .gitignore 和 license（我们已经有了）
4. 点击 "Create repository"

## 🎯 一键上传

### 使用自动化脚本（推荐）

```bash
# 1. 给脚本添加执行权限
chmod +x upload-to-github.sh

# 2. 运行上传脚本
./upload-to-github.sh
```

脚本会引导您完成以下步骤：
- ✅ 检查Git环境
- ✅ 获取GitHub仓库信息
- ✅ 初始化Git仓库
- ✅ 配置远程仓库
- ✅ 提交代码
- ✅ 推送到GitHub

### 手动上传步骤

如果您更喜欢手动操作：

```bash
# 1. 初始化Git仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交代码
git commit -m "feat: initial commit - complete IP query system"

# 4. 设置默认分支
git branch -M main

# 5. 添加远程仓库
git remote add origin https://github.com/your-username/ip-query-system.git

# 6. 推送代码
git push -u origin main
```

## 📁 项目文件说明

上传到GitHub的主要文件包括：

### 核心代码
- `api-system/` - Node.js API服务
- `admin-panel/` - Laravel管理后台
- `ip-tool/` - Next.js前端应用
- `database/` - 数据库文件
- `nginx/` - Nginx配置
- `deploy/` - 部署脚本

### GitHub配置
- `.gitignore` - Git忽略规则
- `LICENSE` - MIT许可证
- `CONTRIBUTING.md` - 贡献指南
- `.github/workflows/ci.yml` - GitHub Actions配置
- `README.md` - 项目说明

### 部署相关
- `docker-compose.yml` - Docker编排文件
- `upload-to-github.sh` - GitHub上传脚本
- `docs/` - 完整文档

## 🔧 常见问题

### 1. 推送失败：仓库不存在

**错误信息**：
```
remote: Repository not found.
fatal: repository 'https://github.com/username/repo.git/' not found
```

**解决方法**：
- 确保在GitHub上已创建仓库
- 检查仓库名称和用户名是否正确
- 确保仓库是公开的或您有访问权限

### 2. 推送失败：权限不足

**错误信息**：
```
remote: Permission to username/repo.git denied
```

**解决方法**：
- 检查GitHub用户名和密码
- 使用Personal Access Token代替密码
- 配置SSH密钥认证

### 3. 文件过大

**错误信息**：
```
remote: error: File xxx is xxx MB; this exceeds GitHub's file size limit
```

**解决方法**：
- 检查并删除大文件（如数据库文件、日志文件）
- 使用Git LFS处理大文件
- 确保`.gitignore`正确配置

## 🔐 安全建议

### 1. 保护敏感信息

确保以下文件不会被上传：
- `.env` - 环境变量文件
- `*.log` - 日志文件
- `*.mmdb` - MaxMind数据库文件
- `backups/` - 备份文件
- `ssl/` - SSL证书文件

### 2. 使用环境变量

在代码中使用环境变量而不是硬编码敏感信息：
```javascript
// ✅ 正确
const dbPassword = process.env.DB_PASSWORD;

// ❌ 错误
const dbPassword = "my_secret_password";
```

### 3. 定期更新依赖

```bash
# 检查安全漏洞
npm audit
composer audit

# 更新依赖
npm update
composer update
```

## 📊 GitHub功能

### 1. GitHub Actions

项目包含基础的CI/CD配置：
- 代码质量检查
- 项目结构验证
- 依赖检查
- 文档检查

### 2. Issue模板

GitHub会自动提供：
- Bug报告模板
- 功能请求模板
- Pull Request模板

### 3. 项目管理

您可以使用GitHub的项目管理功能：
- Issues - 问题跟踪
- Projects - 项目看板
- Wiki - 项目文档
- Discussions - 社区讨论

## 🎉 上传完成后

### 1. 验证上传

访问您的GitHub仓库页面，确认：
- ✅ 所有文件已正确上传
- ✅ README.md正确显示
- ✅ 项目结构完整

### 2. 配置仓库

- 编辑仓库描述
- 添加主题标签
- 设置仓库可见性
- 配置分支保护规则

### 3. 邀请协作者

如果是团队项目：
- Settings → Manage access → Invite a collaborator
- 设置适当的权限级别

### 4. 启用功能

根据需要启用：
- GitHub Pages（用于文档）
- Discussions（用于社区讨论）
- Security alerts（安全警报）

## 📞 获取帮助

如果在上传过程中遇到问题：

1. **查看GitHub文档**：https://docs.github.com/
2. **检查脚本输出**：仔细阅读错误信息
3. **联系支持**：support@example.com
4. **创建Issue**：在项目仓库中创建Issue

---

🚀 **恭喜！您的IP查询系统现在已经托管在GitHub上了！**

下一步：
- 📖 查看 [部署指南](docs/deployment.md) 了解如何部署
- 🔧 配置环境变量和域名
- 🚀 开始使用您的IP查询系统
