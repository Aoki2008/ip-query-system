@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🚀 IP查询系统 - 启动所有服务
echo ========================================
echo.

set PROJECT_ROOT=%~dp0..
cd /d "%PROJECT_ROOT%"

echo 📍 当前目录: %CD%
echo.

echo 🔍 检查项目结构...
if not exist "backend-fastapi" (
    echo ❌ 未找到backend-fastapi目录
    pause
    exit /b 1
)

if not exist "frontend-admin" (
    echo ❌ 未找到frontend-admin目录
    pause
    exit /b 1
)

echo ✅ 项目结构检查通过
echo.

echo 🐍 启动后端服务...
echo 📍 后端地址: http://localhost:8000
echo 📖 API文档: http://localhost:8000/docs
echo.

start "IP查询系统-后端服务" cmd /k "cd /d %PROJECT_ROOT%\backend-fastapi && echo 🚀 启动FastAPI服务器... && python main.py"

echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 启动前端管理后台...
echo 📍 管理后台地址: http://localhost:5174
echo.

start "IP查询系统-管理后台" cmd /k "cd /d %PROJECT_ROOT%\frontend-admin && echo 🚀 启动管理后台... && npm run dev"

echo ⏳ 等待前端服务启动...
timeout /t 3 /nobreak >nul

echo.
echo ✅ 所有服务启动完成！
echo.
echo 📋 服务地址:
echo   - 后端API: http://localhost:8000
echo   - API文档: http://localhost:8000/docs
echo   - 管理后台: http://localhost:5174
echo   - 用户前端: http://localhost:5173 (需要单独启动)
echo.
echo 🔑 默认管理员账户:
echo   - 用户名: admin
echo   - 密码: admin123
echo.
echo 💡 提示:
echo   - 如果遇到端口冲突，请检查端口是否被占用
echo   - 如果后端启动失败，请检查Python环境和依赖
echo   - 如果前端启动失败，请检查Node.js环境和依赖
echo.
echo 🛑 按任意键关闭此窗口...
pause >nul
