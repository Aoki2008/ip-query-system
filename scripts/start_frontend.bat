@echo off
echo ========================================
echo IP查询工具 - 前端服务启动脚本
echo ========================================

cd /d "%~dp0IP查询工具"

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 启动前端服务...
echo 服务地址: http://localhost:3000
echo 浏览器将自动打开，按 Ctrl+C 停止服务
echo ========================================
python start.py

pause
