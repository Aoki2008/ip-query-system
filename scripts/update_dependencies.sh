#!/bin/bash
# 🔄 自动化依赖更新脚本
# 安全地更新Python和Node.js依赖

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups/dependencies"

echo -e "${BLUE}🔄 依赖更新工具${NC}"
echo "=================================="

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份当前依赖文件
backup_dependencies() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_path="$BACKUP_DIR/backup_$timestamp"
    mkdir -p "$backup_path"
    
    echo -e "${YELLOW}📦 备份当前依赖文件...${NC}"
    
    # 备份Python依赖
    if [[ -f "$PROJECT_ROOT/backend-fastapi/requirements.txt" ]]; then
        cp "$PROJECT_ROOT/backend-fastapi/requirements.txt" "$backup_path/"
        echo "✅ 已备份 requirements.txt"
    fi
    
    # 备份Node.js依赖
    for project in "frontend-vue3" "frontend-admin"; do
        if [[ -f "$PROJECT_ROOT/$project/package.json" ]]; then
            cp "$PROJECT_ROOT/$project/package.json" "$backup_path/"
            cp "$PROJECT_ROOT/$project/package-lock.json" "$backup_path/" 2>/dev/null || true
            echo "✅ 已备份 $project/package.json"
        fi
    done
    
    echo -e "${GREEN}📁 备份完成: $backup_path${NC}"
}

# 更新Python依赖
update_python_dependencies() {
    echo -e "${BLUE}🐍 更新Python依赖...${NC}"
    
    local backend_dir="$PROJECT_ROOT/backend-fastapi"
    if [[ ! -d "$backend_dir" ]]; then
        echo -e "${YELLOW}⚠️  后端目录不存在，跳过Python依赖更新${NC}"
        return
    fi
    
    cd "$backend_dir"
    
    # 检查是否有虚拟环境
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo "✅ 已激活虚拟环境"
    elif [[ -f "../venv/bin/activate" ]]; then
        source ../venv/bin/activate
        echo "✅ 已激活虚拟环境"
    else
        echo -e "${YELLOW}⚠️  未找到虚拟环境，使用系统Python${NC}"
    fi
    
    # 更新pip
    echo "📦 更新pip..."
    python -m pip install --upgrade pip
    
    # 安装安全扫描工具
    echo "🔧 安装安全扫描工具..."
    pip install pip-audit safety bandit
    
    # 运行安全扫描
    echo "🔍 运行安全扫描..."
    if command -v pip-audit &> /dev/null; then
        echo "运行 pip-audit..."
        pip-audit --desc || echo -e "${YELLOW}⚠️  发现安全漏洞，建议手动检查${NC}"
    fi
    
    # 尝试自动修复
    echo "🔧 尝试自动修复安全漏洞..."
    if command -v pip-audit &> /dev/null; then
        pip-audit --fix --dry-run || true
        
        read -p "是否应用自动修复? (y/N): " apply_fix
        if [[ "$apply_fix" =~ ^[Yy]$ ]]; then
            pip-audit --fix
            echo -e "${GREEN}✅ 自动修复已应用${NC}"
        fi
    fi
    
    # 更新requirements.txt
    if [[ -f "requirements.txt" ]]; then
        echo "📝 更新requirements.txt..."
        pip freeze > requirements_new.txt
        
        echo -e "${YELLOW}📋 依赖变更对比:${NC}"
        diff requirements.txt requirements_new.txt || true
        
        read -p "是否更新requirements.txt? (y/N): " update_req
        if [[ "$update_req" =~ ^[Yy]$ ]]; then
            mv requirements_new.txt requirements.txt
            echo -e "${GREEN}✅ requirements.txt已更新${NC}"
        else
            rm requirements_new.txt
        fi
    fi
    
    cd "$PROJECT_ROOT"
}

# 更新Node.js依赖
update_nodejs_dependencies() {
    echo -e "${BLUE}📦 更新Node.js依赖...${NC}"
    
    for project in "frontend-vue3" "frontend-admin"; do
        local project_dir="$PROJECT_ROOT/$project"
        
        if [[ ! -d "$project_dir" ]] || [[ ! -f "$project_dir/package.json" ]]; then
            echo -e "${YELLOW}⚠️  $project 目录不存在或无package.json，跳过${NC}"
            continue
        fi
        
        echo -e "${BLUE}📂 处理项目: $project${NC}"
        cd "$project_dir"
        
        # 运行npm audit
        echo "🔍 运行安全扫描..."
        npm audit || echo -e "${YELLOW}⚠️  发现安全漏洞${NC}"
        
        # 尝试自动修复
        echo "🔧 尝试自动修复..."
        npm audit fix --dry-run || true
        
        read -p "是否应用npm audit fix? (y/N): " apply_npm_fix
        if [[ "$apply_npm_fix" =~ ^[Yy]$ ]]; then
            npm audit fix
            echo -e "${GREEN}✅ npm audit fix已应用${NC}"
        fi
        
        # 检查过时的包
        echo "📊 检查过时的包..."
        npm outdated || true
        
        read -p "是否更新所有包到最新版本? (y/N): " update_all
        if [[ "$update_all" =~ ^[Yy]$ ]]; then
            npm update
            echo -e "${GREEN}✅ 所有包已更新${NC}"
        else
            # 选择性更新
            echo "可以手动更新特定包: npm install package@latest"
        fi
        
        # 清理未使用的包
        read -p "是否清理未使用的包? (y/N): " cleanup
        if [[ "$cleanup" =~ ^[Yy]$ ]]; then
            npm prune
            echo -e "${GREEN}✅ 未使用的包已清理${NC}"
        fi
    done
    
    cd "$PROJECT_ROOT"
}

# 验证更新后的依赖
verify_dependencies() {
    echo -e "${BLUE}🧪 验证更新后的依赖...${NC}"
    
    # 验证Python依赖
    echo "🐍 验证Python依赖..."
    cd "$PROJECT_ROOT/backend-fastapi"
    if [[ -f "requirements.txt" ]]; then
        pip check || echo -e "${YELLOW}⚠️  Python依赖存在冲突${NC}"
    fi
    
    # 验证Node.js依赖
    echo "📦 验证Node.js依赖..."
    for project in "frontend-vue3" "frontend-admin"; do
        if [[ -d "$PROJECT_ROOT/$project" ]]; then
            cd "$PROJECT_ROOT/$project"
            npm ls --depth=0 || echo -e "${YELLOW}⚠️  $project 依赖存在问题${NC}"
        fi
    done
    
    cd "$PROJECT_ROOT"
}

# 运行测试
run_tests() {
    echo -e "${BLUE}🧪 运行测试验证更新...${NC}"
    
    read -p "是否运行测试验证更新? (y/N): " run_test
    if [[ "$run_test" =~ ^[Yy]$ ]]; then
        # 运行后端测试
        if [[ -f "$PROJECT_ROOT/backend-fastapi/test_main.py" ]]; then
            echo "🐍 运行后端测试..."
            cd "$PROJECT_ROOT/backend-fastapi"
            python -m pytest test_main.py -v || echo -e "${YELLOW}⚠️  后端测试失败${NC}"
        fi
        
        # 运行前端构建测试
        for project in "frontend-vue3" "frontend-admin"; do
            if [[ -d "$PROJECT_ROOT/$project" ]]; then
                echo "📦 测试 $project 构建..."
                cd "$PROJECT_ROOT/$project"
                npm run build || echo -e "${YELLOW}⚠️  $project 构建失败${NC}"
            fi
        done
    fi
    
    cd "$PROJECT_ROOT"
}

# 生成更新报告
generate_report() {
    echo -e "${BLUE}📄 生成更新报告...${NC}"
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local report_file="$BACKUP_DIR/update_report_$timestamp.md"
    
    cat > "$report_file" << EOF
# 依赖更新报告

**更新时间**: $(date)
**操作人员**: $(whoami)

## 更新内容

### Python依赖更新
- 项目: backend-fastapi
- 工具: pip-audit, safety
- 状态: 已完成

### Node.js依赖更新
- 项目: frontend-vue3, frontend-admin  
- 工具: npm audit, npm update
- 状态: 已完成

## 安全扫描结果

$(python "$PROJECT_ROOT/scripts/dependency_security_scan.py" 2>/dev/null || echo "扫描工具未就绪")

## 备份信息

备份位置: $BACKUP_DIR/backup_$timestamp

## 建议

1. 定期运行依赖更新 (建议每月一次)
2. 关注安全公告和CVE通知
3. 在生产环境部署前进行充分测试
4. 保持依赖版本的文档记录

EOF

    echo -e "${GREEN}📄 更新报告已生成: $report_file${NC}"
}

# 主函数
main() {
    echo -e "${YELLOW}⚠️  注意: 此操作将更新项目依赖，建议在测试环境先行验证${NC}"
    read -p "是否继续? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
    
    # 执行更新流程
    backup_dependencies
    update_python_dependencies
    update_nodejs_dependencies
    verify_dependencies
    run_tests
    generate_report
    
    echo -e "${GREEN}🎉 依赖更新完成！${NC}"
    echo -e "${YELLOW}📝 请检查更新报告并在生产环境部署前进行测试${NC}"
}

# 解析命令行参数
case "${1:-}" in
    --python-only)
        backup_dependencies
        update_python_dependencies
        verify_dependencies
        ;;
    --nodejs-only)
        backup_dependencies
        update_nodejs_dependencies
        verify_dependencies
        ;;
    --help|-h)
        echo "用法: $0 [选项]"
        echo "选项:"
        echo "  --python-only    仅更新Python依赖"
        echo "  --nodejs-only    仅更新Node.js依赖"
        echo "  --help, -h       显示帮助信息"
        ;;
    *)
        main
        ;;
esac
