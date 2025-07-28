const express = require('express');
const { body, query, validationResult } = require('express-validator');
const router = express.Router();

const { optionalApiKeyAuth } = require('../middleware/auth');
const { ipQueryRateLimit, batchQueryRateLimit } = require('../middleware/rateLimit');
const maxmindService = require('../services/maxmind');
const database = require('../config/database');
const redis = require('../config/redis');
const logger = require('../utils/logger');

// 验证IP地址格式
const validateIp = (value) => {
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$/;
  
  if (!ipv4Regex.test(value) && !ipv6Regex.test(value)) {
    throw new Error('Invalid IP address format');
  }
  return true;
};

// 单个IP查询
router.get('/query',
  optionalApiKeyAuth,
  ipQueryRateLimit,
  [
    query('ip')
      .notEmpty()
      .withMessage('IP address is required')
      .custom(validateIp)
  ],
  async (req, res) => {
    const startTime = Date.now();
    
    try {
      // 验证请求参数
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: 'Validation failed',
          code: 'VALIDATION_ERROR',
          details: errors.array()
        });
      }

      const { ip } = req.query;
      const clientIp = req.ip || req.connection.remoteAddress;

      // 检查缓存
      let result = await redis.getCachedIpResult(ip);
      
      if (!result) {
        // 缓存中没有，查询MaxMind数据库
        result = await maxmindService.lookupIp(ip);
        
        // 缓存结果（1小时）
        await redis.cacheIpResult(ip, result, 3600);
      }

      const responseTime = Date.now() - startTime;

      // 记录API调用日志
      const logData = {
        api_key_id: req.apiKey?.id || null,
        user_id: req.user?.id || null,
        client_ip: clientIp,
        query_ip: ip,
        user_agent: req.get('User-Agent'),
        referer: req.get('Referer'),
        response_time: responseTime,
        status_code: 200,
        response_data: result
      };

      // 异步记录日志，不阻塞响应
      database.logApiCall(logData).catch(error => {
        logger.error('Failed to log API call:', error);
      });

      // 更新API密钥最后使用时间
      if (req.apiKey) {
        database.updateApiKeyLastUsed(req.apiKey.id).catch(error => {
          logger.error('Failed to update API key last used time:', error);
        });
      }

      res.json({
        success: true,
        data: result,
        cached: !!result.cached,
        response_time: responseTime
      });

    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      logger.error('IP query error:', {
        ip: req.query.ip,
        error: error.message,
        stack: error.stack
      });

      // 记录错误日志
      const logData = {
        api_key_id: req.apiKey?.id || null,
        user_id: req.user?.id || null,
        client_ip: req.ip,
        query_ip: req.query.ip,
        user_agent: req.get('User-Agent'),
        referer: req.get('Referer'),
        response_time: responseTime,
        status_code: 500,
        error_message: error.message
      };

      database.logApiCall(logData).catch(logError => {
        logger.error('Failed to log API call error:', logError);
      });

      res.status(500).json({
        error: 'IP query failed',
        code: 'QUERY_FAILED',
        message: error.message
      });
    }
  }
);

// 批量IP查询
router.post('/batch',
  optionalApiKeyAuth,
  batchQueryRateLimit,
  [
    body('ips')
      .isArray({ min: 1, max: 100 })
      .withMessage('IPs must be an array with 1-100 items'),
    body('ips.*')
      .custom(validateIp)
  ],
  async (req, res) => {
    const startTime = Date.now();
    
    try {
      // 验证请求参数
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: 'Validation failed',
          code: 'VALIDATION_ERROR',
          details: errors.array()
        });
      }

      const { ips } = req.body;
      const clientIp = req.ip || req.connection.remoteAddress;
      const results = [];

      // 并发查询所有IP
      const promises = ips.map(async (ip) => {
        try {
          // 检查缓存
          let result = await redis.getCachedIpResult(ip);
          
          if (!result) {
            // 缓存中没有，查询MaxMind数据库
            result = await maxmindService.lookupIp(ip);
            
            // 缓存结果（1小时）
            await redis.cacheIpResult(ip, result, 3600);
          }

          return {
            ip,
            success: true,
            data: result,
            cached: !!result.cached
          };
        } catch (error) {
          logger.error(`Batch query error for IP ${ip}:`, error);
          return {
            ip,
            success: false,
            error: error.message
          };
        }
      });

      const queryResults = await Promise.all(promises);
      const responseTime = Date.now() - startTime;

      // 统计结果
      const successCount = queryResults.filter(r => r.success).length;
      const errorCount = queryResults.length - successCount;

      // 记录批量查询日志
      const logData = {
        api_key_id: req.apiKey?.id || null,
        user_id: req.user?.id || null,
        client_ip: clientIp,
        query_ip: `batch:${ips.length}`, // 标记为批量查询
        user_agent: req.get('User-Agent'),
        referer: req.get('Referer'),
        response_time: responseTime,
        status_code: 200,
        response_data: {
          total: ips.length,
          success: successCount,
          errors: errorCount
        }
      };

      database.logApiCall(logData).catch(error => {
        logger.error('Failed to log batch API call:', error);
      });

      // 更新API密钥最后使用时间
      if (req.apiKey) {
        database.updateApiKeyLastUsed(req.apiKey.id).catch(error => {
          logger.error('Failed to update API key last used time:', error);
        });
      }

      res.json({
        success: true,
        data: queryResults,
        summary: {
          total: ips.length,
          success: successCount,
          errors: errorCount
        },
        response_time: responseTime
      });

    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      logger.error('Batch query error:', {
        ips: req.body.ips,
        error: error.message,
        stack: error.stack
      });

      res.status(500).json({
        error: 'Batch query failed',
        code: 'BATCH_QUERY_FAILED',
        message: error.message
      });
    }
  }
);

// 获取IP查询统计信息
router.get('/stats',
  optionalApiKeyAuth,
  async (req, res) => {
    try {
      if (!req.apiKey) {
        return res.status(401).json({
          error: 'API key required for statistics',
          code: 'API_KEY_REQUIRED'
        });
      }

      const { timeRange = '24h' } = req.query;
      const stats = await database.getApiCallStats(req.apiKey.id, timeRange);

      res.json({
        success: true,
        data: stats,
        timeRange
      });

    } catch (error) {
      logger.error('Stats query error:', error);
      res.status(500).json({
        error: 'Failed to get statistics',
        code: 'STATS_QUERY_FAILED',
        message: error.message
      });
    }
  }
);

// 获取数据库信息（仅管理员）
router.get('/database/info',
  optionalApiKeyAuth,
  async (req, res) => {
    try {
      // 检查是否为管理员
      if (!req.user || req.user.type === 'guest') {
        return res.status(403).json({
          error: 'Admin access required',
          code: 'ADMIN_ACCESS_REQUIRED'
        });
      }

      const dbInfo = maxmindService.getDbInfo();

      res.json({
        success: true,
        data: dbInfo
      });

    } catch (error) {
      logger.error('Database info query error:', error);
      res.status(500).json({
        error: 'Failed to get database info',
        code: 'DB_INFO_QUERY_FAILED',
        message: error.message
      });
    }
  }
);

module.exports = router;
