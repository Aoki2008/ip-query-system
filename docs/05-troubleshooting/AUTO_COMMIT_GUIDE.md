# 🔄 自动提交Git设置指南

## 📋 概述

本指南介绍如何设置和使用项目的自动Git提交功能，包括多种自动提交方式和配置选项。

## 🛠️ 可用的自动提交方式

### 1. 📜 脚本方式

#### Linux/macOS (Bash)
```bash
# 基本使用
./scripts/auto-commit.sh

# 自定义提交信息
./scripts/auto-commit.sh "修复登录bug"

# 自动推送
./scripts/auto-commit.sh -p "更新文档"

# 显示帮助
./scripts/auto-commit.sh -h
```

#### Windows (批处理)
```cmd
# 基本使用
scripts\auto-commit.bat

# 自定义提交信息
scripts\auto-commit.bat "修复登录bug"
```

#### Windows (PowerShell)
```powershell
# 基本使用
.\scripts\auto-commit.ps1

# 自定义提交信息
.\scripts\auto-commit.ps1 -Message "修复登录bug"

# 自动推送
.\scripts\auto-commit.ps1 -Message "更新文档" -Push

# 显示帮助
.\scripts\auto-commit.ps1 -Help
```

### 2. 🪝 Git钩子方式

#### 设置Git钩子
```bash
# 运行设置脚本
./scripts/setup-auto-commit.sh
```

#### 钩子功能
- **pre-commit**: 代码质量检查
- **post-commit**: 询问是否自动推送
- **commit-msg**: 提交信息格式检查

### 3. ⚙️ 环境变量配置

#### 启用自动推送
```bash
# Linux/macOS
export AUTO_PUSH=true

# Windows (PowerShell)
$env:AUTO_PUSH = "true"

# Windows (CMD)
set AUTO_PUSH=true
```

## 📝 自动生成提交信息规则

### 文件类型映射

| 文件类型 | 表情符号 | 范围 | 示例提交信息 |
|---------|---------|------|-------------|
| `*.md` | 📝 | docs | `📝 自动提交 - docs (3个文件) - 2025-07-31 15:30` |
| `*.py` | 🐍 | backend | `🐍 自动提交 - backend (2个文件) - 2025-07-31 15:30` |
| `*.vue,*.ts,*.js` | 🌐 | frontend | `🌐 自动提交 - frontend (5个文件) - 2025-07-31 15:30` |
| `docker*,*.yml` | 🐳 | deploy | `🐳 自动提交 - deploy (1个文件) - 2025-07-31 15:30` |
| `*.json,package*` | 📦 | deps | `📦 自动提交 - deps (1个文件) - 2025-07-31 15:30` |

### 提交信息格式
```
{emoji} 自动提交 - {scope} ({fileCount}个文件) - {timestamp}
```

## 🔧 配置选项

### 配置文件位置
- `scripts/auto-commit-config.json`

### 主要配置项

#### 提交规则
```json
{
  "commitRules": {
    "minLength": 10,
    "maxLength": 100,
    "requireType": false
  }
}
```

#### 自动推送
```json
{
  "autoPush": {
    "enabled": false,
    "branches": ["main", "master"],
    "askConfirmation": true
  }
}
```

#### Git钩子
```json
{
  "hooks": {
    "preCommit": {
      "enabled": true,
      "runLinting": true,
      "checkSensitiveData": true
    }
  }
}
```

## 🚀 使用示例

### 场景1: 快速提交文档更新
```bash
# 修改了一些文档文件
./scripts/auto-commit.sh
# 输出: 📝 自动提交 - docs (3个文件) - 2025-07-31 15:30
```

### 场景2: 提交代码修改并推送
```bash
# 修改了后端代码
./scripts/auto-commit.sh -p "修复API响应问题"
# 自动提交并推送到远程仓库
```

### 场景3: 使用PowerShell自动提交
```powershell
# 修改了前端代码
.\scripts\auto-commit.ps1 -Message "优化用户界面" -Push
```

## ⚠️ 注意事项

### 安全考虑
1. **敏感信息检查**: 脚本会检查提交信息中的敏感词汇
2. **文件内容扫描**: 避免提交包含密码、密钥的文件
3. **分支保护**: 只在指定分支上启用自动推送

### 最佳实践
1. **定期检查**: 定期查看自动生成的提交信息
2. **手动审查**: 重要更改建议手动编写提交信息
3. **测试环境**: 先在测试分支验证自动提交功能

### 故障排除

#### 常见问题

**问题1**: 脚本无法执行
```bash
# 解决方案: 添加执行权限
chmod +x scripts/auto-commit.sh
```

**问题2**: PowerShell执行策略限制
```powershell
# 解决方案: 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**问题3**: Git钩子不生效
```bash
# 解决方案: 重新运行设置脚本
./scripts/setup-auto-commit.sh
```

## 📊 功能对比

| 功能 | Bash脚本 | 批处理 | PowerShell | Git钩子 |
|------|---------|--------|-----------|---------|
| 自动生成提交信息 | ✅ | ✅ | ✅ | ❌ |
| 自定义提交信息 | ✅ | ✅ | ✅ | ❌ |
| 自动推送 | ✅ | ✅ | ✅ | ✅ |
| 代码质量检查 | ❌ | ❌ | ❌ | ✅ |
| 提交信息验证 | ❌ | ❌ | ❌ | ✅ |
| 跨平台支持 | Linux/macOS | Windows | Windows | 全平台 |

## 🔗 相关文档

- [Git钩子官方文档](https://git-scm.com/book/zh/v2/自定义-Git-Git-钩子)
- [项目开发规范](../.augment/rules/rule.md)
- [代码质量规范](../.augment/rules/rule1.md)

---

**💡 提示**: 建议根据团队需求选择合适的自动提交方式，并定期审查自动生成的提交历史。
