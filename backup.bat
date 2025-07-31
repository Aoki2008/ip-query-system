@echo off
chcp 65001 >nul
echo 🔄 启动IP查询系统自动备份...
powershell -ExecutionPolicy Bypass -File "scripts\auto-backup.ps1" %*
pause
