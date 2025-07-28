@echo off
echo ========================================
echo IP查询工具 - 后端服务启动脚本
echo ========================================

cd /d "%~dp0API"

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 检查依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

echo 检查数据库文件...
if not exist "GeoLite2-City.mmdb" (
    echo 错误: 未找到GeoLite2-City.mmdb数据库文件
    echo 请从MaxMind官网下载该文件并放置在API目录下
    pause
    exit /b 1
)

echo 启动后端服务...
echo 服务地址: http://localhost:5000/api
echo 按 Ctrl+C 停止服务
echo ========================================
python start.py

pause
