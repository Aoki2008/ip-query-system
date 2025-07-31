@echo off
setlocal enabledelayedexpansion

echo.
echo IP Query System - FastAPI Backend Startup Script
echo ================================================

REM Check if in project root directory
if not exist "backend-fastapi" (
    echo Error: Please run this script from project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo 📁 切换到后端目录...
cd backend-fastapi

echo 🐍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.11+
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

echo 📦 检查依赖包...
if not exist "requirements.txt" (
    echo ❌ 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)

echo 🔧 安装/更新依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
)

echo ✅ 依赖包检查完成

echo 📊 检查数据文件...
if not exist "data\GeoLite2-City.mmdb" (
    echo ⚠️  警告: 未找到GeoLite2-City.mmdb数据文件
    echo 💡 请从MaxMind官网下载并放置在data目录下
    echo 🔗 https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
)

echo.
echo 🚀 启动FastAPI服务器...
echo 📍 服务地址: http://localhost:8000
echo 📖 API文档: http://localhost:8000/docs
echo.

python main.py

echo.
echo 🛑 服务已停止
pause
