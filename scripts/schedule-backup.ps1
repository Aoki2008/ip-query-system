# 定时备份脚本 - 设置Windows任务计划程序
# 每天自动备份项目到GitHub

param(
    [string]$Time = "23:00",  # 默认每天23:00执行
    [switch]$Remove = $false   # 移除定时任务
)

$TaskName = "IP查询系统自动备份"
$ScriptPath = Join-Path $PSScriptRoot "auto-backup.ps1"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

if ($Remove) {
    Write-Host "🗑️ 移除定时备份任务..." -ForegroundColor Yellow
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
        Write-Host "✅ 定时备份任务已移除" -ForegroundColor Green
    } catch {
        Write-Host "❌ 移除失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit
}

Write-Host "⏰ 设置定时备份任务..." -ForegroundColor Green
Write-Host "📁 项目路径: $ProjectRoot" -ForegroundColor Cyan
Write-Host "🕐 执行时间: 每天 $Time" -ForegroundColor Cyan

try {
    # 创建任务动作
    $Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -Message `"scheduled: 定时自动备份`""
    
    # 创建任务触发器（每天执行）
    $Trigger = New-ScheduledTaskTrigger -Daily -At $Time
    
    # 创建任务设置
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    # 创建任务主体（以当前用户身份运行）
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    
    # 注册任务
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "自动备份IP查询系统项目到GitHub" -Force
    
    Write-Host "✅ 定时备份任务设置成功!" -ForegroundColor Green
    Write-Host "📋 任务名称: $TaskName" -ForegroundColor Cyan
    Write-Host "🔧 管理任务: 打开任务计划程序查看和管理" -ForegroundColor Yellow
    
    # 显示任务信息
    Get-ScheduledTask -TaskName $TaskName | Format-Table TaskName, State, NextRunTime -AutoSize
    
} catch {
    Write-Host "❌ 设置定时任务失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 提示: 请以管理员身份运行PowerShell" -ForegroundColor Yellow
}
