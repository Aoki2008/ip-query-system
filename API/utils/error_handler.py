"""
统一错误处理模块
"""
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API自定义异常类"""
    def __init__(self, message, status_code=400, error_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def handle_validation_error(message="参数验证失败"):
        """处理参数验证错误"""
        return jsonify({
            'error': True,
            'message': message,
            'error_code': 'VALIDATION_ERROR'
        }), 400
    
    @staticmethod
    def handle_not_found_error(message="资源未找到"):
        """处理资源未找到错误"""
        return jsonify({
            'error': True,
            'message': message,
            'error_code': 'NOT_FOUND'
        }), 404
    
    @staticmethod
    def handle_internal_error(message="服务器内部错误"):
        """处理服务器内部错误"""
        return jsonify({
            'error': True,
            'message': message,
            'error_code': 'INTERNAL_ERROR'
        }), 500
    
    @staticmethod
    def handle_rate_limit_error(message="请求过于频繁"):
        """处理限流错误"""
        return jsonify({
            'error': True,
            'message': message,
            'error_code': 'RATE_LIMIT'
        }), 429
    
    @staticmethod
    def handle_api_error(error):
        """处理自定义API错误"""
        return jsonify({
            'error': True,
            'message': error.message,
            'error_code': error.error_code or 'API_ERROR'
        }), error.status_code
    
    @staticmethod
    def handle_unknown_error(exception):
        """处理未知错误"""
        logger.error(f"未知错误: {str(exception)}", exc_info=True)
        return jsonify({
            'error': True,
            'message': "服务暂时不可用，请稍后重试",
            'error_code': 'UNKNOWN_ERROR'
        }), 500

def register_error_handlers(app):
    """注册错误处理器到Flask应用"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        return ErrorHandler.handle_api_error(error)
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        return ErrorHandler.handle_validation_error()
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return ErrorHandler.handle_not_found_error("接口不存在")
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return ErrorHandler.handle_internal_error()
    
    @app.errorhandler(Exception)
    def handle_unknown_error(error):
        return ErrorHandler.handle_unknown_error(error)
