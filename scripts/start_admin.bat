@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo 🛡️ IP查询系统 - 管理后台启动脚本
echo ==========================================

REM 检查是否在项目根目录
if not exist "frontend-admin" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo 📁 切换到管理后台目录...
cd frontend-admin

echo 📦 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Node.js，请先安装Node.js 18+
    echo 💡 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js环境检查通过

echo 📦 检查npm环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到npm
    pause
    exit /b 1
)

echo ✅ npm环境检查通过

echo 🔧 安装/更新依赖包...
if not exist "node_modules" (
    echo 📦 首次安装依赖包...
    npm install
) else (
    echo 🔄 检查依赖包更新...
    npm ci
)

if errorlevel 1 (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
)

echo ✅ 依赖包检查完成

echo.
echo 🚀 启动管理后台开发服务器...
echo 📍 管理后台: http://localhost:5174
echo 🔐 默认账户: admin / admin123
echo 🛑 按 Ctrl+C 停止服务
echo.

npm run dev

echo.
echo 🛑 管理后台服务已停止
pause
