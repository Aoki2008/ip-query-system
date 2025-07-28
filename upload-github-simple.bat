@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo IP Query System - GitHub Upload
echo ==========================================
echo.

:: Check Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git not found. Please install Git first.
    echo Download: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git found:
git --version
echo.

:: Get user input
set /p GITHUB_USERNAME="Enter your GitHub username: "
if "!GITHUB_USERNAME!"=="" (
    echo ERROR: Username cannot be empty
    pause
    exit /b 1
)

set /p REPO_NAME="Enter repository name [ip-query-system]: "
if "!REPO_NAME!"=="" set REPO_NAME=ip-query-system

echo.
echo Repository: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
echo.
set /p CONFIRM="Is this correct? (y/N): "
if /i not "!CONFIRM!"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo ==========================================
echo GitHub Repository Setup Guide
echo ==========================================
echo.
echo Please create the repository on GitHub first:
echo 1. Go to https://github.com/new
echo 2. Repository name: !REPO_NAME!
echo 3. Description: Enterprise IP Query System
echo 4. Choose Public or Private
echo 5. DO NOT check any initialization options
echo 6. Click 'Create repository'
echo.
pause

:: Initialize Git
echo Initializing Git repository...
if exist ".git" (
    echo Git repository already exists.
    set /p REINIT="Reinitialize? (y/N): "
    if /i "!REINIT!"=="y" (
        rmdir /s /q .git
        git init
        echo Git repository reinitialized.
    )
) else (
    git init
    echo Git repository initialized.
)

git branch -M main

:: Configure Git user if needed
for /f "tokens=*" %%i in ('git config user.name 2^>nul') do set GIT_USER_NAME=%%i
if "!GIT_USER_NAME!"=="" (
    set /p GIT_USERNAME="Enter your Git username: "
    git config user.name "!GIT_USERNAME!"
)

for /f "tokens=*" %%i in ('git config user.email 2^>nul') do set GIT_USER_EMAIL=%%i
if "!GIT_USER_EMAIL!"=="" (
    set /p GIT_EMAIL="Enter your Git email: "
    git config user.email "!GIT_EMAIL!"
)

echo Git configuration complete.

:: Add remote
echo Configuring remote repository...
git remote | findstr "origin" >nul 2>&1
if %errorlevel% equ 0 (
    echo Remote origin already exists.
    git remote set-url origin "https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git"
    echo Remote URL updated.
) else (
    git remote add origin "https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git"
    echo Remote origin added.
)

:: Commit code
echo Adding files...
git add .

echo Committing code...
git commit -m "feat: initial commit - complete IP query system"

:: Push to GitHub
echo.
echo Ready to push to GitHub.
echo Make sure you have created the repository: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
echo.
set /p CONFIRM_PUSH="Continue with push? (y/N): "
if /i not "!CONFIRM_PUSH!"=="y" (
    echo Push cancelled. You can push later with: git push -u origin main
    pause
    exit /b 0
)

echo Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo SUCCESS! Code uploaded to GitHub
    echo ==========================================
    echo.
    echo Repository: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
    echo Clone URL: git clone https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git
    echo.
    echo Next steps:
    echo 1. Visit your GitHub repository
    echo 2. Edit repository description
    echo 3. Configure repository settings
    echo 4. Start deployment using docs/deployment.md
    echo.
) else (
    echo.
    echo ERROR: Push failed
    echo.
    echo Possible causes:
    echo 1. Repository does not exist on GitHub
    echo 2. Insufficient permissions
    echo 3. Network issues
    echo.
    echo You can try again later with: git push -u origin main
)

pause
