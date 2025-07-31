@echo off
echo.
echo IP Query System - Quick Start
echo =============================

if not exist "backend-fastapi" (
    echo Error: Please run from project root directory
    pause
    exit /b 1
)

echo Starting all services...
echo.

echo [1/3] Starting FastAPI Backend (Port 8000)...
start "Backend" cmd /k "cd backend-fastapi && python main.py"
timeout /t 2 /nobreak >nul

echo [2/3] Starting Vue3 Frontend (Port 5173)...
start "Frontend" cmd /k "cd frontend-vue3 && npm run dev"
timeout /t 2 /nobreak >nul

echo [3/3] Starting Admin Panel (Port 5174)...
start "Admin" cmd /k "cd frontend-admin && npm run dev"

echo.
echo All services are starting...
echo.
echo Service URLs:
echo - Backend API: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo - User Interface: http://localhost:5173
echo - Admin Panel: http://localhost:5174
echo.
echo Default Admin Login:
echo - Username: admin
echo - Password: admin123
echo.
echo Note: Each service opens in a separate window
echo Close the window to stop that service
echo.

pause
