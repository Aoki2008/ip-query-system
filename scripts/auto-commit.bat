@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 🔄 自动Git提交脚本 (Windows版本)
REM 用法: scripts\auto-commit.bat [提交信息]

echo.
echo 🔄 自动Git提交脚本
echo ==================

REM 检查是否在Git仓库中
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 当前目录不是Git仓库
    pause
    exit /b 1
)

REM 检查是否有未提交的更改
git diff-index --quiet HEAD -- >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  警告: 没有检测到未提交的更改
    pause
    exit /b 0
)

echo.
echo 📋 当前Git状态:
git status --short

echo.
echo 📦 添加所有更改到暂存区...
git add .

REM 生成提交信息
set "commit_message=%~1"
if "%commit_message%"=="" (
    REM 自动生成提交信息
    for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "current_date=%%c-%%a-%%b"
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "current_time=%%a:%%b"
    set "timestamp=!current_date! !current_time!"
    
    REM 检查更改的文件类型
    set "commit_type=📝"
    set "commit_scope=general"
    
    git diff --cached --name-only | findstr "\.md$" >nul 2>&1
    if not errorlevel 1 (
        set "commit_type=📝"
        set "commit_scope=docs"
    )
    
    git diff --cached --name-only | findstr "\.py$" >nul 2>&1
    if not errorlevel 1 (
        set "commit_type=🐍"
        set "commit_scope=backend"
    )
    
    git diff --cached --name-only | findstr "\.vue$ \.ts$ \.js$" >nul 2>&1
    if not errorlevel 1 (
        set "commit_type=🌐"
        set "commit_scope=frontend"
    )
    
    git diff --cached --name-only | findstr "docker \.yml$ \.yaml$" >nul 2>&1
    if not errorlevel 1 (
        set "commit_type=🐳"
        set "commit_scope=deploy"
    )
    
    set "commit_message=!commit_type! 自动提交 - !commit_scope! - !timestamp!"
)

echo.
echo 💬 提交信息: !commit_message!

REM 执行提交
echo.
echo 🚀 执行提交...
git commit -m "!commit_message!"
if errorlevel 1 (
    echo ❌ 提交失败
    pause
    exit /b 1
)

echo ✅ 提交完成!

REM 询问是否推送到远程
echo.
set /p "push_choice=是否推送到远程仓库? (y/N): "
if /i "!push_choice!"=="y" (
    echo.
    echo 📤 推送到远程仓库...
    git push origin main
    if errorlevel 1 (
        echo ❌ 推送失败
        pause
        exit /b 1
    )
    echo ✅ 推送完成!
) else (
    echo.
    echo ℹ️  跳过推送，可以稍后手动执行: git push origin main
)

echo.
echo 🎉 自动提交流程完成!
pause
