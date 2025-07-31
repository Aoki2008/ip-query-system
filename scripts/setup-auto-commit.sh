#!/bin/bash

# 🔧 设置自动提交Git钩子
# 用法: ./scripts/setup-auto-commit.sh

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

# 检查是否在Git仓库中
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
}

# 创建pre-commit钩子
create_pre_commit_hook() {
    local hooks_dir=".git/hooks"
    local pre_commit_file="$hooks_dir/pre-commit"
    
    log_info "创建pre-commit钩子..."
    
    cat > "$pre_commit_file" << 'EOF'
#!/bin/bash

# 🔍 Pre-commit钩子 - 代码质量检查

set -e

echo "🔍 运行pre-commit检查..."

# 检查Python代码格式
if git diff --cached --name-only | grep -q "\.py$"; then
    echo "📝 检查Python代码格式..."
    
    # 检查是否安装了black
    if command -v black &> /dev/null; then
        black --check --diff $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$") || {
            echo "❌ Python代码格式不符合规范，请运行: black ."
            exit 1
        }
    fi
    
    # 检查是否安装了flake8
    if command -v flake8 &> /dev/null; then
        flake8 $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$") || {
            echo "❌ Python代码质量检查失败"
            exit 1
        }
    fi
fi

# 检查JavaScript/TypeScript代码格式
if git diff --cached --name-only | grep -q "\.(js|ts|vue)$"; then
    echo "📝 检查JavaScript/TypeScript代码格式..."
    
    # 检查是否有package.json
    if [ -f "package.json" ]; then
        # 运行ESLint检查
        if npm list eslint &> /dev/null; then
            npm run lint:check 2>/dev/null || {
                echo "❌ JavaScript/TypeScript代码格式检查失败"
                exit 1
            }
        fi
    fi
fi

# 检查提交信息格式
check_commit_message() {
    local commit_msg_file="$1"
    local commit_msg=$(cat "$commit_msg_file")
    
    # 检查提交信息是否符合规范
    if [[ ! "$commit_msg" =~ ^(feat|fix|docs|style|refactor|test|chore|perf)(\(.+\))?: .+ ]]; then
        echo "⚠️  提交信息建议使用规范格式: type(scope): description"
        echo "   例如: feat(auth): 添加用户登录功能"
    fi
}

echo "✅ Pre-commit检查通过"
EOF

    chmod +x "$pre_commit_file"
    log_success "Pre-commit钩子创建完成"
}

# 创建post-commit钩子
create_post_commit_hook() {
    local hooks_dir=".git/hooks"
    local post_commit_file="$hooks_dir/post-commit"
    
    log_info "创建post-commit钩子..."
    
    cat > "$post_commit_file" << 'EOF'
#!/bin/bash

# 📤 Post-commit钩子 - 自动推送

# 获取当前分支
current_branch=$(git rev-parse --abbrev-ref HEAD)

# 检查是否是主分支
if [ "$current_branch" = "main" ] || [ "$current_branch" = "master" ]; then
    echo "📤 检测到主分支提交，询问是否自动推送..."
    
    # 检查是否设置了自动推送环境变量
    if [ "$AUTO_PUSH" = "true" ]; then
        echo "🚀 自动推送到远程仓库..."
        git push origin "$current_branch"
        echo "✅ 推送完成"
    else
        # 在非交互环境中跳过询问
        if [ -t 1 ]; then
            read -p "是否推送到远程仓库? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "🚀 推送到远程仓库..."
                git push origin "$current_branch"
                echo "✅ 推送完成"
            fi
        fi
    fi
fi
EOF

    chmod +x "$post_commit_file"
    log_success "Post-commit钩子创建完成"
}

# 创建commit-msg钩子
create_commit_msg_hook() {
    local hooks_dir=".git/hooks"
    local commit_msg_file="$hooks_dir/commit-msg"
    
    log_info "创建commit-msg钩子..."
    
    cat > "$commit_msg_file" << 'EOF'
#!/bin/bash

# 📝 Commit-msg钩子 - 提交信息检查

commit_msg_file="$1"
commit_msg=$(cat "$commit_msg_file")

# 检查提交信息长度
if [ ${#commit_msg} -lt 10 ]; then
    echo "❌ 提交信息太短，至少需要10个字符"
    exit 1
fi

if [ ${#commit_msg} -gt 100 ]; then
    echo "❌ 提交信息太长，建议不超过100个字符"
    exit 1
fi

# 检查是否包含敏感信息
if echo "$commit_msg" | grep -qi "password\|secret\|key\|token"; then
    echo "⚠️  警告: 提交信息中可能包含敏感信息"
    echo "请确认提交信息不包含密码、密钥等敏感数据"
fi

echo "✅ 提交信息检查通过"
EOF

    chmod +x "$commit_msg_file"
    log_success "Commit-msg钩子创建完成"
}

# 设置Git配置
setup_git_config() {
    log_info "设置Git配置..."
    
    # 设置自动推送配置
    git config --local push.default simple
    git config --local push.followTags true
    
    # 设置提交模板
    if [ ! -f ".gitmessage" ]; then
        cat > ".gitmessage" << 'EOF'
# 提交类型(必需): 简短描述(必需)
#
# 提交类型:
# feat:     新功能
# fix:      修复bug
# docs:     文档更新
# style:    代码格式调整
# refactor: 代码重构
# test:     测试相关
# chore:    构建过程或辅助工具的变动
# perf:     性能优化
#
# 示例:
# feat(auth): 添加用户登录功能
# fix(api): 修复IP查询接口错误
# docs: 更新README文档
#
# 详细描述(可选):
#
# 相关Issue(可选):
# Closes #123
EOF
        git config --local commit.template .gitmessage
        log_success "Git提交模板创建完成"
    fi
    
    log_success "Git配置完成"
}

# 显示使用说明
show_usage() {
    echo ""
    log_success "🎉 自动提交设置完成!"
    echo ""
    echo "📋 可用的自动提交方式:"
    echo ""
    echo "1. 🔧 使用脚本:"
    echo "   ./scripts/auto-commit.sh [提交信息]"
    echo "   ./scripts/auto-commit.bat [提交信息]  (Windows)"
    echo "   ./scripts/auto-commit.ps1 [提交信息] (PowerShell)"
    echo ""
    echo "2. 🪝 Git钩子 (已设置):"
    echo "   - pre-commit: 代码质量检查"
    echo "   - post-commit: 询问是否自动推送"
    echo "   - commit-msg: 提交信息检查"
    echo ""
    echo "3. ⚙️ 环境变量:"
    echo "   export AUTO_PUSH=true  # 启用自动推送"
    echo ""
    echo "4. 📝 提交信息模板:"
    echo "   git commit  # 使用模板"
    echo ""
}

# 主函数
main() {
    echo "🔧 设置自动提交Git钩子"
    echo "========================"
    
    check_git_repo
    
    create_pre_commit_hook
    create_post_commit_hook
    create_commit_msg_hook
    setup_git_config
    
    show_usage
}

# 运行主函数
main "$@"
