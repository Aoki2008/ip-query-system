@echo off
setlocal enabledelayedexpansion

:: IP Query System - GitHub Upload Script (Windows)
:: Upload project code to GitHub repository

echo.
echo ==========================================
echo IP Query System - GitHub Upload Script
echo ==========================================
echo.
echo This script will help you:
echo 1. Initialize Git repository
echo 2. Configure GitHub remote repository
echo 3. Commit and push code
echo.

:: 检查Git是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git未安装，请先安装Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [信息] Git已安装: 
git --version

:: 获取用户输入
echo.
echo [步骤] 获取GitHub仓库信息...
set /p GITHUB_USERNAME="请输入您的GitHub用户名: "
if "!GITHUB_USERNAME!"=="" (
    echo [错误] GitHub用户名不能为空
    pause
    exit /b 1
)

set /p REPO_NAME="请输入仓库名称 [ip-query-system]: "
if "!REPO_NAME!"=="" set REPO_NAME=ip-query-system

echo.
echo 确认信息：
echo   GitHub用户名: !GITHUB_USERNAME!
echo   仓库名称: !REPO_NAME!
echo   仓库地址: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
echo.

set /p CONFIRM="信息是否正确？(y/N): "
if /i not "!CONFIRM!"=="y" (
    echo [信息] 已取消操作
    pause
    exit /b 0
)

:: 显示GitHub仓库创建指南
echo.
echo ==========================================
echo GitHub仓库创建指南
echo ==========================================
echo.
echo 如果您还没有创建GitHub仓库，请按以下步骤操作：
echo.
echo 1. 访问 https://github.com/new
echo 2. 填写仓库信息：
echo    - Repository name: !REPO_NAME!
echo    - Description: 企业级IP查询系统
echo    - 选择 Public 或 Private
echo    - 不要勾选 'Initialize this repository with a README'
echo    - 不要添加 .gitignore 和 license（我们已经有了）
echo 3. 点击 'Create repository'
echo 4. 创建完成后返回此脚本继续操作
echo.
echo ==========================================
echo.
pause

:: 初始化Git仓库
echo [步骤] 初始化Git仓库...

if exist ".git" (
    echo [警告] 当前目录已经是Git仓库
    set /p REINIT="是否重新初始化？(y/N): "
    if /i "!REINIT!"=="y" (
        rmdir /s /q .git
        git init
        echo [信息] Git仓库重新初始化完成
    ) else (
        echo [信息] 使用现有Git仓库
    )
) else (
    git init
    echo [信息] Git仓库初始化完成
)

:: 设置默认分支为main
git branch -M main

:: 配置Git用户信息（如果未配置）
for /f "tokens=*" %%i in ('git config user.name 2^>nul') do set GIT_USER_NAME=%%i
if "!GIT_USER_NAME!"=="" (
    set /p GIT_USERNAME="请输入您的Git用户名: "
    git config user.name "!GIT_USERNAME!"
)

for /f "tokens=*" %%i in ('git config user.email 2^>nul') do set GIT_USER_EMAIL=%%i
if "!GIT_USER_EMAIL!"=="" (
    set /p GIT_EMAIL="请输入您的Git邮箱: "
    git config user.email "!GIT_EMAIL!"
)

echo [信息] Git配置完成

:: 配置远程仓库
echo [步骤] 配置远程仓库...

git remote | findstr "origin" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] 已存在origin远程仓库
    for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set CURRENT_ORIGIN=%%i
    echo 当前origin: !CURRENT_ORIGIN!
    
    set /p UPDATE_ORIGIN="是否更新origin地址？(y/N): "
    if /i "!UPDATE_ORIGIN!"=="y" (
        git remote set-url origin "https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git"
        echo [信息] 远程仓库地址已更新
    )
) else (
    git remote add origin "https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git"
    echo [信息] 远程仓库已添加
)

echo 远程仓库地址: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git

:: 提交代码
echo [步骤] 提交代码...

:: 检查是否有文件需要提交
git status --porcelain >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 没有文件需要提交
    goto :push_code
)

:: 添加所有文件
echo [信息] 添加文件到暂存区...
git add .

:: 显示将要提交的文件
echo.
echo 将要提交的文件：
git status --short
echo.

set /p CONFIRM_COMMIT="确认提交这些文件？(y/N): "
if /i not "!CONFIRM_COMMIT!"=="y" (
    echo [信息] 已取消提交
    pause
    exit /b 0
)

:: 提交代码
git commit -m "feat: initial commit - complete IP query system

- Add Node.js API service with Express framework
- Add Laravel admin panel with dashboard  
- Add Next.js frontend application
- Add complete database schema and migrations
- Add Docker containerization support
- Add comprehensive documentation
- Add deployment scripts and configurations"

echo [信息] 代码提交完成

:push_code
:: 推送到GitHub
echo [步骤] 推送代码到GitHub...

echo [警告] 请确保您已在GitHub上创建了仓库: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
echo [警告] 如果仓库不存在，请先在GitHub上创建仓库
echo.

set /p CONFIRM_PUSH="仓库已创建，继续推送？(y/N): "
if /i not "!CONFIRM_PUSH!"=="y" (
    echo [信息] 已取消推送
    echo.
    echo 您可以稍后手动推送：
    echo   git push -u origin main
    pause
    exit /b 0
)

:: 推送代码
echo [信息] 正在推送代码...
git push -u origin main
if %errorlevel% equ 0 (
    echo [信息] 代码推送成功！
) else (
    echo [错误] 代码推送失败
    echo.
    echo 可能的原因：
    echo 1. 仓库不存在 - 请在GitHub上创建仓库
    echo 2. 权限不足 - 请检查GitHub访问权限
    echo 3. 网络问题 - 请检查网络连接
    echo.
    echo 您可以稍后手动推送：
    echo   git push -u origin main
    pause
    exit /b 1
)

:: 显示完成信息
echo.
echo ==========================================
echo 代码已成功上传到GitHub
echo ==========================================
echo.
echo 仓库信息：
echo   GitHub地址: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
echo   克隆地址: git clone https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git
echo.
echo 下一步操作：
echo   1. 访问GitHub仓库页面查看代码
echo   2. 编辑仓库描述和README
echo   3. 设置仓库可见性（公开/私有）
echo   4. 配置GitHub Pages（如果需要）
echo   5. 邀请协作者（如果需要）
echo.
echo 部署说明：
echo   - 查看 docs\deployment.md 了解部署步骤
echo   - 使用 deploy\install.sh 进行一键部署
echo   - 配置环境变量和域名
echo.
echo ==========================================

pause
