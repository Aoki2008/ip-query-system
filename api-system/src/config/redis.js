const { createClient } = require('redis');
const logger = require('../utils/logger');

class RedisClient {
  constructor() {
    this.client = null;
    this.config = {
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD || null,
      db: process.env.REDIS_DB || 0,
      retryDelayOnFailover: 100,
      enableReadyCheck: true,
      maxRetriesPerRequest: 3,
    };
  }

  async init() {
    try {
      this.client = createClient({
        socket: {
          host: this.config.host,
          port: this.config.port,
        },
        password: this.config.password,
        database: this.config.db,
      });

      this.client.on('error', (err) => {
        logger.error('Redis Client Error:', err);
      });

      this.client.on('connect', () => {
        logger.info('Redis Client Connected');
      });

      this.client.on('ready', () => {
        logger.info('Redis Client Ready');
      });

      this.client.on('end', () => {
        logger.info('Redis Client Disconnected');
      });

      await this.client.connect();
      logger.info('Redis connection established');
    } catch (error) {
      logger.error('Failed to connect to Redis:', error);
      throw error;
    }
  }

  async ping() {
    try {
      if (!this.client) {
        await this.init();
      }
      const result = await this.client.ping();
      return result === 'PONG';
    } catch (error) {
      logger.error('Redis ping failed:', error);
      throw error;
    }
  }

  async get(key) {
    try {
      if (!this.client) {
        await this.init();
      }
      const value = await this.client.get(key);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      logger.error('Redis get error:', { key, error: error.message });
      return null;
    }
  }

  async set(key, value, ttl = 3600) {
    try {
      if (!this.client) {
        await this.init();
      }
      const serializedValue = JSON.stringify(value);
      await this.client.setEx(key, ttl, serializedValue);
      return true;
    } catch (error) {
      logger.error('Redis set error:', { key, error: error.message });
      return false;
    }
  }

  async del(key) {
    try {
      if (!this.client) {
        await this.init();
      }
      await this.client.del(key);
      return true;
    } catch (error) {
      logger.error('Redis del error:', { key, error: error.message });
      return false;
    }
  }

  async exists(key) {
    try {
      if (!this.client) {
        await this.init();
      }
      const result = await this.client.exists(key);
      return result === 1;
    } catch (error) {
      logger.error('Redis exists error:', { key, error: error.message });
      return false;
    }
  }

  async incr(key, ttl = 3600) {
    try {
      if (!this.client) {
        await this.init();
      }
      const result = await this.client.incr(key);
      if (result === 1) {
        await this.client.expire(key, ttl);
      }
      return result;
    } catch (error) {
      logger.error('Redis incr error:', { key, error: error.message });
      return 0;
    }
  }

  async hget(hash, field) {
    try {
      if (!this.client) {
        await this.init();
      }
      const value = await this.client.hGet(hash, field);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      logger.error('Redis hget error:', { hash, field, error: error.message });
      return null;
    }
  }

  async hset(hash, field, value, ttl = 3600) {
    try {
      if (!this.client) {
        await this.init();
      }
      const serializedValue = JSON.stringify(value);
      await this.client.hSet(hash, field, serializedValue);
      await this.client.expire(hash, ttl);
      return true;
    } catch (error) {
      logger.error('Redis hset error:', { hash, field, error: error.message });
      return false;
    }
  }

  async quit() {
    if (this.client) {
      await this.client.quit();
      logger.info('Redis connection closed');
    }
  }

  // 限流相关方法
  async checkRateLimit(key, limit, window) {
    try {
      const current = await this.incr(key, window);
      return {
        allowed: current <= limit,
        current,
        limit,
        remaining: Math.max(0, limit - current),
        resetTime: Date.now() + (window * 1000)
      };
    } catch (error) {
      logger.error('Rate limit check error:', { key, error: error.message });
      return { allowed: true, current: 0, limit, remaining: limit };
    }
  }

  // 缓存IP查询结果
  async cacheIpResult(ip, result, ttl = 3600) {
    const key = `ip:${ip}`;
    return await this.set(key, result, ttl);
  }

  async getCachedIpResult(ip) {
    const key = `ip:${ip}`;
    return await this.get(key);
  }
}

module.exports = new RedisClient();
