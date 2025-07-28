const logger = require('../utils/logger');

// 错误处理中间件
const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;

  // 记录错误日志
  logger.error('Error Handler:', {
    error: error.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    userId: req.user?.id,
    apiKeyId: req.apiKey?.id
  });

  // Mongoose错误处理
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = { message, statusCode: 404 };
  }

  // Mongoose重复字段错误
  if (err.code === 11000) {
    const message = 'Duplicate field value entered';
    error = { message, statusCode: 400 };
  }

  // Mongoose验证错误
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = { message, statusCode: 400 };
  }

  // JWT错误
  if (err.name === 'JsonWebTokenError') {
    const message = 'Invalid token';
    error = { message, statusCode: 401 };
  }

  if (err.name === 'TokenExpiredError') {
    const message = 'Token expired';
    error = { message, statusCode: 401 };
  }

  // MySQL错误
  if (err.code === 'ER_DUP_ENTRY') {
    const message = 'Duplicate entry';
    error = { message, statusCode: 400 };
  }

  if (err.code === 'ER_NO_SUCH_TABLE') {
    const message = 'Database table not found';
    error = { message, statusCode: 500 };
  }

  // Redis错误
  if (err.code === 'ECONNREFUSED' && err.port === 6379) {
    const message = 'Cache service unavailable';
    error = { message, statusCode: 503 };
  }

  // 文件系统错误
  if (err.code === 'ENOENT') {
    const message = 'File not found';
    error = { message, statusCode: 404 };
  }

  if (err.code === 'EACCES') {
    const message = 'Permission denied';
    error = { message, statusCode: 403 };
  }

  // 网络错误
  if (err.code === 'ENOTFOUND') {
    const message = 'Network error - host not found';
    error = { message, statusCode: 503 };
  }

  if (err.code === 'ETIMEDOUT') {
    const message = 'Request timeout';
    error = { message, statusCode: 408 };
  }

  // 限流错误
  if (err.type === 'entity.too.large') {
    const message = 'Request entity too large';
    error = { message, statusCode: 413 };
  }

  // 语法错误
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    const message = 'Invalid JSON';
    error = { message, statusCode: 400 };
  }

  // 默认错误响应
  const statusCode = error.statusCode || 500;
  const message = error.message || 'Internal Server Error';

  // 生产环境不暴露详细错误信息
  const response = {
    success: false,
    error: message,
    code: getErrorCode(err),
    ...(process.env.NODE_ENV === 'development' && {
      stack: err.stack,
      details: error
    })
  };

  res.status(statusCode).json(response);
};

// 获取错误代码
const getErrorCode = (err) => {
  // JWT错误
  if (err.name === 'JsonWebTokenError') return 'INVALID_TOKEN';
  if (err.name === 'TokenExpiredError') return 'TOKEN_EXPIRED';
  
  // 验证错误
  if (err.name === 'ValidationError') return 'VALIDATION_ERROR';
  
  // 数据库错误
  if (err.code === 'ER_DUP_ENTRY') return 'DUPLICATE_ENTRY';
  if (err.code === 'ER_NO_SUCH_TABLE') return 'TABLE_NOT_FOUND';
  
  // 网络错误
  if (err.code === 'ENOTFOUND') return 'HOST_NOT_FOUND';
  if (err.code === 'ETIMEDOUT') return 'REQUEST_TIMEOUT';
  if (err.code === 'ECONNREFUSED') return 'CONNECTION_REFUSED';
  
  // 文件系统错误
  if (err.code === 'ENOENT') return 'FILE_NOT_FOUND';
  if (err.code === 'EACCES') return 'PERMISSION_DENIED';
  
  // HTTP错误
  if (err.type === 'entity.too.large') return 'PAYLOAD_TOO_LARGE';
  
  // 默认错误代码
  return 'INTERNAL_ERROR';
};

// 404处理中间件
const notFound = (req, res, next) => {
  const error = new Error(`Not found - ${req.originalUrl}`);
  error.statusCode = 404;
  next(error);
};

// 异步错误包装器
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

module.exports = {
  errorHandler,
  notFound,
  asyncHandler
};
