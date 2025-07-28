#!/usr/bin/env python3
"""
IP查询工具后端服务启动脚本
"""

import os
import sys
import logging

# 导入app并检查路由
try:
    from app import app

    # 检查路由注册情况
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")

    print(f"Flask应用已加载，共{len(routes)}个路由:")
    for route in routes:
        print(f"  {route}")

    # 检查监控路由
    monitoring_routes = [r for r in routes if 'monitoring' in r]
    print(f"\n监控路由数量: {len(monitoring_routes)}")

except Exception as e:
    print(f"导入app失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        import geoip2
        logger.info("所有依赖已正确安装")
        return True
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.error("请运行: pip install -r requirements.txt")
        return False

def check_database():
    """检查数据库文件是否存在"""
    db_path = os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb')
    if not os.path.exists(db_path):
        logger.error(f"数据库文件不存在: {db_path}")
        logger.error("请从MaxMind官网下载GeoLite2-City.mmdb文件")
        return False
    
    logger.info(f"数据库文件已找到: {db_path}")
    return True

def main():
    """主函数"""
    logger.info("正在启动IP查询工具后端服务...")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查数据库
    if not check_database():
        sys.exit(1)
    
    # 启动服务
    logger.info("后端服务启动成功!")
    logger.info("API地址: http://localhost:5000/api")
    logger.info("健康检查: http://localhost:5000/api/health")
    logger.info("按 Ctrl+C 停止服务")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("服务已停止")

if __name__ == '__main__':
    main()
