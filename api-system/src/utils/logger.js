const winston = require('winston');
const path = require('path');

// 创建logs目录
const logsDir = path.join(__dirname, '../../logs');

// 自定义日志格式
const logFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss'
  }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.prettyPrint()
);

// 控制台输出格式
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss'
  }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let msg = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(meta).length > 0) {
      msg += '\n' + JSON.stringify(meta, null, 2);
    }
    return msg;
  })
);

// 创建logger实例
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: { service: 'ip-query-api' },
  transports: [
    // 错误日志文件
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      format: logFormat
    }),
    
    // 组合日志文件
    new winston.transports.File({
      filename: path.join(logsDir, 'combined.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      format: logFormat
    }),
    
    // API访问日志
    new winston.transports.File({
      filename: path.join(logsDir, 'access.log'),
      level: 'info',
      maxsize: 10485760, // 10MB
      maxFiles: 10,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      )
    })
  ],
  
  // 异常处理
  exceptionHandlers: [
    new winston.transports.File({
      filename: path.join(logsDir, 'exceptions.log')
    })
  ],
  
  // 拒绝处理
  rejectionHandlers: [
    new winston.transports.File({
      filename: path.join(logsDir, 'rejections.log')
    })
  ]
});

// 开发环境添加控制台输出
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: consoleFormat
  }));
}

// 生产环境错误时也输出到控制台
if (process.env.NODE_ENV === 'production') {
  logger.add(new winston.transports.Console({
    level: 'error',
    format: consoleFormat
  }));
}

// 扩展logger功能
logger.apiAccess = (req, res, responseTime) => {
  const logData = {
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    referer: req.get('Referer'),
    statusCode: res.statusCode,
    responseTime: responseTime,
    apiKey: req.apiKey?.id || null,
    userId: req.user?.id || null,
    timestamp: new Date().toISOString()
  };
  
  logger.info('API Access', logData);
};

logger.apiError = (req, error, responseTime) => {
  const logData = {
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    error: {
      message: error.message,
      stack: error.stack,
      name: error.name
    },
    responseTime: responseTime,
    apiKey: req.apiKey?.id || null,
    userId: req.user?.id || null,
    timestamp: new Date().toISOString()
  };
  
  logger.error('API Error', logData);
};

logger.security = (event, details) => {
  const logData = {
    event,
    details,
    timestamp: new Date().toISOString(),
    level: 'security'
  };
  
  logger.warn('Security Event', logData);
};

logger.performance = (operation, duration, details = {}) => {
  const logData = {
    operation,
    duration,
    details,
    timestamp: new Date().toISOString()
  };
  
  if (duration > 1000) { // 超过1秒的操作记录为警告
    logger.warn('Slow Operation', logData);
  } else {
    logger.info('Performance', logData);
  }
};

module.exports = logger;
