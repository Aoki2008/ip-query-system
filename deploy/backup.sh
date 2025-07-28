#!/bin/bash

# IP查询系统备份脚本
# 用于备份数据库、配置文件和重要数据

set -e

# 配置
PROJECT_DIR="/opt/ip-query-system"
BACKUP_DIR="$PROJECT_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查Docker Compose是否运行
check_services() {
    log_info "检查服务状态..."
    
    cd $PROJECT_DIR
    
    if ! docker-compose ps | grep -q "Up"; then
        log_error "Docker Compose服务未运行"
        exit 1
    fi
    
    log_info "服务状态正常"
}

# 创建备份目录
create_backup_dir() {
    log_info "创建备份目录..."
    
    mkdir -p $BACKUP_DIR
    
    # 创建当日备份目录
    DAILY_BACKUP_DIR="$BACKUP_DIR/$DATE"
    mkdir -p $DAILY_BACKUP_DIR
    
    log_info "备份目录: $DAILY_BACKUP_DIR"
}

# 备份MySQL数据库
backup_mysql() {
    log_info "备份MySQL数据库..."
    
    # 从环境变量获取数据库密码
    DB_PASSWORD=$(grep "DB_PASSWORD=" $PROJECT_DIR/.env | cut -d'=' -f2)
    
    if [[ -z "$DB_PASSWORD" ]]; then
        log_error "无法获取数据库密码"
        return 1
    fi
    
    # 备份数据库
    docker-compose exec -T mysql mysqldump \
        -u root \
        -p$DB_PASSWORD \
        --single-transaction \
        --routines \
        --triggers \
        ip_query_system > $DAILY_BACKUP_DIR/mysql_backup.sql
    
    if [[ $? -eq 0 ]]; then
        log_info "MySQL数据库备份完成"
        
        # 压缩备份文件
        gzip $DAILY_BACKUP_DIR/mysql_backup.sql
        log_info "数据库备份文件已压缩"
    else
        log_error "MySQL数据库备份失败"
        return 1
    fi
}

# 备份Redis数据
backup_redis() {
    log_info "备份Redis数据..."
    
    # 触发Redis保存
    docker-compose exec -T redis redis-cli BGSAVE
    
    # 等待保存完成
    sleep 5
    
    # 复制RDB文件
    docker cp $(docker-compose ps -q redis):/data/dump.rdb $DAILY_BACKUP_DIR/redis_backup.rdb
    
    if [[ $? -eq 0 ]]; then
        log_info "Redis数据备份完成"
        
        # 压缩备份文件
        gzip $DAILY_BACKUP_DIR/redis_backup.rdb
        log_info "Redis备份文件已压缩"
    else
        log_error "Redis数据备份失败"
        return 1
    fi
}

# 备份配置文件
backup_configs() {
    log_info "备份配置文件..."
    
    # 创建配置备份目录
    CONFIG_BACKUP_DIR="$DAILY_BACKUP_DIR/configs"
    mkdir -p $CONFIG_BACKUP_DIR
    
    # 备份环境变量文件
    cp $PROJECT_DIR/.env $CONFIG_BACKUP_DIR/
    
    # 备份Docker Compose文件
    cp $PROJECT_DIR/docker-compose.yml $CONFIG_BACKUP_DIR/
    
    # 备份Nginx配置
    cp -r $PROJECT_DIR/nginx $CONFIG_BACKUP_DIR/
    
    # 备份数据库初始化脚本
    cp -r $PROJECT_DIR/database $CONFIG_BACKUP_DIR/
    
    log_info "配置文件备份完成"
}

# 备份上传文件和日志
backup_data() {
    log_info "备份数据文件..."
    
    # 创建数据备份目录
    DATA_BACKUP_DIR="$DAILY_BACKUP_DIR/data"
    mkdir -p $DATA_BACKUP_DIR
    
    # 备份MaxMind数据库文件
    if [[ -f "$PROJECT_DIR/data/GeoLite2-City.mmdb" ]]; then
        cp $PROJECT_DIR/data/GeoLite2-City.mmdb $DATA_BACKUP_DIR/
        log_info "MaxMind数据库文件备份完成"
    fi
    
    # 备份上传文件
    if [[ -d "$PROJECT_DIR/uploads" ]]; then
        cp -r $PROJECT_DIR/uploads $DATA_BACKUP_DIR/
        log_info "上传文件备份完成"
    fi
    
    # 备份最近的日志文件（最近3天）
    LOG_BACKUP_DIR="$DATA_BACKUP_DIR/logs"
    mkdir -p $LOG_BACKUP_DIR
    
    find $PROJECT_DIR/logs -name "*.log" -mtime -3 -exec cp {} $LOG_BACKUP_DIR/ \;
    log_info "日志文件备份完成"
}

# 创建备份清单
create_manifest() {
    log_info "创建备份清单..."
    
    MANIFEST_FILE="$DAILY_BACKUP_DIR/backup_manifest.txt"
    
    cat > $MANIFEST_FILE << EOF
IP查询系统备份清单
==================

备份时间: $(date)
备份版本: $DATE
项目目录: $PROJECT_DIR

备份内容:
- MySQL数据库: mysql_backup.sql.gz
- Redis数据: redis_backup.rdb.gz
- 配置文件: configs/
- 数据文件: data/

文件列表:
EOF
    
    # 添加文件列表
    find $DAILY_BACKUP_DIR -type f -exec ls -lh {} \; >> $MANIFEST_FILE
    
    log_info "备份清单创建完成"
}

# 压缩备份
compress_backup() {
    log_info "压缩备份文件..."
    
    cd $BACKUP_DIR
    tar -czf "backup_$DATE.tar.gz" $DATE/
    
    if [[ $? -eq 0 ]]; then
        # 删除未压缩的目录
        rm -rf $DATE/
        log_info "备份压缩完成: backup_$DATE.tar.gz"
    else
        log_error "备份压缩失败"
        return 1
    fi
}

# 清理过期备份
cleanup_old_backups() {
    log_info "清理过期备份..."
    
    # 删除超过保留天数的备份文件
    find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    
    # 删除超过保留天数的目录（如果有）
    find $BACKUP_DIR -type d -name "20*" -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    log_info "过期备份清理完成"
}

# 验证备份
verify_backup() {
    log_info "验证备份文件..."
    
    BACKUP_FILE="$BACKUP_DIR/backup_$DATE.tar.gz"
    
    if [[ -f "$BACKUP_FILE" ]]; then
        # 检查文件大小
        SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_info "备份文件大小: $SIZE"
        
        # 测试压缩文件完整性
        if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
            log_info "备份文件完整性验证通过"
        else
            log_error "备份文件损坏"
            return 1
        fi
    else
        log_error "备份文件不存在"
        return 1
    fi
}

# 发送通知（可选）
send_notification() {
    log_info "发送备份通知..."
    
    # 这里可以添加邮件通知或其他通知方式
    # 例如：发送到Slack、钉钉等
    
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/backup_$DATE.tar.gz" | cut -f1)
    
    # 示例：写入系统日志
    logger "IP查询系统备份完成 - 时间: $DATE, 大小: $BACKUP_SIZE"
    
    log_info "备份通知已发送"
}

# 主函数
main() {
    log_info "开始备份IP查询系统..."
    
    # 检查是否在正确的目录
    if [[ ! -f "$PROJECT_DIR/docker-compose.yml" ]]; then
        log_error "项目目录不存在或配置错误: $PROJECT_DIR"
        exit 1
    fi
    
    # 执行备份步骤
    check_services
    create_backup_dir
    backup_mysql
    backup_redis
    backup_configs
    backup_data
    create_manifest
    compress_backup
    cleanup_old_backups
    verify_backup
    send_notification
    
    log_info "备份完成！备份文件: backup_$DATE.tar.gz"
}

# 错误处理
trap 'log_error "备份过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"
