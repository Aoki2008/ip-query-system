@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

:: 检查是否存在虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 错误：虚拟环境创建失败
        pause
        exit /b 1
    )
)

:: 检查激活脚本是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 错误：虚拟环境损坏，请删除venv文件夹后重试
    pause
    exit /b 1
)

:: 激活虚拟环境
call "venv\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo 错误：虚拟环境激活失败
    pause
    exit /b 1
)

:: 检查requirements.txt是否存在
if not exist "requirements.txt" (
    echo 错误：未找到requirements.txt文件
    pause
    exit /b 1
)

:: 安装依赖
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误：依赖安装失败
    pause
    exit /b 1
)

:: 检查app.py是否存在
if not exist "app.py" (
    echo 错误：未找到app.py文件
    pause
    exit /b 1
)

:: 停止已有Flask进程
taskkill /f /im python.exe /fi "WINDOWTITLE eq *Flask*" >nul 2>nul

:: 启动应用
echo 启动应用程序...
python app.py
if %errorlevel% neq 0 (
    echo 错误：应用启动失败
    pause
    exit /b 1
)

:: 暂停以查看输出
pause