#!/bin/bash

# IP查询系统 - 快速开始脚本
# 用于快速设置和上传项目到GitHub

set -e

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

# 显示欢迎信息
show_welcome() {
    clear
    echo ""
    echo "=========================================="
    echo "🚀 IP查询系统 - 快速开始"
    echo "=========================================="
    echo ""
    echo "这个脚本将帮助您："
    echo "1. 检查项目完整性"
    echo "2. 设置必要的权限"
    echo "3. 上传代码到GitHub"
    echo "4. 提供部署指导"
    echo ""
}

# 检查项目完整性
check_project() {
    log_step "检查项目完整性..."
    
    # 检查核心目录
    directories=("api-system" "admin-panel" "ip-tool" "database" "docs" "deploy")
    missing_dirs=()
    
    for dir in "${directories[@]}"; do
        if [[ -d "$dir" ]]; then
            log_info "✓ $dir 目录存在"
        else
            log_warn "✗ $dir 目录缺失"
            missing_dirs+=("$dir")
        fi
    done
    
    # 检查核心文件
    files=("README.md" "docker-compose.yml" ".gitignore" "LICENSE")
    missing_files=()
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            log_info "✓ $file 文件存在"
        else
            log_warn "✗ $file 文件缺失"
            missing_files+=("$file")
        fi
    done
    
    # 报告缺失项
    if [[ ${#missing_dirs[@]} -gt 0 || ${#missing_files[@]} -gt 0 ]]; then
        log_warn "发现缺失的文件或目录，但可以继续"
    else
        log_info "项目完整性检查通过"
    fi
}

# 设置权限
set_permissions() {
    log_step "设置脚本权限..."
    
    # 给脚本添加执行权限
    scripts=("upload-to-github.sh" "deploy/install.sh" "deploy/backup.sh" "deploy/restore.sh")
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            chmod +x "$script"
            log_info "✓ $script 权限已设置"
        else
            log_warn "✗ $script 文件不存在"
        fi
    done
}

# 显示选项菜单
show_menu() {
    echo ""
    echo "请选择您要执行的操作："
    echo ""
    echo "1) 上传代码到GitHub"
    echo "2) 本地Docker部署"
    echo "3) 查看项目信息"
    echo "4) 查看帮助文档"
    echo "5) 退出"
    echo ""
}

# 上传到GitHub
upload_to_github() {
    log_step "准备上传到GitHub..."
    
    if [[ -f "upload-to-github.sh" ]]; then
        log_info "运行GitHub上传脚本..."
        ./upload-to-github.sh
    else
        log_error "upload-to-github.sh 脚本不存在"
        echo ""
        echo "您可以手动执行以下命令："
        echo "git init"
        echo "git add ."
        echo "git commit -m 'feat: initial commit'"
        echo "git branch -M main"
        echo "git remote add origin https://github.com/your-username/ip-query-system.git"
        echo "git push -u origin main"
    fi
}

# 本地部署
local_deploy() {
    log_step "准备本地部署..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        echo "安装指南: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        echo "安装指南: https://docs.docker.com/compose/install/"
        return 1
    fi
    
    # 检查配置文件
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            log_info "复制环境变量模板..."
            cp .env.example .env
            log_warn "请编辑 .env 文件，配置必要的参数"
            echo "主要配置项："
            echo "- DB_PASSWORD: 数据库密码"
            echo "- REDIS_PASSWORD: Redis密码"
            echo "- JWT_SECRET: JWT密钥"
            echo "- MAXMIND_LICENSE_KEY: MaxMind许可证密钥"
        else
            log_error ".env.example 文件不存在，无法创建配置文件"
            return 1
        fi
    fi
    
    # 启动服务
    log_info "启动Docker服务..."
    if docker-compose up -d; then
        log_info "服务启动成功！"
        echo ""
        echo "访问地址："
        echo "- 前端应用: http://localhost:3000"
        echo "- API服务: http://localhost:3001"
        echo "- 管理后台: http://localhost:8080"
    else
        log_error "服务启动失败，请检查配置"
    fi
}

# 显示项目信息
show_project_info() {
    log_step "项目信息"
    
    echo ""
    echo "=========================================="
    echo "IP查询系统项目信息"
    echo "=========================================="
    echo ""
    echo "📁 项目结构："
    echo "├── api-system/          # Node.js API服务"
    echo "├── admin-panel/         # Laravel管理后台"
    echo "├── ip-tool/            # Next.js前端应用"
    echo "├── database/           # 数据库文件"
    echo "├── docs/               # 项目文档"
    echo "├── deploy/             # 部署脚本"
    echo "└── nginx/              # Nginx配置"
    echo ""
    echo "🔧 技术栈："
    echo "- 前端: Next.js 14 + React 18 + TypeScript"
    echo "- API: Node.js + Express + TypeScript"
    echo "- 后端: Laravel 10 + PHP 8.1"
    echo "- 数据库: MySQL 8.0 + Redis 7.0"
    echo "- 部署: Docker + Docker Compose + Nginx"
    echo ""
    echo "🚀 主要功能："
    echo "- IP地址查询（单个/批量）"
    echo "- 用户管理和认证"
    echo "- API密钥管理"
    echo "- 限流和缓存"
    echo "- 管理后台"
    echo "- 完整的API文档"
    echo ""
    echo "📖 文档："
    echo "- README.md - 项目说明"
    echo "- docs/api.md - API文档"
    echo "- docs/deployment.md - 部署指南"
    echo "- GITHUB_UPLOAD_GUIDE.md - GitHub上传指南"
    echo ""
}

# 显示帮助
show_help() {
    log_step "帮助文档"
    
    echo ""
    echo "=========================================="
    echo "帮助文档"
    echo "=========================================="
    echo ""
    echo "📚 可用文档："
    echo ""
    
    if [[ -f "README.md" ]]; then
        echo "✓ README.md - 项目总体说明"
    fi
    
    if [[ -f "GITHUB_UPLOAD_GUIDE.md" ]]; then
        echo "✓ GITHUB_UPLOAD_GUIDE.md - GitHub上传详细指南"
    fi
    
    if [[ -f "docs/api.md" ]]; then
        echo "✓ docs/api.md - API接口文档"
    fi
    
    if [[ -f "docs/deployment.md" ]]; then
        echo "✓ docs/deployment.md - 部署指南"
    fi
    
    if [[ -f "CONTRIBUTING.md" ]]; then
        echo "✓ CONTRIBUTING.md - 贡献指南"
    fi
    
    echo ""
    echo "🔧 常用命令："
    echo ""
    echo "上传到GitHub:"
    echo "  ./upload-to-github.sh"
    echo ""
    echo "本地部署:"
    echo "  docker-compose up -d"
    echo ""
    echo "查看日志:"
    echo "  docker-compose logs -f"
    echo ""
    echo "停止服务:"
    echo "  docker-compose down"
    echo ""
    echo "📞 获取支持："
    echo "- 查看文档目录中的详细说明"
    echo "- 创建GitHub Issue"
    echo "- 发送邮件: support@example.com"
    echo ""
}

# 主循环
main_loop() {
    while true; do
        show_menu
        read -p "请输入选项 (1-5): " choice
        
        case $choice in
            1)
                upload_to_github
                ;;
            2)
                local_deploy
                ;;
            3)
                show_project_info
                ;;
            4)
                show_help
                ;;
            5)
                log_info "感谢使用IP查询系统！"
                exit 0
                ;;
            *)
                log_error "无效选项，请输入1-5"
                ;;
        esac
        
        echo ""
        read -p "按Enter键继续..."
    done
}

# 主函数
main() {
    show_welcome
    check_project
    set_permissions
    main_loop
}

# 错误处理
trap 'log_error "脚本执行出错，退出码: $?"' ERR

# 执行主函数
main "$@"
