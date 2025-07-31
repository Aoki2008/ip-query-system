# 📦 项目自动备份指南

## 🎯 概述

IP查询系统现已集成自动备份功能，可以将项目代码自动提交并推送到GitHub仓库，确保代码安全和版本控制。

## 🚀 快速开始

### 1. 手动备份

#### 使用批处理文件（推荐）
```bash
# 在项目根目录执行
backup.bat
```

#### 使用PowerShell脚本
```powershell
# 基础备份
powershell -ExecutionPolicy Bypass -File "scripts\auto-backup.ps1"

# 自定义提交信息
powershell -ExecutionPolicy Bypass -File "scripts\auto-backup.ps1" -Message "feat: 添加新功能"

# 强制备份（即使没有更改）
powershell -ExecutionPolicy Bypass -File "scripts\auto-backup.ps1" -Force
```

### 2. 智能备份

```powershell
# 使用配置文件的智能备份
powershell -ExecutionPolicy Bypass -File "scripts\smart-backup.ps1"

# 模拟运行（不实际执行）
powershell -ExecutionPolicy Bypass -File "scripts\smart-backup.ps1" -DryRun

# 自定义提交信息
powershell -ExecutionPolicy Bypass -File "scripts\smart-backup.ps1" -Message "fix: 修复重要bug"
```

## ⏰ 定时备份

### 设置定时任务

```powershell
# 设置每天23:00自动备份
powershell -ExecutionPolicy Bypass -File "scripts\schedule-backup.ps1"

# 自定义时间
powershell -ExecutionPolicy Bypass -File "scripts\schedule-backup.ps1" -Time "22:30"

# 移除定时任务
powershell -ExecutionPolicy Bypass -File "scripts\schedule-backup.ps1" -Remove
```

### 管理定时任务

1. 打开"任务计划程序"
2. 找到"IP查询系统自动备份"任务
3. 可以查看、编辑、禁用或删除任务

## 🔧 配置文件

配置文件位置：`scripts/backup-config.json`

### 主要配置项

```json
{
  "backup": {
    "enabled": true,                    // 启用/禁用备份
    "repository": "GitHub仓库地址",      // 远程仓库
    "branch": "main",                   // 默认分支
    "auto_commit": {
      "enabled": true,                  // 自动提交
      "message_prefix": "auto:",        // 提交信息前缀
      "include_timestamp": true         // 包含时间戳
    }
  }
}
```

## 📋 备份脚本功能

### auto-backup.ps1
- ✅ 检查Git状态
- ✅ 添加所有更改
- ✅ 自动生成提交信息
- ✅ 推送到GitHub
- ✅ 错误处理和日志

### smart-backup.ps1
- ✅ 基于配置文件
- ✅ 智能文件过滤
- ✅ 模拟运行模式
- ✅ 详细状态显示
- ✅ 自动更新配置

### schedule-backup.ps1
- ✅ 创建Windows定时任务
- ✅ 自定义执行时间
- ✅ 任务管理功能

## 🛡️ 安全注意事项

### 1. 敏感信息保护
- 确保`.env`文件在`.gitignore`中
- 不要提交数据库密码等敏感信息
- 检查配置文件中的排除模式

### 2. 权限管理
- 确保GitHub访问权限正确
- 定时任务需要适当的用户权限

## 🔍 故障排除

### 常见问题

#### 1. Git推送失败
```
解决方案：
- 检查网络连接
- 验证GitHub访问权限
- 确认远程仓库地址正确
```

#### 2. 定时任务不执行
```
解决方案：
- 以管理员身份运行PowerShell
- 检查任务计划程序中的任务状态
- 验证脚本路径正确
```

#### 3. PowerShell执行策略限制
```
解决方案：
powershell -ExecutionPolicy Bypass -File "脚本路径"
```

## 📊 使用统计

### 查看备份历史
```powershell
# 查看最近的提交
git log --oneline -10

# 查看备份配置
Get-Content scripts\backup-config.json | ConvertFrom-Json
```

### 检查仓库状态
```powershell
# 检查远程仓库
git remote -v

# 检查分支状态
git status
```

## 🎯 最佳实践

### 1. 定期备份
- 建议设置每日自动备份
- 重要更改后手动备份
- 定期检查备份状态

### 2. 提交信息规范
- 使用有意义的提交信息
- 遵循约定式提交格式
- 包含更改类型和描述

### 3. 监控和维护
- 定期检查GitHub仓库
- 监控备份脚本执行状态
- 及时处理备份失败

---

**🔗 相关链接**
- GitHub仓库: https://github.com/Aoki2008/ip-query-system
- 项目文档: docs/
- 技术支持: 查看项目README.md
