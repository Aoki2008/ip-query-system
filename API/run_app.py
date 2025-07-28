#!/usr/bin/env python3
"""
简单的Flask应用启动脚本
"""
from app import app

if __name__ == '__main__':
    print("启动Flask应用...")
    print("访问地址: http://localhost:5000/api/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
