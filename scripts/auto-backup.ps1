# IP查询系统自动备份脚本
# 自动提交并推送代码到GitHub

param(
    [string]$Message = "auto: 自动备份项目代码",
    [switch]$Force = $false
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 获取脚本所在目录的父目录（项目根目录）
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "🔄 开始自动备份项目..." -ForegroundColor Green
Write-Host "📁 项目路径: $ProjectRoot" -ForegroundColor Cyan

try {
    # 切换到项目根目录
    Set-Location $ProjectRoot
    
    # 检查是否是Git仓库
    if (-not (Test-Path ".git")) {
        Write-Host "❌ 错误: 当前目录不是Git仓库" -ForegroundColor Red
        exit 1
    }
    
    # 检查Git状态
    Write-Host "📊 检查Git状态..." -ForegroundColor Yellow
    $gitStatus = git status --porcelain
    
    if (-not $gitStatus -and -not $Force) {
        Write-Host "✅ 没有需要提交的更改" -ForegroundColor Green
        exit 0
    }
    
    # 显示当前状态
    Write-Host "📋 当前Git状态:" -ForegroundColor Yellow
    git status --short
    
    # 添加所有更改
    Write-Host "➕ 添加所有更改..." -ForegroundColor Yellow
    git add .
    
    # 生成提交信息
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "$Message - $timestamp"
    
    # 提交更改
    Write-Host "💾 提交更改..." -ForegroundColor Yellow
    Write-Host "📝 提交信息: $commitMessage" -ForegroundColor Cyan
    git commit -m $commitMessage
    
    # 推送到远程仓库
    Write-Host "🚀 推送到GitHub..." -ForegroundColor Yellow
    git push origin main
    
    Write-Host "✅ 自动备份完成!" -ForegroundColor Green
    Write-Host "🔗 GitHub仓库: https://github.com/Aoki2008/ip-query-system" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ 备份失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
