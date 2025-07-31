# 🚀 自动推送功能使用指南

## 📋 概述

自动推送功能允许您在提交代码后自动推送到远程仓库，无需手动确认。

## 🛠️ 使用方法

### 1. Bash脚本 (Linux/macOS/Git Bash)

#### 基本语法
```bash
./scripts/auto-commit.sh [选项] [提交信息]
```

#### 自动推送示例
```bash
# 自动生成提交信息并推送
./scripts/auto-commit.sh -p

# 自定义提交信息并推送
./scripts/auto-commit.sh -p "修复登录bug"

# 显示帮助信息
./scripts/auto-commit.sh -h
```

### 2. PowerShell脚本 (Windows)

#### 基本语法
```powershell
.\scripts\auto-commit.ps1 [参数]
```

#### 自动推送示例
```powershell
# 自动生成提交信息并推送
.\scripts\auto-commit.ps1 -Push

# 自定义提交信息并推送
.\scripts\auto-commit.ps1 -Message "修复登录bug" -Push

# 显示帮助信息
.\scripts\auto-commit.ps1 -Help
```

### 3. 环境变量方式

#### 设置自动推送环境变量
```bash
# Linux/macOS
export AUTO_PUSH=true

# Windows PowerShell
$env:AUTO_PUSH = "true"

# Windows CMD
set AUTO_PUSH=true
```

#### 使用环境变量
```bash
# 设置后，所有提交都会自动推送
./scripts/auto-commit.sh "提交信息"
```

## 🔧 故障排除

### 问题1: 自动推送不工作

#### 可能原因
1. **参数传递错误**: 脚本内部参数没有正确传递
2. **权限问题**: 没有推送权限到远程仓库
3. **网络问题**: 无法连接到远程仓库
4. **分支问题**: 当前分支与远程分支不匹配

#### 解决方案
```bash
# 1. 检查Git配置
git config --list | grep remote
git remote -v

# 2. 检查当前分支
git branch -a
git status

# 3. 手动测试推送
git push origin main

# 4. 检查权限
git push --dry-run origin main
```

### 问题2: 脚本执行失败

#### Windows用户
```cmd
# 如果PowerShell执行策略限制
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 使用完整路径
powershell -ExecutionPolicy Bypass -File ".\scripts\auto-commit.ps1" -Push
```

#### Linux/macOS用户
```bash
# 添加执行权限
chmod +x scripts/auto-commit.sh

# 使用bash直接执行
bash scripts/auto-commit.sh -p
```

### 问题3: 推送被拒绝

#### 常见原因和解决方案
```bash
# 1. 远程有新提交，需要先拉取
git pull origin main
git push origin main

# 2. 分支保护规则
# 检查GitHub/GitLab的分支保护设置

# 3. 认证问题
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 4. SSH密钥问题
ssh -T git@github.com
```

## 📊 功能验证

### 测试自动推送功能

#### 创建测试文件
```bash
echo "Test auto-push $(date)" > test-auto-push.txt
```

#### 使用自动推送
```bash
# Bash版本
./scripts/auto-commit.sh -p "测试自动推送功能"

# PowerShell版本
.\scripts\auto-commit.ps1 -Message "测试自动推送功能" -Push
```

#### 验证结果
```bash
# 检查远程仓库是否有新提交
git log --oneline -5
git ls-remote origin main
```

#### 清理测试文件
```bash
rm test-auto-push.txt
git add test-auto-push.txt
git commit -m "清理测试文件"
git push origin main
```

## ⚙️ 高级配置

### 1. 配置默认推送行为

#### Git配置
```bash
# 设置默认推送策略
git config --global push.default simple

# 设置自动推送标签
git config --global push.followTags true

# 设置推送时自动设置上游分支
git config --global push.autoSetupRemote true
```

### 2. 自定义推送脚本

#### 创建别名
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias gcp="./scripts/auto-commit.sh -p"
alias gcm="./scripts/auto-commit.sh"

# 使用别名
gcp "快速提交并推送"
```

#### PowerShell别名
```powershell
# 添加到 PowerShell Profile
function gcp { .\scripts\auto-commit.ps1 -Message $args[0] -Push }
function gcm { .\scripts\auto-commit.ps1 -Message $args[0] }

# 使用别名
gcp "快速提交并推送"
```

### 3. CI/CD集成

#### GitHub Actions示例
```yaml
name: Auto Commit and Push
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时运行一次
  
jobs:
  auto-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Auto commit
        run: |
          if [[ -n $(git status --porcelain) ]]; then
            ./scripts/auto-commit.sh -p "自动提交 - $(date)"
          fi
```

## 📋 最佳实践

### 1. 使用建议
- **开发环境**: 使用自动推送提高效率
- **生产环境**: 谨慎使用，建议手动确认
- **团队协作**: 统一使用规范的提交信息格式

### 2. 安全考虑
- **敏感信息**: 确保不提交密码、密钥等敏感信息
- **代码审查**: 重要更改建议通过Pull Request流程
- **备份策略**: 定期备份重要分支

### 3. 性能优化
- **批量提交**: 避免频繁的小提交
- **网络优化**: 在网络良好时进行推送
- **冲突处理**: 及时解决合并冲突

## 🔗 相关文档

- [自动提交脚本指南](AUTO_COMMIT_GUIDE.md)
- [Git工作流程](../02-technical-specs/GIT_WORKFLOW.md)
- [项目开发规范](../../.augment/rules/rule.md)

---

**💡 提示**: 如果自动推送仍然不工作，请检查网络连接、Git配置和远程仓库权限。
