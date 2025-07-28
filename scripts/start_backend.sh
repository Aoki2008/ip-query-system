#!/bin/bash

echo "========================================"
echo "IP查询工具 - 后端服务启动脚本"
echo "========================================"

# 切换到后端目录
cd "$(dirname "$0")/API"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "检查依赖包..."
if ! python3 -c "import flask, flask_cors, geoip2" &> /dev/null; then
    echo "正在安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖包安装失败"
        exit 1
    fi
fi

# 检查数据库文件
if [ ! -f "GeoLite2-City.mmdb" ]; then
    echo "错误: 未找到GeoLite2-City.mmdb数据库文件"
    echo "请从MaxMind官网下载该文件并放置在API目录下"
    exit 1
fi

echo "启动后端服务..."
echo "服务地址: http://localhost:5000/api"
echo "按 Ctrl+C 停止服务"
echo "========================================"

python3 start.py
