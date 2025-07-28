#!/usr/bin/env python3
"""
异步Flask应用启动脚本
"""
from async_app import app

if __name__ == '__main__':
    print("启动异步Flask应用...")
    print("访问地址: http://localhost:5001/api/health")
    app.run(host='0.0.0.0', port=5001, debug=True)
