@echo off
setlocal enabledelayedexpansion

REM IP查询工具 - Windows容器化部署脚本

set "command=%1"
set "env=%2"

if "%command%"=="" set "command=help"
if "%env%"=="" set "env=prod"

echo [INFO] IP查询工具 - 容器化部署

REM 检查Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose未安装，请先安装Docker Compose
    exit /b 1
)

REM 创建必要目录
if not exist "nginx\conf.d" mkdir "nginx\conf.d"
if not exist "API\logs" mkdir "API\logs"
if not exist "backend-fastapi\data" mkdir "backend-fastapi\data"

REM 复制GeoIP数据库
if not exist "backend-fastapi\data\GeoLite2-City.mmdb" (
    if exist "API\GeoLite2-City.mmdb" (
        copy "API\GeoLite2-City.mmdb" "backend-fastapi\data\"
        echo [INFO] 已复制GeoIP数据库到FastAPI目录
    )
)

if "%command%"=="start" goto start
if "%command%"=="stop" goto stop
if "%command%"=="restart" goto restart
if "%command%"=="build" goto build
if "%command%"=="logs" goto logs
if "%command%"=="health" goto health
if "%command%"=="cleanup" goto cleanup
goto help

:start
echo [INFO] 启动服务...
if "%env%"=="dev" (
    docker-compose -f docker-compose.dev.yml build
    docker-compose -f docker-compose.dev.yml up -d
    echo [INFO] 开发环境服务启动中...
    echo [INFO] 前端: http://localhost:8080
    echo [INFO] FastAPI: http://localhost:8000
    echo [INFO] API文档: http://localhost:8000/docs
) else (
    docker-compose build
    docker-compose up -d
    echo [INFO] 生产环境服务启动中...
    echo [INFO] 主入口: http://localhost
    echo [INFO] 前端: http://localhost:8080
    echo [INFO] FastAPI: http://localhost:8000
    echo [INFO] Flask API: http://localhost:5000
    echo [INFO] API文档: http://localhost:8082/docs
)
echo [SUCCESS] 服务启动完成
goto end

:stop
echo [INFO] 停止服务...
if "%env%"=="dev" (
    docker-compose -f docker-compose.dev.yml down
) else (
    docker-compose down
)
echo [SUCCESS] 服务已停止
goto end

:restart
echo [INFO] 重启服务...
call :stop
call :start
goto end

:build
echo [INFO] 构建Docker镜像...
if "%env%"=="dev" (
    docker-compose -f docker-compose.dev.yml build
) else (
    docker-compose build
)
echo [SUCCESS] 镜像构建完成
goto end

:logs
echo [INFO] 查看日志...
if "%env%"=="dev" (
    docker-compose -f docker-compose.dev.yml logs -f
) else (
    docker-compose logs -f
)
goto end

:health
echo [INFO] 执行健康检查...
timeout /t 10 /nobreak >nul
docker-compose ps
echo [INFO] 健康检查完成
goto end

:cleanup
echo [INFO] 清理Docker资源...
if "%env%"=="dev" (
    docker-compose -f docker-compose.dev.yml down -v --rmi local
) else (
    docker-compose down -v --rmi local
)
docker system prune -f
echo [SUCCESS] 清理完成
goto end

:help
echo.
echo IP查询工具 - 容器化部署脚本
echo.
echo 用法: %0 [命令] [环境]
echo.
echo 命令:
echo   start     启动服务
echo   stop      停止服务
echo   restart   重启服务
echo   build     构建镜像
echo   logs      查看日志
echo   health    健康检查
echo   cleanup   清理资源
echo   help      显示帮助
echo.
echo 环境:
echo   prod      生产环境（默认）
echo   dev       开发环境
echo.
echo 示例:
echo   %0 start prod     # 启动生产环境
echo   %0 start dev      # 启动开发环境
echo   %0 logs           # 查看生产环境日志
echo.

:end
endlocal
