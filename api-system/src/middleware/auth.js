const jwt = require('jsonwebtoken');
const database = require('../config/database');
const redis = require('../config/redis');
const logger = require('../utils/logger');

// API密钥认证中间件
const apiKeyAuth = async (req, res, next) => {
  try {
    const apiKey = req.headers['x-api-key'] || req.query.api_key;
    
    if (!apiKey) {
      return res.status(401).json({
        error: 'API key is required',
        code: 'MISSING_API_KEY'
      });
    }

    // 从缓存中获取API密钥信息
    let keyInfo = await redis.get(`api_key:${apiKey}`);
    
    if (!keyInfo) {
      // 缓存中没有，从数据库查询
      keyInfo = await database.findApiKeyByKey(apiKey);
      
      if (!keyInfo) {
        return res.status(401).json({
          error: 'Invalid API key',
          code: 'INVALID_API_KEY'
        });
      }

      // 缓存API密钥信息（5分钟）
      await redis.set(`api_key:${apiKey}`, keyInfo, 300);
    }

    // 检查API密钥状态
    if (keyInfo.status !== 'active') {
      return res.status(401).json({
        error: 'API key is disabled',
        code: 'API_KEY_DISABLED'
      });
    }

    // 检查用户状态
    if (keyInfo.user_status !== 'active') {
      return res.status(401).json({
        error: 'User account is disabled',
        code: 'USER_DISABLED'
      });
    }

    // 检查API密钥是否过期
    if (keyInfo.expires_at && new Date(keyInfo.expires_at) < new Date()) {
      return res.status(401).json({
        error: 'API key has expired',
        code: 'API_KEY_EXPIRED'
      });
    }

    // 检查域名限制
    if (keyInfo.allowed_origins && keyInfo.allowed_origins.length > 0) {
      const origin = req.headers.origin || req.headers.referer;
      const allowedOrigins = JSON.parse(keyInfo.allowed_origins);
      
      if (!allowedOrigins.includes('*') && origin) {
        const isAllowed = allowedOrigins.some(allowedOrigin => {
          if (allowedOrigin === '*') return true;
          if (allowedOrigin.startsWith('*.')) {
            const domain = allowedOrigin.substring(2);
            return origin.endsWith(domain);
          }
          return origin.includes(allowedOrigin);
        });

        if (!isAllowed) {
          return res.status(403).json({
            error: 'Origin not allowed',
            code: 'ORIGIN_NOT_ALLOWED'
          });
        }
      }
    }

    // 将API密钥信息添加到请求对象
    req.apiKey = keyInfo;
    req.user = {
      id: keyInfo.user_id,
      username: keyInfo.username,
      email: keyInfo.email
    };

    next();
  } catch (error) {
    logger.error('API key authentication error:', error);
    res.status(500).json({
      error: 'Authentication service error',
      code: 'AUTH_SERVICE_ERROR'
    });
  }
};

// JWT认证中间件（用于管理后台）
const jwtAuth = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        error: 'Access token is required',
        code: 'MISSING_TOKEN'
      });
    }

    // 验证JWT
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // 检查token是否在黑名单中
    const isBlacklisted = await redis.exists(`blacklist:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({
        error: 'Token has been revoked',
        code: 'TOKEN_REVOKED'
      });
    }

    // 获取用户信息
    const user = await database.findUserById(decoded.userId);
    if (!user) {
      return res.status(401).json({
        error: 'User not found',
        code: 'USER_NOT_FOUND'
      });
    }

    if (user.status !== 'active') {
      return res.status(401).json({
        error: 'User account is disabled',
        code: 'USER_DISABLED'
      });
    }

    req.user = user;
    req.token = token;
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        error: 'Invalid token',
        code: 'INVALID_TOKEN'
      });
    }
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        error: 'Token has expired',
        code: 'TOKEN_EXPIRED'
      });
    }

    logger.error('JWT authentication error:', error);
    res.status(500).json({
      error: 'Authentication service error',
      code: 'AUTH_SERVICE_ERROR'
    });
  }
};

// 可选的API密钥认证（允许游客访问）
const optionalApiKeyAuth = async (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  if (apiKey) {
    // 如果提供了API密钥，进行认证
    return apiKeyAuth(req, res, next);
  } else {
    // 没有API密钥，设置为游客用户
    req.user = {
      id: null,
      username: 'guest',
      email: null,
      type: 'guest'
    };
    req.apiKey = null;
    next();
  }
};

// 管理员权限检查
const adminAuth = (requiredRole = 'operator') => {
  return async (req, res, next) => {
    try {
      if (!req.user || !req.user.role) {
        return res.status(403).json({
          error: 'Admin access required',
          code: 'ADMIN_ACCESS_REQUIRED'
        });
      }

      const roleHierarchy = {
        'operator': 1,
        'admin': 2,
        'super_admin': 3
      };

      const userRoleLevel = roleHierarchy[req.user.role] || 0;
      const requiredRoleLevel = roleHierarchy[requiredRole] || 0;

      if (userRoleLevel < requiredRoleLevel) {
        return res.status(403).json({
          error: 'Insufficient permissions',
          code: 'INSUFFICIENT_PERMISSIONS'
        });
      }

      next();
    } catch (error) {
      logger.error('Admin authentication error:', error);
      res.status(500).json({
        error: 'Authentication service error',
        code: 'AUTH_SERVICE_ERROR'
      });
    }
  };
};

module.exports = {
  apiKeyAuth,
  jwtAuth,
  optionalApiKeyAuth,
  adminAuth
};
