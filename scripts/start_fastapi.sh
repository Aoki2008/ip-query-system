#!/bin/bash

# 🚀 IP查询系统 - FastAPI后端启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo ""
echo "🚀 IP查询系统 - FastAPI后端启动脚本"
echo "=========================================="

# 检查是否在项目根目录
if [ ! -d "backend-fastapi" ]; then
    log_error "请在项目根目录运行此脚本"
    log_error "当前目录: $(pwd)"
    exit 1
fi

log_info "📁 切换到后端目录..."
cd backend-fastapi

log_info "🐍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        log_error "未找到Python，请先安装Python 3.11+"
        log_info "💡 安装指南: https://www.python.org/downloads/"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

log_success "Python环境检查通过"

log_info "📦 检查依赖包..."
if [ ! -f "requirements.txt" ]; then
    log_error "未找到requirements.txt文件"
    exit 1
fi

log_info "🔧 安装/更新依赖包..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    log_error "依赖包安装失败"
    exit 1
fi

log_success "依赖包检查完成"

log_info "📊 检查数据文件..."
if [ ! -f "data/GeoLite2-City.mmdb" ]; then
    log_warning "未找到GeoLite2-City.mmdb数据文件"
    log_info "💡 请从MaxMind官网下载并放置在data目录下"
    log_info "🔗 https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
fi

echo ""
log_info "🚀 启动FastAPI服务器..."
log_info "📍 服务地址: http://localhost:8000"
log_info "📖 API文档: http://localhost:8000/docs"
echo ""

$PYTHON_CMD main.py

echo ""
log_info "🛑 服务已停止"
