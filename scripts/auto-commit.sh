#!/bin/bash

# 🔄 自动Git提交脚本
# 用法: ./scripts/auto-commit.sh [提交信息]

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

# 检查是否在git仓库中
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
}

# 检查是否有未提交的更改
check_changes() {
    if git diff-index --quiet HEAD --; then
        log_warning "没有检测到未提交的更改"
        return 1
    fi
    return 0
}

# 生成自动提交信息
generate_commit_message() {
    local custom_message="$1"
    
    if [ -n "$custom_message" ]; then
        echo "$custom_message"
        return
    fi
    
    # 获取更改的文件
    local changed_files=$(git diff --name-only HEAD)
    local added_files=$(git diff --cached --name-only)
    local file_count=$(echo "$changed_files $added_files" | tr ' ' '\n' | sort -u | wc -l)
    
    # 根据更改类型生成提交信息
    local commit_type="📝"
    local commit_scope=""
    
    # 检查文件类型
    if echo "$changed_files $added_files" | grep -q "\.md$"; then
        commit_type="📝"
        commit_scope="docs"
    elif echo "$changed_files $added_files" | grep -q "\.py$"; then
        commit_type="🐍"
        commit_scope="backend"
    elif echo "$changed_files $added_files" | grep -q "\.vue$\|\.ts$\|\.js$"; then
        commit_type="🌐"
        commit_scope="frontend"
    elif echo "$changed_files $added_files" | grep -q "docker\|\.yml$\|\.yaml$"; then
        commit_type="🐳"
        commit_scope="deploy"
    elif echo "$changed_files $added_files" | grep -q "\.json$\|package"; then
        commit_type="📦"
        commit_scope="deps"
    fi
    
    # 生成时间戳
    local timestamp=$(date '+%Y-%m-%d %H:%M')
    
    echo "${commit_type} 自动提交 - ${commit_scope} (${file_count}个文件) - ${timestamp}"
}

# 执行自动提交
auto_commit() {
    local commit_message="$1"
    local auto_push="$2"

    log_info "开始自动Git提交流程..."
    
    # 检查Git仓库
    check_git_repo
    
    # 检查是否有更改
    if ! check_changes; then
        log_warning "没有需要提交的更改，退出"
        exit 0
    fi
    
    # 显示当前状态
    log_info "当前Git状态:"
    git status --short
    
    # 添加所有更改
    log_info "添加所有更改到暂存区..."
    git add .
    
    # 生成提交信息
    local final_message=$(generate_commit_message "$commit_message")
    log_info "提交信息: $final_message"
    
    # 执行提交
    log_info "执行提交..."
    git commit -m "$final_message"
    log_success "提交完成!"
    
    # 推送到远程
    if [ "$auto_push" = "true" ]; then
        log_info "自动推送到远程仓库..."
        git push origin main
        log_success "推送完成!"
    else
        read -p "是否推送到远程仓库? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "推送到远程仓库..."
            git push origin main
            log_success "推送完成!"
        else
            log_info "跳过推送，可以稍后手动执行: git push origin main"
        fi
    fi
}

# 显示帮助信息
show_help() {
    echo "🔄 自动Git提交脚本"
    echo ""
    echo "用法:"
    echo "  $0 [选项] [提交信息]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -f, --force    强制提交（跳过确认）"
    echo "  -p, --push     自动推送到远程"
    echo ""
    echo "示例:"
    echo "  $0                           # 自动生成提交信息"
    echo "  $0 \"修复登录bug\"             # 使用自定义提交信息"
    echo "  $0 -p \"更新文档\"             # 提交并自动推送"
}

# 主函数
main() {
    local commit_message=""
    local auto_push=false
    local force_commit=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                force_commit=true
                shift
                ;;
            -p|--push)
                auto_push=true
                shift
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                commit_message="$1"
                shift
                ;;
        esac
    done
    
    # 执行自动提交
    auto_commit "$commit_message" "$auto_push"
}

# 运行主函数
main "$@"
