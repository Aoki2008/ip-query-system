@echo off
setlocal enabledelayedexpansion

echo.
echo IP Query System - Start All Services
echo =====================================

REM Check if in project root directory
if not exist "backend-fastapi" (
    echo Error: Please run this script from project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Preparing to start the following services:
echo   - FastAPI Backend Service (Port: 8000)
echo   - Vue3 User Frontend (Port: 5173)
echo   - Vue3 Admin Panel (Port: 5174)
echo.

set /p "confirm=Continue to start all services? (y/N): "
if /i not "!confirm!"=="y" (
    echo Startup cancelled
    pause
    exit /b 0
)

echo.
echo Starting services...

REM Start backend service
echo Starting FastAPI backend service...
start "FastAPI Backend" cmd /k "cd backend-fastapi && python main.py"

REM Wait for backend to start
echo Waiting for backend service to start...
timeout /t 3 /nobreak >nul

REM Start user frontend
echo Starting Vue3 user frontend...
start "Vue3 Frontend" cmd /k "cd frontend-vue3 && npm run dev"

REM Wait for frontend to start
echo Waiting for frontend service to start...
timeout /t 3 /nobreak >nul

REM Start admin panel
echo Starting Vue3 admin panel...
start "Vue3 Admin" cmd /k "cd frontend-admin && npm run dev"

echo.
echo All services started successfully!
echo.
echo Service URLs:
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - User Frontend: http://localhost:5173
echo   - Admin Panel: http://localhost:5174
echo.
echo Default Admin Account:
echo   Username: admin
echo   Password: admin123
echo.
echo Tips:
echo   - Each service runs in a separate command window
echo   - Close the corresponding window to stop a service
echo   - Recommended startup order: Backend - Frontend - Admin
echo.

pause
