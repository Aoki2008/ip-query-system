const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const { v4: uuidv4 } = require('uuid');
const router = express.Router();

const database = require('../config/database');
const redis = require('../config/redis');
const logger = require('../utils/logger');
const { jwtAuth } = require('../middleware/auth');
const { loginRateLimit, registerRateLimit, passwordResetRateLimit } = require('../middleware/rateLimit');

// 用户注册
router.post('/register',
  registerRateLimit,
  [
    body('username')
      .isLength({ min: 3, max: 50 })
      .withMessage('Username must be 3-50 characters')
      .matches(/^[a-zA-Z0-9_]+$/)
      .withMessage('Username can only contain letters, numbers and underscores'),
    body('email')
      .isEmail()
      .withMessage('Valid email is required')
      .normalizeEmail(),
    body('password')
      .isLength({ min: 8 })
      .withMessage('Password must be at least 8 characters')
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
      .withMessage('Password must contain at least one lowercase letter, one uppercase letter, and one number')
  ],
  async (req, res) => {
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

      const { username, email, password } = req.body;

      // 检查用户是否已存在
      const existingUser = await database.findUserByEmail(email);
      if (existingUser) {
        return res.status(409).json({
          error: 'User already exists',
          code: 'USER_EXISTS'
        });
      }

      // 检查用户名是否已存在
      const existingUsername = await database.query(
        'SELECT id FROM users WHERE username = ? LIMIT 1',
        [username]
      );
      if (existingUsername.length > 0) {
        return res.status(409).json({
          error: 'Username already taken',
          code: 'USERNAME_TAKEN'
        });
      }

      // 加密密码
      const passwordHash = await bcrypt.hash(password, 12);

      // 创建用户
      const userData = {
        username,
        email,
        password_hash: passwordHash,
        status: 'active', // 简化流程，直接激活
        user_type: 'free'
      };

      await database.createUser(userData);

      // 获取创建的用户
      const newUser = await database.findUserByEmail(email);

      // 创建默认API密钥
      const apiKey = `ak_${uuidv4().replace(/-/g, '')}`;
      const secretKey = `sk_${uuidv4().replace(/-/g, '')}`;

      await database.query(`
        INSERT INTO api_keys (id, user_id, key_name, api_key, secret_key, status)
        VALUES (UUID(), ?, ?, ?, ?, 'active')
      `, [newUser.id, 'Default Key', apiKey, secretKey]);

      logger.info('User registered successfully', {
        userId: newUser.id,
        username,
        email,
        ip: req.ip
      });

      res.status(201).json({
        success: true,
        message: 'User registered successfully',
        data: {
          user: {
            id: newUser.id,
            username: newUser.username,
            email: newUser.email,
            user_type: newUser.user_type
          },
          api_key: apiKey
        }
      });

    } catch (error) {
      logger.error('Registration error:', error);
      res.status(500).json({
        error: 'Registration failed',
        code: 'REGISTRATION_FAILED',
        message: error.message
      });
    }
  }
);

// 用户登录
router.post('/login',
  loginRateLimit,
  [
    body('email')
      .isEmail()
      .withMessage('Valid email is required')
      .normalizeEmail(),
    body('password')
      .notEmpty()
      .withMessage('Password is required')
  ],
  async (req, res) => {
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

      const { email, password } = req.body;

      // 查找用户
      const user = await database.findUserByEmail(email);
      if (!user) {
        return res.status(401).json({
          error: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS'
        });
      }

      // 检查用户状态
      if (user.status !== 'active') {
        return res.status(401).json({
          error: 'Account is disabled',
          code: 'ACCOUNT_DISABLED'
        });
      }

      // 验证密码
      const isValidPassword = await bcrypt.compare(password, user.password_hash);
      if (!isValidPassword) {
        return res.status(401).json({
          error: 'Invalid credentials',
          code: 'INVALID_CREDENTIALS'
        });
      }

      // 生成JWT token
      const token = jwt.sign(
        { 
          userId: user.id,
          email: user.email,
          username: user.username,
          userType: user.user_type
        },
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
      );

      // 记录登录日志
      await database.query(`
        INSERT INTO user_login_logs (user_id, ip_address, user_agent, login_type, status)
        VALUES (?, ?, ?, 'web', 'success')
      `, [user.id, req.ip, req.get('User-Agent')]);

      logger.info('User logged in successfully', {
        userId: user.id,
        username: user.username,
        email: user.email,
        ip: req.ip
      });

      res.json({
        success: true,
        message: 'Login successful',
        data: {
          token,
          user: {
            id: user.id,
            username: user.username,
            email: user.email,
            user_type: user.user_type,
            daily_limit: user.daily_limit
          }
        }
      });

    } catch (error) {
      logger.error('Login error:', error);
      res.status(500).json({
        error: 'Login failed',
        code: 'LOGIN_FAILED',
        message: error.message
      });
    }
  }
);

// 用户登出
router.post('/logout',
  jwtAuth,
  async (req, res) => {
    try {
      // 将token加入黑名单
      const token = req.token;
      const decoded = jwt.decode(token);
      const expiresIn = decoded.exp - Math.floor(Date.now() / 1000);
      
      if (expiresIn > 0) {
        await redis.set(`blacklist:${token}`, true, expiresIn);
      }

      logger.info('User logged out', {
        userId: req.user.id,
        username: req.user.username,
        ip: req.ip
      });

      res.json({
        success: true,
        message: 'Logout successful'
      });

    } catch (error) {
      logger.error('Logout error:', error);
      res.status(500).json({
        error: 'Logout failed',
        code: 'LOGOUT_FAILED',
        message: error.message
      });
    }
  }
);

// 获取用户信息
router.get('/me',
  jwtAuth,
  async (req, res) => {
    try {
      const user = req.user;
      
      // 获取用户的API密钥
      const apiKeys = await database.query(`
        SELECT id, key_name, api_key, rate_limit_per_minute, rate_limit_per_day, 
               status, last_used_at, created_at
        FROM api_keys 
        WHERE user_id = ? 
        ORDER BY created_at DESC
      `, [user.id]);

      res.json({
        success: true,
        data: {
          user: {
            id: user.id,
            username: user.username,
            email: user.email,
            user_type: user.user_type,
            daily_limit: user.daily_limit,
            status: user.status,
            created_at: user.created_at
          },
          api_keys: apiKeys
        }
      });

    } catch (error) {
      logger.error('Get user info error:', error);
      res.status(500).json({
        error: 'Failed to get user info',
        code: 'GET_USER_INFO_FAILED',
        message: error.message
      });
    }
  }
);

module.exports = router;
