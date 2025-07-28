#!/bin/bash

echo "========================================"
echo "IP查询工具 - 前端服务启动脚本"
echo "========================================"

# 切换到前端目录
cd "$(dirname "$0")/IP查询工具"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "启动前端服务..."
echo "服务地址: http://localhost:3000"
echo "浏览器将自动打开，按 Ctrl+C 停止服务"
echo "========================================"

python3 start.py
