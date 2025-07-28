"""
异步Flask应用
支持异步IP查询的高性能API服务
"""
import asyncio
import time
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import logging
import os
from api.async_ip_service import async_ip_service
from utils.error_handler import register_error_handlers, ErrorHandler
from utils.validators import request_validator
from utils.logger import app_logger, request_logger, performance_monitor

# 使用自定义日志配置
logger = app_logger

# 创建Flask应用
app = Flask(__name__)

# 配置CORS - 允许前端跨域访问
CORS(app, origins=[
    'http://localhost:3000', 'http://127.0.0.1:3000',    # 原前端
    'http://localhost:5173', 'http://127.0.0.1:5173',    # Vue3 Vite开发服务器
    'http://localhost:8080', 'http://127.0.0.1:8080'     # 其他可能的端口
])

# 初始化异步IP服务
logger.info("初始化异步IP查询服务...")

# 注册错误处理器
register_error_handlers(app)

# 请求监控中间件
@app.before_request
def before_request():
    """请求前处理"""
    g.start_time = time.time()
    
    # 记录请求信息
    request_logger.log_request(
        method=request.method,
        path=request.path,
        ip=request.remote_addr or 'unknown',
        user_agent=request.headers.get('User-Agent', '')
    )

@app.after_request
def after_request(response):
    """请求后处理"""
    if hasattr(g, 'start_time'):
        response_time = time.time() - g.start_time
        
        # 记录响应信息
        request_logger.log_response(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            response_time=response_time
        )
        
        # 记录性能数据
        performance_monitor.record_request(
            response_time=response_time,
            success=response.status_code < 400
        )
    
    return response

# 异步路由装饰器
def async_route(f):
    """异步路由装饰器"""
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/', methods=['GET'])
def root():
    """根路径重定向"""
    return jsonify({
        'message': '异步IP查询API服务',
        'version': '2.0',
        'service_type': 'async',
        'endpoints': {
            'health': '/api/health',
            'query_ip': '/api/query-ip?ip=<ip_address>',
            'query_batch': '/api/query-batch',
            'stats': '/api/stats',
            'cache_stats': '/api/cache/stats',
            'cache_clear': '/api/cache/clear'
        }
    })

@app.route('/api', methods=['GET'])
def api_info():
    """API信息接口"""
    return jsonify({
        'message': '异步IP查询API服务',
        'version': '2.0',
        'service_type': 'async',
        'status': 'running',
        'endpoints': [
            '/api/health',
            '/api/query-ip',
            '/api/query-batch',
            '/api/stats',
            '/api/cache/stats',
            '/api/cache/clear'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    logger.info('健康检查请求')
    return jsonify({
        'status': 'healthy',
        'message': 'IP查询API服务运行正常',
        'service_type': 'async'
    })

@app.route('/api/query-ip', methods=['GET'])
@async_route
async def query_single_ip():
    """异步单个IP查询接口"""
    try:
        ip = request.args.get('ip')
        logger.info(f'收到异步单个IP查询请求: {ip}')
        
        # 验证IP地址
        clean_ip = request_validator.validate_single_ip_request(ip)
        
        # 异步查询IP信息
        result = await async_ip_service.query_ip(clean_ip)
        logger.info(f'异步查询完成: {clean_ip}')
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        logger.warning(f'参数验证失败: {str(e)}')
        return ErrorHandler.handle_validation_error(str(e))
    except Exception as e:
        logger.error(f'异步查询失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("查询服务暂时不可用")

@app.route('/api/query-batch', methods=['POST'])
@async_route
async def query_batch_ips():
    """异步批量IP查询接口"""
    try:
        data = request.get_json()
        if not data:
            return ErrorHandler.handle_validation_error("请求体不能为空")
        
        logger.info(f'收到异步批量IP查询请求')
        
        # 验证IP地址列表
        valid_ips = request_validator.validate_batch_ip_request(data)
        
        logger.info(f'验证通过，共{len(valid_ips)}个有效IP，开始异步查询')
        
        # 异步批量查询
        batch_size = int(request.args.get('batch_size', 50))
        results = await async_ip_service.query_batch_ips(valid_ips, batch_size=batch_size)
        success_count = len([r for r in results if not r.get("error")])
        
        logger.info(f'异步批量查询完成，成功{success_count}个')
        
        return jsonify({
            'success': True,
            'data': {
                'total': len(valid_ips),
                'success_count': success_count,
                'results': results,
                'query_type': 'async'
            }
        })
        
    except ValueError as e:
        logger.warning(f'参数验证失败: {str(e)}')
        return ErrorHandler.handle_validation_error(str(e))
    except Exception as e:
        logger.error(f'异步批量查询失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("批量查询服务暂时不可用")

@app.route('/api/stats', methods=['GET'])
@async_route
async def get_stats():
    """获取性能统计信息"""
    try:
        # 获取基础统计
        base_stats = performance_monitor.get_stats()
        
        # 获取异步服务统计
        service_stats = await async_ip_service.get_service_stats()
        
        # 合并统计信息
        stats = {
            **base_stats,
            'service': service_stats,
            'timestamp': time.time()
        }
        
        logger.info('获取异步服务统计信息')
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f'获取统计信息失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("获取统计信息失败")

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """获取缓存统计信息"""
    try:
        from utils.cache_service import cache_service
        stats = cache_service.get_cache_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f'获取缓存统计失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("获取缓存统计失败")

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清空缓存"""
    try:
        from utils.cache_service import cache_service
        success = cache_service.clear_all()
        
        if success:
            logger.info('缓存已清空')
            return jsonify({
                'success': True,
                'message': '缓存已清空'
            })
        else:
            return ErrorHandler.handle_internal_error("清空缓存失败")
            
    except Exception as e:
        logger.error(f'清空缓存失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("清空缓存失败")

if __name__ == '__main__':
    # 从环境变量获取配置，默认值用于开发环境
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5001))  # 使用不同端口避免冲突
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    
    logger.info(f"启动异步Flask应用: {host}:{port}, debug={debug_mode}")
    app.run(host=host, port=port, debug=debug_mode)
