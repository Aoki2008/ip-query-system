@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo 🌐 IP查询系统 - 前端服务启动脚本
echo ==========================================

REM 检查是否在项目根目录
if not exist "frontend-vue3" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo 📁 切换到前端目录...
cd frontend-vue3

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
echo 🚀 启动Vue3开发服务器...
echo 📍 用户前端: http://localhost:5173
echo 🛑 按 Ctrl+C 停止服务
echo.

npm run dev

echo.
echo 🛑 前端服务已停止
pause
