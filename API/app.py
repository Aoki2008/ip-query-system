from flask import Flask, request, jsonify, g
from flask_cors import CORS
import logging
import os
import time
from api.ip_service import IPService
from utils.error_handler import register_error_handlers, APIError, ErrorHandler
from utils.validators import request_validator
from utils.logger import app_logger, request_logger, performance_monitor
from utils.monitoring import metrics_collector, alert_manager, health_checker

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

# 初始化IP服务
ip_service = IPService()

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

        # 记录监控指标
        metrics_collector.record_metric('request_count', 1)
        metrics_collector.record_metric('response_time', response_time)

        if response.status_code >= 400:
            metrics_collector.record_metric('error_count', 1)

        # 计算错误率
        error_stats = metrics_collector.get_metric_stats('error_count', 300)  # 5分钟窗口
        request_stats = metrics_collector.get_metric_stats('request_count', 300)

        if request_stats.get('count', 0) > 0:
            error_rate = (error_stats.get('count', 0) / request_stats.get('count', 1)) * 100
            metrics_collector.record_metric('error_rate', error_rate)

    return response

@app.route('/', methods=['GET'])
def root():
    """根路径重定向"""
    return jsonify({
        'message': 'IP查询API服务',
        'version': '2.0',
        'endpoints': {
            'health': '/api/health',
            'query_ip': '/api/query-ip?ip=<ip_address>',
            'query_batch': '/api/query-batch',
            'stats': '/api/stats',
            'monitoring': {
                'metrics': '/api/monitoring/metrics',
                'alerts': '/api/monitoring/alerts',
                'health': '/api/monitoring/health'
            }
        },
        'documentation': 'https://github.com/your-repo/ip-query-tool'
    })

@app.route('/api', methods=['GET'])
def api_info():
    """API信息接口"""
    return jsonify({
        'message': 'IP查询API服务',
        'version': '2.0',
        'status': 'running',
        'endpoints': [
            '/api/health',
            '/api/query-ip',
            '/api/query-batch',
            '/api/stats',
            '/api/monitoring/metrics',
            '/api/monitoring/alerts',
            '/api/monitoring/health'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': 'IP查询API服务运行正常'
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取性能统计信息"""
    try:
        stats = performance_monitor.get_stats()
        logger.info('获取性能统计信息')
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f'获取统计信息失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("获取统计信息失败")

@app.route('/api/monitoring/metrics', methods=['GET'])
def get_monitoring_metrics():
    """获取监控指标"""
    try:
        # 简化版本，先返回基础信息
        return jsonify({
            'success': True,
            'data': {
                'metrics': {'test': 'working'},
                'timestamp': time.time()
            }
        })
    except Exception as e:
        logger.error(f'获取监控指标失败: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitoring/alerts', methods=['GET'])
def get_alerts():
    """获取告警信息"""
    try:
        active_alerts = alert_manager.get_active_alerts()
        alert_history = alert_manager.get_alert_history(50)

        return jsonify({
            'success': True,
            'data': {
                'active_alerts': active_alerts,
                'alert_history': alert_history,
                'total_active': len(active_alerts)
            }
        })
    except Exception as e:
        logger.error(f'获取告警信息失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("获取告警信息失败")

@app.route('/api/monitoring/health', methods=['GET'])
def get_health_status():
    """获取健康状态"""
    try:
        # 注册基础健康检查
        def check_database():
            """检查数据库文件"""
            db_path = os.path.join(os.path.dirname(__file__), 'GeoLite2-City.mmdb')
            return os.path.exists(db_path)

        def check_cache():
            """检查缓存服务"""
            from utils.cache_service import cache_service
            try:
                # 测试缓存读写
                test_key = 'health_check_test'
                cache_service.cache.set(test_key, 'test_value', ttl=10)
                result = cache_service.cache.get(test_key)
                cache_service.cache.delete(test_key)
                return result == 'test_value'
            except:
                return False

        # 注册检查
        health_checker.register_check('database', check_database)
        health_checker.register_check('cache', check_cache)

        # 运行检查
        health_results = health_checker.run_checks()

        return jsonify({
            'success': True,
            'data': health_results
        })
    except Exception as e:
        logger.error(f'健康检查失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("健康检查失败")

@app.route('/api/query-ip', methods=['GET'])
def query_single_ip():
    """单个IP查询接口"""
    try:
        ip = request.args.get('ip')
        logger.info(f'收到单个IP查询请求: {ip}')

        # 验证IP地址
        clean_ip = request_validator.validate_single_ip_request(ip)

        # 查询IP信息
        result = ip_service.query_ip(clean_ip)
        logger.info(f'查询成功: {clean_ip}')

        return jsonify({
            'success': True,
            'data': result
        })

    except ValueError as e:
        logger.warning(f'参数验证失败: {str(e)}')
        return ErrorHandler.handle_validation_error(str(e))
    except Exception as e:
        logger.error(f'查询失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("查询服务暂时不可用")

@app.route('/api/query-batch', methods=['POST'])
def query_batch_ips():
    """批量IP查询接口"""
    try:
        data = request.get_json()
        if not data:
            return ErrorHandler.handle_validation_error("请求体不能为空")

        logger.info(f'收到批量IP查询请求')

        # 验证IP地址列表
        valid_ips = request_validator.validate_batch_ip_request(data)

        logger.info(f'验证通过，共{len(valid_ips)}个有效IP')

        # 批量查询
        results = ip_service.query_batch_ips(valid_ips)
        success_count = len([r for r in results if not r.get("error")])

        logger.info(f'批量查询完成，成功{success_count}个')

        return jsonify({
            'success': True,
            'data': {
                'total': len(valid_ips),
                'success_count': success_count,
                'results': results
            }
        })

    except ValueError as e:
        logger.warning(f'参数验证失败: {str(e)}')
        return ErrorHandler.handle_validation_error(str(e))
    except Exception as e:
        logger.error(f'批量查询失败: {str(e)}', exc_info=True)
        return ErrorHandler.handle_internal_error("批量查询服务暂时不可用")

# 错误处理器已在register_error_handlers中注册

if __name__ == '__main__':
    # 从环境变量获取配置，默认值用于开发环境
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')

    app.run(host=host, port=port, debug=debug_mode)
