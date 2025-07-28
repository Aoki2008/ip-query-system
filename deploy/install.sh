#!/bin/bash

# IP查询系统一键部署脚本
# 支持CentOS 7+, Ubuntu 18.04+, Debian 9+

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/redhat-release ]]; then
        OS="centos"
        log_info "检测到CentOS系统"
    elif [[ -f /etc/lsb-release ]]; then
        OS="ubuntu"
        log_info "检测到Ubuntu系统"
    elif [[ -f /etc/debian_version ]]; then
        OS="debian"
        log_info "检测到Debian系统"
    else
        log_error "不支持的操作系统"
        exit 1
    fi
}

# 安装Docker
install_docker() {
    log_step "安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker已安装，跳过安装步骤"
        return
    fi

    case $OS in
        "centos")
            yum update -y
            yum install -y yum-utils device-mapper-persistent-data lvm2
            yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            yum install -y docker-ce docker-ce-cli containerd.io
            ;;
        "ubuntu"|"debian")
            apt-get update
            apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
            apt-get update
            apt-get install -y docker-ce docker-ce-cli containerd.io
            ;;
    esac

    systemctl start docker
    systemctl enable docker
    log_info "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_step "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装，跳过安装步骤"
        return
    fi

    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_info "Docker Compose安装完成"
}

# 创建项目目录
create_directories() {
    log_step "创建项目目录..."
    
    PROJECT_DIR="/opt/ip-query-system"
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # 创建必要的目录
    mkdir -p {logs,data,uploads,backups}
    mkdir -p {mysql_data,redis_data}
    mkdir -p nginx/{conf.d,ssl,logs}
    
    log_info "项目目录创建完成: $PROJECT_DIR"
}

# 生成配置文件
generate_configs() {
    log_step "生成配置文件..."
    
    # 生成随机密码
    DB_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 64)
    APP_KEY=$(openssl rand -base64 32)
    
    # 创建.env文件
    cat > .env << EOF
# 数据库配置
DB_PASSWORD=$DB_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD

# 应用密钥
JWT_SECRET=$JWT_SECRET
LARAVEL_APP_KEY=base64:$APP_KEY

# 域名配置（请修改为您的域名）
FRONTEND_DOMAIN=localhost
API_DOMAIN=api.localhost
ADMIN_DOMAIN=admin.localhost

# MaxMind配置（请填入您的许可证密钥）
MAXMIND_LICENSE_KEY=your_license_key_here

# 邮件配置（可选）
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EOF

    log_info "配置文件生成完成"
    log_warn "请编辑 .env 文件，填入您的域名和MaxMind许可证密钥"
}

# 下载MaxMind数据库
download_maxmind_db() {
    log_step "下载MaxMind数据库..."
    
    if [[ ! -f "data/GeoLite2-City.mmdb" ]]; then
        log_warn "请手动下载GeoLite2-City.mmdb文件到 data/ 目录"
        log_info "下载地址: https://www.maxmind.com/en/accounts/current/geoip/downloads"
    else
        log_info "MaxMind数据库已存在"
    fi
}

# 启动服务
start_services() {
    log_step "启动服务..."
    
    # 检查docker-compose.yml是否存在
    if [[ ! -f "docker-compose.yml" ]]; then
        log_error "docker-compose.yml文件不存在，请确保项目文件完整"
        exit 1
    fi
    
    # 构建并启动服务
    docker-compose up -d --build
    
    log_info "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_step "等待服务就绪..."
    
    # 等待MySQL启动
    log_info "等待MySQL启动..."
    while ! docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
        sleep 2
    done
    
    # 等待Redis启动
    log_info "等待Redis启动..."
    while ! docker-compose exec redis redis-cli ping; do
        sleep 2
    done
    
    log_info "所有服务已就绪"
}

# 初始化数据库
init_database() {
    log_step "初始化数据库..."
    
    # 运行数据库迁移
    docker-compose exec admin-panel php artisan migrate --force
    docker-compose exec admin-panel php artisan db:seed --force
    
    log_info "数据库初始化完成"
}

# 显示访问信息
show_access_info() {
    log_step "部署完成！"
    
    echo ""
    echo "=========================================="
    echo "IP查询系统部署完成"
    echo "=========================================="
    echo ""
    echo "访问地址："
    echo "  前端应用: http://localhost"
    echo "  API服务:  http://localhost:3001"
    echo "  管理后台: http://localhost:8080"
    echo ""
    echo "默认管理员账号："
    echo "  用户名: admin"
    echo "  密码: admin123"
    echo ""
    echo "重要提醒："
    echo "  1. 请修改默认管理员密码"
    echo "  2. 请配置您的域名和SSL证书"
    echo "  3. 请填入MaxMind许可证密钥"
    echo "  4. 生产环境请修改所有默认密码"
    echo ""
    echo "日志查看："
    echo "  docker-compose logs -f [service_name]"
    echo ""
    echo "服务管理："
    echo "  启动: docker-compose up -d"
    echo "  停止: docker-compose down"
    echo "  重启: docker-compose restart"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始部署IP查询系统..."
    
    check_root
    detect_os
    install_docker
    install_docker_compose
    create_directories
    generate_configs
    download_maxmind_db
    start_services
    wait_for_services
    init_database
    show_access_info
    
    log_info "部署完成！"
}

# 执行主函数
main "$@"
