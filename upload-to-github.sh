#!/bin/bash

# IP查询系统 - GitHub上传脚本
# 用于将项目代码上传到GitHub仓库

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
    echo ""
    echo "=========================================="
    echo "IP查询系统 - GitHub上传脚本"
    echo "=========================================="
    echo ""
    echo "此脚本将帮助您："
    echo "1. 初始化Git仓库"
    echo "2. 配置GitHub远程仓库"
    echo "3. 提交并推送代码"
    echo ""
}

# 检查依赖
check_dependencies() {
    log_step "检查依赖..."
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        log_error "Git未安装，请先安装Git"
        echo "安装方法："
        echo "  Ubuntu/Debian: sudo apt-get install git"
        echo "  CentOS/RHEL: sudo yum install git"
        echo "  macOS: brew install git"
        echo "  Windows: https://git-scm.com/download/win"
        exit 1
    fi
    
    log_info "Git已安装: $(git --version)"
}

# 获取用户输入
get_user_input() {
    log_step "获取GitHub仓库信息..."
    
    # GitHub用户名
    read -p "请输入您的GitHub用户名: " GITHUB_USERNAME
    if [[ -z "$GITHUB_USERNAME" ]]; then
        log_error "GitHub用户名不能为空"
        exit 1
    fi
    
    # 仓库名称
    read -p "请输入仓库名称 [ip-query-system]: " REPO_NAME
    REPO_NAME=${REPO_NAME:-ip-query-system}
    
    # 确认信息
    echo ""
    echo "确认信息："
    echo "  GitHub用户名: $GITHUB_USERNAME"
    echo "  仓库名称: $REPO_NAME"
    echo "  仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    
    read -p "信息是否正确？(y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        log_info "已取消操作"
        exit 0
    fi
}

# 初始化Git仓库
init_git_repo() {
    log_step "初始化Git仓库..."
    
    # 检查是否已经是Git仓库
    if [[ -d ".git" ]]; then
        log_warn "当前目录已经是Git仓库"
        read -p "是否重新初始化？(y/N): " REINIT
        if [[ "$REINIT" =~ ^[Yy]$ ]]; then
            rm -rf .git
            git init
            log_info "Git仓库重新初始化完成"
        else
            log_info "使用现有Git仓库"
        fi
    else
        git init
        log_info "Git仓库初始化完成"
    fi
    
    # 设置默认分支为main
    git branch -M main
    
    # 配置Git用户信息（如果未配置）
    if [[ -z "$(git config user.name)" ]]; then
        read -p "请输入您的Git用户名: " GIT_USERNAME
        git config user.name "$GIT_USERNAME"
    fi
    
    if [[ -z "$(git config user.email)" ]]; then
        read -p "请输入您的Git邮箱: " GIT_EMAIL
        git config user.email "$GIT_EMAIL"
    fi
    
    log_info "Git配置完成"
}

# 添加远程仓库
add_remote_repo() {
    log_step "配置远程仓库..."
    
    # 检查是否已有origin远程仓库
    if git remote | grep -q "origin"; then
        log_warn "已存在origin远程仓库"
        current_origin=$(git remote get-url origin)
        echo "当前origin: $current_origin"
        
        read -p "是否更新origin地址？(y/N): " UPDATE_ORIGIN
        if [[ "$UPDATE_ORIGIN" =~ ^[Yy]$ ]]; then
            git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
            log_info "远程仓库地址已更新"
        fi
    else
        git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        log_info "远程仓库已添加"
    fi
    
    echo "远程仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
}

# 提交代码
commit_code() {
    log_step "提交代码..."
    
    # 检查是否有文件需要提交
    if [[ -z "$(git status --porcelain)" ]]; then
        log_warn "没有文件需要提交"
        return
    fi
    
    # 添加所有文件
    log_info "添加文件到暂存区..."
    git add .
    
    # 显示将要提交的文件
    echo ""
    echo "将要提交的文件："
    git status --short
    echo ""
    
    read -p "确认提交这些文件？(y/N): " CONFIRM_COMMIT
    if [[ ! "$CONFIRM_COMMIT" =~ ^[Yy]$ ]]; then
        log_info "已取消提交"
        exit 0
    fi
    
    # 提交代码
    COMMIT_MESSAGE="feat: initial commit - complete IP query system

- Add Node.js API service with Express framework
- Add Laravel admin panel with dashboard  
- Add Next.js frontend application
- Add complete database schema and migrations
- Add Docker containerization support
- Add comprehensive documentation
- Add deployment scripts and configurations"

    git commit -m "$COMMIT_MESSAGE"
    log_info "代码提交完成"
}

# 推送到GitHub
push_to_github() {
    log_step "推送代码到GitHub..."
    
    log_warn "请确保您已在GitHub上创建了仓库: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    log_warn "如果仓库不存在，请先在GitHub上创建仓库"
    echo ""
    
    read -p "仓库已创建，继续推送？(y/N): " CONFIRM_PUSH
    if [[ ! "$CONFIRM_PUSH" =~ ^[Yy]$ ]]; then
        log_info "已取消推送"
        echo ""
        echo "您可以稍后手动推送："
        echo "  git push -u origin main"
        exit 0
    fi
    
    # 推送代码
    log_info "正在推送代码..."
    if git push -u origin main; then
        log_info "代码推送成功！"
    else
        log_error "代码推送失败"
        echo ""
        echo "可能的原因："
        echo "1. 仓库不存在 - 请在GitHub上创建仓库"
        echo "2. 权限不足 - 请检查GitHub访问权限"
        echo "3. 网络问题 - 请检查网络连接"
        echo ""
        echo "您可以稍后手动推送："
        echo "  git push -u origin main"
        exit 1
    fi
}

# 显示完成信息
show_completion() {
    log_step "上传完成！"
    
    echo ""
    echo "=========================================="
    echo "代码已成功上传到GitHub"
    echo "=========================================="
    echo ""
    echo "仓库信息："
    echo "  GitHub地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "  克隆地址: git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo ""
    echo "下一步操作："
    echo "  1. 访问GitHub仓库页面查看代码"
    echo "  2. 编辑仓库描述和README"
    echo "  3. 设置仓库可见性（公开/私有）"
    echo "  4. 配置GitHub Pages（如果需要）"
    echo "  5. 邀请协作者（如果需要）"
    echo ""
    echo "部署说明："
    echo "  - 查看 docs/deployment.md 了解部署步骤"
    echo "  - 使用 deploy/install.sh 进行一键部署"
    echo "  - 配置环境变量和域名"
    echo ""
    echo "=========================================="
}

# 显示GitHub仓库创建指南
show_github_guide() {
    echo ""
    echo "=========================================="
    echo "GitHub仓库创建指南"
    echo "=========================================="
    echo ""
    echo "如果您还没有创建GitHub仓库，请按以下步骤操作："
    echo ""
    echo "1. 访问 https://github.com/new"
    echo "2. 填写仓库信息："
    echo "   - Repository name: $REPO_NAME"
    echo "   - Description: 企业级IP查询系统"
    echo "   - 选择 Public 或 Private"
    echo "   - 不要勾选 'Initialize this repository with a README'"
    echo "   - 不要添加 .gitignore 和 license（我们已经有了）"
    echo "3. 点击 'Create repository'"
    echo "4. 创建完成后返回此脚本继续操作"
    echo ""
    echo "=========================================="
    echo ""
}

# 主函数
main() {
    show_welcome
    check_dependencies
    get_user_input
    show_github_guide
    
    read -p "按Enter键继续..."
    
    init_git_repo
    add_remote_repo
    commit_code
    push_to_github
    show_completion
}

# 错误处理
trap 'log_error "脚本执行失败，退出码: $?"' ERR

# 执行主函数
main "$@"
