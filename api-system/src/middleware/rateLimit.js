const redis = require('../config/redis');
const logger = require('../utils/logger');

// 创建限流中间件
const createRateLimit = (options = {}) => {
  const {
    windowMs = 60 * 1000, // 1分钟
    max = 60, // 最大请求数
    keyGenerator = (req) => req.ip, // 生成限流key的函数
    skipSuccessfulRequests = false,
    skipFailedRequests = false,
    onLimitReached = null
  } = options;

  return async (req, res, next) => {
    try {
      const key = `rate_limit:${keyGenerator(req)}`;
      const windowSeconds = Math.floor(windowMs / 1000);
      
      // 检查限流
      const result = await redis.checkRateLimit(key, max, windowSeconds);
      
      // 设置响应头
      res.set({
        'X-RateLimit-Limit': max,
        'X-RateLimit-Remaining': result.remaining,
        'X-RateLimit-Reset': new Date(result.resetTime).toISOString()
      });

      if (!result.allowed) {
        // 触发限流回调
        if (onLimitReached) {
          onLimitReached(req, res);
        }

        logger.warn(`Rate limit exceeded for key: ${key}`, {
          ip: req.ip,
          userAgent: req.get('User-Agent'),
          path: req.path
        });

        return res.status(429).json({
          error: 'Too many requests',
          code: 'RATE_LIMIT_EXCEEDED',
          limit: max,
          remaining: result.remaining,
          resetTime: result.resetTime
        });
      }

      // 在响应结束后更新计数器（如果需要跳过成功/失败请求）
      if (skipSuccessfulRequests || skipFailedRequests) {
        const originalSend = res.send;
        res.send = function(data) {
          const statusCode = res.statusCode;
          const shouldSkip = (
            (skipSuccessfulRequests && statusCode < 400) ||
            (skipFailedRequests && statusCode >= 400)
          );

          if (shouldSkip) {
            // 减少计数器
            redis.incr(key, -1);
          }

          return originalSend.call(this, data);
        };
      }

      next();
    } catch (error) {
      logger.error('Rate limit middleware error:', error);
      // 限流服务出错时，允许请求通过
      next();
    }
  };
};

// API密钥专用限流
const apiKeyRateLimit = async (req, res, next) => {
  try {
    if (!req.apiKey) {
      return next();
    }

    const apiKeyId = req.apiKey.id;
    const perMinuteLimit = req.apiKey.rate_limit_per_minute || 60;
    const perDayLimit = req.apiKey.rate_limit_per_day || 1000;

    // 检查每分钟限制
    const minuteKey = `api_rate:${apiKeyId}:minute:${Math.floor(Date.now() / 60000)}`;
    const minuteResult = await redis.checkRateLimit(minuteKey, perMinuteLimit, 60);

    if (!minuteResult.allowed) {
      return res.status(429).json({
        error: 'API rate limit exceeded (per minute)',
        code: 'API_RATE_LIMIT_MINUTE',
        limit: perMinuteLimit,
        remaining: minuteResult.remaining,
        resetTime: minuteResult.resetTime
      });
    }

    // 检查每日限制
    const dayKey = `api_rate:${apiKeyId}:day:${Math.floor(Date.now() / 86400000)}`;
    const dayResult = await redis.checkRateLimit(dayKey, perDayLimit, 86400);

    if (!dayResult.allowed) {
      return res.status(429).json({
        error: 'API rate limit exceeded (per day)',
        code: 'API_RATE_LIMIT_DAY',
        limit: perDayLimit,
        remaining: dayResult.remaining,
        resetTime: dayResult.resetTime
      });
    }

    // 设置响应头
    res.set({
      'X-API-RateLimit-Minute-Limit': perMinuteLimit,
      'X-API-RateLimit-Minute-Remaining': minuteResult.remaining,
      'X-API-RateLimit-Day-Limit': perDayLimit,
      'X-API-RateLimit-Day-Remaining': dayResult.remaining
    });

    next();
  } catch (error) {
    logger.error('API rate limit middleware error:', error);
    next();
  }
};

// 游客限流
const guestRateLimit = createRateLimit({
  windowMs: 24 * 60 * 60 * 1000, // 24小时
  max: 20, // 每日20次
  keyGenerator: (req) => `guest:${req.ip}`,
  onLimitReached: (req, res) => {
    logger.warn(`Guest rate limit exceeded for IP: ${req.ip}`);
  }
});

// IP查询专用限流
const ipQueryRateLimit = async (req, res, next) => {
  try {
    if (req.user && req.user.type !== 'guest') {
      // 已认证用户使用API密钥限流
      return apiKeyRateLimit(req, res, next);
    } else {
      // 游客使用IP限流
      return guestRateLimit(req, res, next);
    }
  } catch (error) {
    logger.error('IP query rate limit error:', error);
    next();
  }
};

// 批量查询限流
const batchQueryRateLimit = createRateLimit({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 10, // 每小时最多10次批量查询
  keyGenerator: (req) => {
    if (req.apiKey) {
      return `batch:api:${req.apiKey.id}`;
    }
    return `batch:guest:${req.ip}`;
  }
});

// 登录限流
const loginRateLimit = createRateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 5, // 最多5次登录尝试
  keyGenerator: (req) => `login:${req.ip}`,
  skipSuccessfulRequests: true, // 成功登录不计入限制
  onLimitReached: (req, res) => {
    logger.warn(`Login rate limit exceeded for IP: ${req.ip}`, {
      userAgent: req.get('User-Agent'),
      email: req.body.email
    });
  }
});

// 注册限流
const registerRateLimit = createRateLimit({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 3, // 每小时最多3次注册
  keyGenerator: (req) => `register:${req.ip}`
});

// 密码重置限流
const passwordResetRateLimit = createRateLimit({
  windowMs: 60 * 60 * 1000, // 1小时
  max: 3, // 每小时最多3次密码重置请求
  keyGenerator: (req) => `password_reset:${req.ip}`
});

module.exports = {
  createRateLimit,
  apiKeyRateLimit,
  guestRateLimit,
  ipQueryRateLimit,
  batchQueryRateLimit,
  loginRateLimit,
  registerRateLimit,
  passwordResetRateLimit
};
