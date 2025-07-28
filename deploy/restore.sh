#!/bin/bash

# IP查询系统恢复脚本
# 用于从备份文件恢复系统

set -e

# 配置
PROJECT_DIR="/opt/ip-query-system"
BACKUP_DIR="$PROJECT_DIR/backups"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 显示使用说明
show_usage() {
    echo "使用方法: $0 <backup_file>"
    echo ""
    echo "参数:"
    echo "  backup_file    备份文件路径（.tar.gz格式）"
    echo ""
    echo "示例:"
    echo "  $0 /opt/ip-query-system/backups/backup_20240101_020000.tar.gz"
    echo "  $0 backup_20240101_020000.tar.gz  # 相对于备份目录"
    echo ""
    echo "可用的备份文件:"
    if [[ -d "$BACKUP_DIR" ]]; then
        ls -la $BACKUP_DIR/backup_*.tar.gz 2>/dev/null || echo "  无可用备份文件"
    fi
}

# 检查参数
check_params() {
    if [[ $# -eq 0 ]]; then
        log_error "请指定备份文件"
        show_usage
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    # 如果是相对路径，添加备份目录前缀
    if [[ ! "$BACKUP_FILE" = /* ]]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    fi
    
    if [[ ! -f "$BACKUP_FILE" ]]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
    
    log_info "使用备份文件: $BACKUP_FILE"
}

# 确认恢复操作
confirm_restore() {
    log_warn "警告：恢复操作将覆盖当前的所有数据！"
    log_warn "请确保您已经备份了当前的重要数据。"
    echo ""
    
    read -p "确定要继续恢复操作吗？(yes/no): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        log_info "恢复操作已取消"
        exit 0
    fi
}

# 停止服务
stop_services() {
    log_step "停止服务..."
    
    cd $PROJECT_DIR
    
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        log_info "服务已停止"
    else
        log_info "服务未运行，跳过停止步骤"
    fi
}

# 解压备份文件
extract_backup() {
    log_step "解压备份文件..."
    
    # 创建临时目录
    TEMP_DIR="/tmp/ip-query-restore-$(date +%s)"
    mkdir -p $TEMP_DIR
    
    # 解压备份文件
    tar -xzf "$BACKUP_FILE" -C $TEMP_DIR
    
    # 查找解压后的目录
    BACKUP_CONTENT_DIR=$(find $TEMP_DIR -maxdepth 1 -type d -name "20*" | head -1)
    
    if [[ -z "$BACKUP_CONTENT_DIR" ]]; then
        log_error "备份文件格式错误，找不到备份内容目录"
        rm -rf $TEMP_DIR
        exit 1
    fi
    
    log_info "备份文件解压完成: $BACKUP_CONTENT_DIR"
}

# 恢复配置文件
restore_configs() {
    log_step "恢复配置文件..."
    
    CONFIG_BACKUP_DIR="$BACKUP_CONTENT_DIR/configs"
    
    if [[ ! -d "$CONFIG_BACKUP_DIR" ]]; then
        log_warn "配置文件备份不存在，跳过恢复"
        return
    fi
    
    # 备份当前配置
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        cp "$PROJECT_DIR/.env" "$PROJECT_DIR/.env.backup.$(date +%s)"
        log_info "当前配置文件已备份"
    fi
    
    # 恢复配置文件
    if [[ -f "$CONFIG_BACKUP_DIR/.env" ]]; then
        cp "$CONFIG_BACKUP_DIR/.env" "$PROJECT_DIR/"
        log_info "环境变量文件已恢复"
    fi
    
    if [[ -f "$CONFIG_BACKUP_DIR/docker-compose.yml" ]]; then
        cp "$CONFIG_BACKUP_DIR/docker-compose.yml" "$PROJECT_DIR/"
        log_info "Docker Compose文件已恢复"
    fi
    
    if [[ -d "$CONFIG_BACKUP_DIR/nginx" ]]; then
        rm -rf "$PROJECT_DIR/nginx"
        cp -r "$CONFIG_BACKUP_DIR/nginx" "$PROJECT_DIR/"
        log_info "Nginx配置已恢复"
    fi
    
    log_info "配置文件恢复完成"
}

# 恢复数据文件
restore_data() {
    log_step "恢复数据文件..."
    
    DATA_BACKUP_DIR="$BACKUP_CONTENT_DIR/data"
    
    if [[ ! -d "$DATA_BACKUP_DIR" ]]; then
        log_warn "数据文件备份不存在，跳过恢复"
        return
    fi
    
    # 恢复MaxMind数据库
    if [[ -f "$DATA_BACKUP_DIR/GeoLite2-City.mmdb" ]]; then
        mkdir -p "$PROJECT_DIR/data"
        cp "$DATA_BACKUP_DIR/GeoLite2-City.mmdb" "$PROJECT_DIR/data/"
        log_info "MaxMind数据库已恢复"
    fi
    
    # 恢复上传文件
    if [[ -d "$DATA_BACKUP_DIR/uploads" ]]; then
        rm -rf "$PROJECT_DIR/uploads"
        cp -r "$DATA_BACKUP_DIR/uploads" "$PROJECT_DIR/"
        log_info "上传文件已恢复"
    fi
    
    log_info "数据文件恢复完成"
}

# 启动基础服务
start_base_services() {
    log_step "启动基础服务..."
    
    cd $PROJECT_DIR
    
    # 只启动MySQL和Redis
    docker-compose up -d mysql redis
    
    log_info "等待数据库服务启动..."
    sleep 30
    
    # 检查MySQL是否就绪
    while ! docker-compose exec mysql mysqladmin ping -h"localhost" --silent; do
        log_info "等待MySQL启动..."
        sleep 5
    done
    
    # 检查Redis是否就绪
    while ! docker-compose exec redis redis-cli ping > /dev/null 2>&1; do
        log_info "等待Redis启动..."
        sleep 5
    done
    
    log_info "基础服务启动完成"
}

# 恢复MySQL数据库
restore_mysql() {
    log_step "恢复MySQL数据库..."
    
    MYSQL_BACKUP_FILE="$BACKUP_CONTENT_DIR/mysql_backup.sql.gz"
    
    if [[ ! -f "$MYSQL_BACKUP_FILE" ]]; then
        log_error "MySQL备份文件不存在: $MYSQL_BACKUP_FILE"
        return 1
    fi
    
    # 获取数据库密码
    DB_PASSWORD=$(grep "DB_PASSWORD=" $PROJECT_DIR/.env | cut -d'=' -f2)
    
    if [[ -z "$DB_PASSWORD" ]]; then
        log_error "无法获取数据库密码"
        return 1
    fi
    
    # 删除现有数据库
    docker-compose exec mysql mysql -u root -p$DB_PASSWORD -e "DROP DATABASE IF EXISTS ip_query_system;"
    docker-compose exec mysql mysql -u root -p$DB_PASSWORD -e "CREATE DATABASE ip_query_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    
    # 恢复数据库
    zcat "$MYSQL_BACKUP_FILE" | docker-compose exec -T mysql mysql -u root -p$DB_PASSWORD ip_query_system
    
    if [[ $? -eq 0 ]]; then
        log_info "MySQL数据库恢复完成"
    else
        log_error "MySQL数据库恢复失败"
        return 1
    fi
}

# 恢复Redis数据
restore_redis() {
    log_step "恢复Redis数据..."
    
    REDIS_BACKUP_FILE="$BACKUP_CONTENT_DIR/redis_backup.rdb.gz"
    
    if [[ ! -f "$REDIS_BACKUP_FILE" ]]; then
        log_warn "Redis备份文件不存在，跳过恢复"
        return
    fi
    
    # 停止Redis服务
    docker-compose stop redis
    
    # 解压并复制RDB文件
    zcat "$REDIS_BACKUP_FILE" > /tmp/dump.rdb
    docker cp /tmp/dump.rdb $(docker-compose ps -q redis):/data/dump.rdb
    rm /tmp/dump.rdb
    
    # 重启Redis服务
    docker-compose start redis
    
    # 等待Redis启动
    sleep 10
    
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        log_info "Redis数据恢复完成"
    else
        log_error "Redis数据恢复失败"
        return 1
    fi
}

# 启动所有服务
start_all_services() {
    log_step "启动所有服务..."
    
    cd $PROJECT_DIR
    
    # 启动所有服务
    docker-compose up -d
    
    log_info "等待所有服务启动..."
    sleep 30
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_info "所有服务启动完成"
    else
        log_error "部分服务启动失败"
        docker-compose ps
        return 1
    fi
}

# 验证恢复结果
verify_restore() {
    log_step "验证恢复结果..."
    
    # 检查前端应用
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        log_info "前端应用正常"
    else
        log_warn "前端应用可能有问题"
    fi
    
    # 检查API服务
    if curl -f http://localhost:3001/health > /dev/null 2>&1; then
        log_info "API服务正常"
    else
        log_warn "API服务可能有问题"
    fi
    
    # 检查管理后台
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        log_info "管理后台正常"
    else
        log_warn "管理后台可能有问题"
    fi
    
    # 检查数据库连接
    if docker-compose exec mysql mysql -u root -p$(grep "DB_PASSWORD=" $PROJECT_DIR/.env | cut -d'=' -f2) -e "SELECT 1;" > /dev/null 2>&1; then
        log_info "数据库连接正常"
    else
        log_warn "数据库连接可能有问题"
    fi
    
    log_info "恢复验证完成"
}

# 清理临时文件
cleanup() {
    log_step "清理临时文件..."
    
    if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
        log_info "临时文件清理完成"
    fi
}

# 显示恢复结果
show_result() {
    log_step "恢复完成！"
    
    echo ""
    echo "=========================================="
    echo "IP查询系统恢复完成"
    echo "=========================================="
    echo ""
    echo "访问地址："
    echo "  前端应用: http://localhost:3000"
    echo "  API服务:  http://localhost:3001"
    echo "  管理后台: http://localhost:8080"
    echo ""
    echo "请检查以下内容："
    echo "  1. 所有服务是否正常运行"
    echo "  2. 数据是否完整恢复"
    echo "  3. 配置是否正确"
    echo ""
    echo "如有问题，请查看日志："
    echo "  docker-compose logs -f"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始恢复IP查询系统..."
    
    check_params "$@"
    confirm_restore
    stop_services
    extract_backup
    restore_configs
    restore_data
    start_base_services
    restore_mysql
    restore_redis
    start_all_services
    verify_restore
    cleanup
    show_result
    
    log_info "恢复完成！"
}

# 错误处理
trap 'log_error "恢复过程中发生错误，退出码: $?"; cleanup' ERR

# 执行主函数
main "$@"
