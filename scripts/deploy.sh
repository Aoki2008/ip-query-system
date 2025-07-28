#!/bin/bash

# IP查询工具 - 容器化部署脚本
# 支持生产环境和开发环境部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_requirements() {
    log_info "检查系统要求..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p nginx/conf.d
    mkdir -p API/logs
    mkdir -p backend-fastapi/data
    
    # 确保GeoIP数据库存在
    if [ ! -f "backend-fastapi/data/GeoLite2-City.mmdb" ] && [ -f "API/GeoLite2-City.mmdb" ]; then
        cp API/GeoLite2-City.mmdb backend-fastapi/data/
        log_info "已复制GeoIP数据库到FastAPI目录"
    fi
    
    log_success "目录创建完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml build
    else
        docker-compose build
    fi
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml up -d
        log_info "开发环境服务启动中..."
        log_info "前端: http://localhost:8080"
        log_info "FastAPI: http://localhost:8000"
        log_info "API文档: http://localhost:8000/docs"
    else
        docker-compose up -d
        log_info "生产环境服务启动中..."
        log_info "主入口: http://localhost"
        log_info "前端: http://localhost:8080"
        log_info "FastAPI: http://localhost:8000"
        log_info "Flask API: http://localhost:5000"
        log_info "Nginx状态: http://localhost:8081/nginx_status"
        log_info "API文档: http://localhost:8082/docs"
    fi
    
    log_success "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    sleep 10  # 等待服务启动
    
    # 检查服务状态
    if [ "$1" = "dev" ]; then
        services=("redis" "backend-fastapi-dev" "frontend-dev")
    else
        services=("redis" "backend-fastapi" "backend-flask" "frontend" "nginx")
    fi
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log_success "$service 服务运行正常"
        else
            log_error "$service 服务启动失败"
            return 1
        fi
    done
    
    # 检查API健康状态
    if [ "$1" != "dev" ]; then
        if curl -f http://localhost/health > /dev/null 2>&1; then
            log_success "Nginx健康检查通过"
        else
            log_warning "Nginx健康检查失败"
        fi
    fi
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "FastAPI健康检查通过"
    else
        log_warning "FastAPI健康检查失败"
    fi
    
    log_success "健康检查完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml down
    else
        docker-compose down
    fi
    
    log_success "服务已停止"
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml down -v --rmi local
    else
        docker-compose down -v --rmi local
    fi
    
    docker system prune -f
    log_success "清理完成"
}

# 显示日志
show_logs() {
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# 显示帮助信息
show_help() {
    echo "IP查询工具 - 容器化部署脚本"
    echo ""
    echo "用法: $0 [命令] [环境]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  build     构建镜像"
    echo "  logs      查看日志"
    echo "  health    健康检查"
    echo "  cleanup   清理资源"
    echo "  help      显示帮助"
    echo ""
    echo "环境:"
    echo "  prod      生产环境（默认）"
    echo "  dev       开发环境"
    echo ""
    echo "示例:"
    echo "  $0 start prod     # 启动生产环境"
    echo "  $0 start dev      # 启动开发环境"
    echo "  $0 logs           # 查看生产环境日志"
    echo "  $0 logs dev       # 查看开发环境日志"
}

# 主函数
main() {
    local command=${1:-help}
    local env=${2:-prod}
    
    case $command in
        start)
            check_requirements
            create_directories
            build_images $env
            start_services $env
            health_check $env
            ;;
        stop)
            stop_services $env
            ;;
        restart)
            stop_services $env
            start_services $env
            health_check $env
            ;;
        build)
            check_requirements
            create_directories
            build_images $env
            ;;
        logs)
            show_logs $env
            ;;
        health)
            health_check $env
            ;;
        cleanup)
            cleanup $env
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
