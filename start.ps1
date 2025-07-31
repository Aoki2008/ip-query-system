# IP Query System - PowerShell Quick Start Script

Write-Host ""
Write-Host "IP Query System - Quick Start" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "backend-fastapi")) {
    Write-Host "Error: Please run from project root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting all services..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "[1/3] Starting FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend-fastapi; python main.py"
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "[2/3] Starting Vue3 Frontend (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend-vue3; npm run dev"
Start-Sleep -Seconds 2

# Start Admin
Write-Host "[3/3] Starting Admin Panel (Port 5174)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend-admin; npm run dev"

Write-Host ""
Write-Host "All services are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "- API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "- User Interface: http://localhost:5173" -ForegroundColor White
Write-Host "- Admin Panel: http://localhost:5174" -ForegroundColor White
Write-Host ""
Write-Host "Default Admin Login:" -ForegroundColor Cyan
Write-Host "- Username: admin" -ForegroundColor White
Write-Host "- Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Note: Each service opens in a separate PowerShell window" -ForegroundColor Yellow
Write-Host "Close the window to stop that service" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit this window"
