#!/usr/bin/env python3
"""
IP查询工具前端服务启动脚本
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import logging
from threading import Timer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

PORT = 3000

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # 自定义日志格式
        logger.info(f"{self.address_string()} - {format % args}")

def open_browser():
    """延迟打开浏览器"""
    webbrowser.open(f'http://localhost:{PORT}')

def main():
    """主函数"""
    # 切换到前端目录
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    logger.info("正在启动IP查询工具前端服务...")
    logger.info(f"服务目录: {frontend_dir}")
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            logger.info(f"前端服务启动成功!")
            logger.info(f"访问地址: http://localhost:{PORT}")
            logger.info("按 Ctrl+C 停止服务")
            
            # 2秒后自动打开浏览器
            Timer(2.0, open_browser).start()
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"端口 {PORT} 已被占用，请关闭其他服务或更改端口")
        else:
            logger.error(f"启动服务失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("前端服务已停止")

if __name__ == '__main__':
    main()
