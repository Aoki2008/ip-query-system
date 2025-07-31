# 智能备份脚本 - 基于配置文件的高级备份功能

param(
    [string]$ConfigPath = "scripts\backup-config.json",
    [string]$Message = "",
    [switch]$Force = $false,
    [switch]$DryRun = $false
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 获取项目根目录
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ConfigFullPath = Join-Path $ProjectRoot $ConfigPath

Write-Host "🤖 智能备份系统启动..." -ForegroundColor Green

try {
    # 读取配置文件
    if (-not (Test-Path $ConfigFullPath)) {
        Write-Host "❌ 配置文件不存在: $ConfigFullPath" -ForegroundColor Red
        exit 1
    }
    
    $config = Get-Content $ConfigFullPath | ConvertFrom-Json
    
    if (-not $config.backup.enabled) {
        Write-Host "⏸️ 备份功能已禁用" -ForegroundColor Yellow
        exit 0
    }
    
    # 切换到项目根目录
    Set-Location $ProjectRoot
    
    Write-Host "📁 项目: $($config.project.name)" -ForegroundColor Cyan
    Write-Host "📂 路径: $ProjectRoot" -ForegroundColor Cyan
    Write-Host "🔗 仓库: $($config.backup.repository)" -ForegroundColor Cyan
    
    # 检查Git状态
    $gitStatus = git status --porcelain
    $hasChanges = $gitStatus.Count -gt 0
    
    if (-not $hasChanges -and -not $Force) {
        Write-Host "✅ 没有需要备份的更改" -ForegroundColor Green
        exit 0
    }
    
    # 显示更改的文件
    if ($hasChanges) {
        Write-Host "📋 检测到以下更改:" -ForegroundColor Yellow
        git status --short | ForEach-Object {
            $status = $_.Substring(0, 2)
            $file = $_.Substring(3)
            $color = switch ($status.Trim()) {
                "M" { "Yellow" }
                "A" { "Green" }
                "D" { "Red" }
                "??" { "Cyan" }
                default { "White" }
            }
            Write-Host "  $status $file" -ForegroundColor $color
        }
    }
    
    if ($DryRun) {
        Write-Host "🔍 模拟运行模式 - 不会实际执行备份" -ForegroundColor Magenta
        exit 0
    }
    
    # 添加文件（排除配置中的模式）
    Write-Host "➕ 添加更改的文件..." -ForegroundColor Yellow
    git add .
    
    # 生成提交信息
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    if ($Message) {
        $commitMessage = $Message
    } else {
        $prefix = $config.backup.auto_commit.message_prefix
        $commitMessage = "$prefix 自动备份项目代码"
    }
    
    if ($config.backup.auto_commit.include_timestamp) {
        $commitMessage += " - $timestamp"
    }
    
    # 提交更改
    Write-Host "💾 提交更改..." -ForegroundColor Yellow
    Write-Host "📝 提交信息: $commitMessage" -ForegroundColor Cyan
    git commit -m $commitMessage
    
    # 推送到远程仓库
    $remoteName = $config.git.remote_name
    $branch = $config.git.default_branch
    
    Write-Host "🚀 推送到远程仓库..." -ForegroundColor Yellow
    git push $remoteName $branch
    
    # 更新配置文件中的最后备份时间
    $config.project.last_backup = $timestamp
    $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigFullPath
    
    if ($config.backup.notifications.success) {
        Write-Host "✅ 智能备份完成!" -ForegroundColor Green
        Write-Host "🕐 备份时间: $timestamp" -ForegroundColor Cyan
        Write-Host "🔗 GitHub: $($config.backup.repository)" -ForegroundColor Cyan
    }
    
} catch {
    if ($config.backup.notifications.failure) {
        Write-Host "❌ 智能备份失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit 1
}
