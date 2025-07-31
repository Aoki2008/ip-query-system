#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "🚀 IP查询系统 - 启动所有服务"
echo "========================================"
echo -e "${NC}"

# 获取脚本所在目录的父目录作为项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📍 当前目录: $PWD${NC}"
echo

echo -e "${YELLOW}🔍 检查项目结构...${NC}"
if [ ! -d "backend-fastapi" ]; then
    echo -e "${RED}❌ 未找到backend-fastapi目录${NC}"
    exit 1
fi

if [ ! -d "frontend-admin" ]; then
    echo -e "${RED}❌ 未找到frontend-admin目录${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 项目结构检查通过${NC}"
echo

# 检查Python环境
echo -e "${YELLOW}🐍 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ 未找到Python，请先安装Python 3.8+${NC}"
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✅ Python环境检查通过${NC}"

# 检查Node.js环境
echo -e "${YELLOW}📦 检查Node.js环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未找到Node.js，请先安装Node.js 16+${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 未找到npm，请先安装npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js环境检查通过${NC}"
echo

# 启动后端服务
echo -e "${BLUE}🐍 启动后端服务...${NC}"
echo -e "${BLUE}📍 后端地址: http://localhost:8000${NC}"
echo -e "${BLUE}📖 API文档: http://localhost:8000/docs${NC}"
echo

cd "$PROJECT_ROOT/backend-fastapi"

# 检查并安装Python依赖
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📦 检查Python依赖...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt > /dev/null 2>&1
fi

# 在新终端中启动后端服务
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="IP查询系统-后端服务" -- bash -c "cd '$PROJECT_ROOT/backend-fastapi' && echo '🚀 启动FastAPI服务器...' && $PYTHON_CMD main.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -title "IP查询系统-后端服务" -e "cd '$PROJECT_ROOT/backend-fastapi' && echo '🚀 启动FastAPI服务器...' && $PYTHON_CMD main.py; exec bash" &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/backend-fastapi' && echo '🚀 启动FastAPI服务器...' && $PYTHON_CMD main.py\""
else
    echo -e "${YELLOW}⚠️ 无法检测到终端类型，请手动在新终端中运行:${NC}"
    echo -e "${YELLOW}cd '$PROJECT_ROOT/backend-fastapi' && $PYTHON_CMD main.py${NC}"
fi

echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
sleep 5

# 启动前端管理后台
echo
echo -e "${BLUE}🌐 启动前端管理后台...${NC}"
echo -e "${BLUE}📍 管理后台地址: http://localhost:5174${NC}"
echo

cd "$PROJECT_ROOT/frontend-admin"

# 检查并安装Node.js依赖
if [ -f "package.json" ]; then
    echo -e "${YELLOW}📦 检查Node.js依赖...${NC}"
    if [ ! -d "node_modules" ]; then
        npm install > /dev/null 2>&1
    fi
fi

# 在新终端中启动前端服务
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="IP查询系统-管理后台" -- bash -c "cd '$PROJECT_ROOT/frontend-admin' && echo '🚀 启动管理后台...' && npm run dev; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -title "IP查询系统-管理后台" -e "cd '$PROJECT_ROOT/frontend-admin' && echo '🚀 启动管理后台...' && npm run dev; exec bash" &
elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_ROOT/frontend-admin' && echo '🚀 启动管理后台...' && npm run dev\""
else
    echo -e "${YELLOW}⚠️ 无法检测到终端类型，请手动在新终端中运行:${NC}"
    echo -e "${YELLOW}cd '$PROJECT_ROOT/frontend-admin' && npm run dev${NC}"
fi

echo -e "${YELLOW}⏳ 等待前端服务启动...${NC}"
sleep 3

echo
echo -e "${GREEN}✅ 所有服务启动完成！${NC}"
echo
echo -e "${BLUE}📋 服务地址:${NC}"
echo -e "  - 后端API: http://localhost:8000"
echo -e "  - API文档: http://localhost:8000/docs"
echo -e "  - 管理后台: http://localhost:5174"
echo -e "  - 用户前端: http://localhost:5173 (需要单独启动)"
echo
echo -e "${BLUE}🔑 默认管理员账户:${NC}"
echo -e "  - 用户名: admin"
echo -e "  - 密码: admin123"
echo
echo -e "${YELLOW}💡 提示:${NC}"
echo -e "  - 如果遇到端口冲突，请检查端口是否被占用"
echo -e "  - 如果后端启动失败，请检查Python环境和依赖"
echo -e "  - 如果前端启动失败，请检查Node.js环境和依赖"
echo
echo -e "${BLUE}🛑 按Enter键退出...${NC}"
read
