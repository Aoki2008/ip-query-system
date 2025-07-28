const mysql = require('mysql2/promise');
const logger = require('../utils/logger');

class Database {
  constructor() {
    this.pool = null;
    this.config = {
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3306,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || '',
      database: process.env.DB_NAME || 'ip_query_system',
      waitForConnections: true,
      connectionLimit: 10,
      queueLimit: 0,
      acquireTimeout: 60000,
      timeout: 60000,
      reconnect: true,
      charset: 'utf8mb4'
    };
  }

  async init() {
    try {
      this.pool = mysql.createPool(this.config);
      logger.info('Database pool created successfully');
    } catch (error) {
      logger.error('Failed to create database pool:', error);
      throw error;
    }
  }

  async testConnection() {
    try {
      if (!this.pool) {
        await this.init();
      }
      const connection = await this.pool.getConnection();
      await connection.ping();
      connection.release();
      logger.info('Database connection test successful');
    } catch (error) {
      logger.error('Database connection test failed:', error);
      throw error;
    }
  }

  async query(sql, params = []) {
    try {
      if (!this.pool) {
        await this.init();
      }
      const [rows] = await this.pool.execute(sql, params);
      return rows;
    } catch (error) {
      logger.error('Database query error:', { sql, params, error: error.message });
      throw error;
    }
  }

  async transaction(callback) {
    const connection = await this.pool.getConnection();
    try {
      await connection.beginTransaction();
      const result = await callback(connection);
      await connection.commit();
      return result;
    } catch (error) {
      await connection.rollback();
      throw error;
    } finally {
      connection.release();
    }
  }

  async close() {
    if (this.pool) {
      await this.pool.end();
      logger.info('Database pool closed');
    }
  }

  // 用户相关查询
  async findUserByEmail(email) {
    const sql = 'SELECT * FROM users WHERE email = ? LIMIT 1';
    const rows = await this.query(sql, [email]);
    return rows[0] || null;
  }

  async findUserById(id) {
    const sql = 'SELECT * FROM users WHERE id = ? LIMIT 1';
    const rows = await this.query(sql, [id]);
    return rows[0] || null;
  }

  async createUser(userData) {
    const sql = `
      INSERT INTO users (id, username, email, password_hash, status, user_type)
      VALUES (UUID(), ?, ?, ?, ?, ?)
    `;
    const params = [
      userData.username,
      userData.email,
      userData.password_hash,
      userData.status || 'pending',
      userData.user_type || 'free'
    ];
    await this.query(sql, params);
  }

  // API密钥相关查询
  async findApiKeyByKey(apiKey) {
    const sql = `
      SELECT ak.*, u.username, u.email, u.status as user_status
      FROM api_keys ak
      JOIN users u ON ak.user_id = u.id
      WHERE ak.api_key = ? AND ak.status = 'active'
      LIMIT 1
    `;
    const rows = await this.query(sql, [apiKey]);
    return rows[0] || null;
  }

  async updateApiKeyLastUsed(apiKeyId) {
    const sql = 'UPDATE api_keys SET last_used_at = NOW() WHERE id = ?';
    await this.query(sql, [apiKeyId]);
  }

  // 日志记录
  async logApiCall(logData) {
    const sql = `
      INSERT INTO api_logs (
        api_key_id, user_id, client_ip, query_ip, user_agent, 
        referer, response_time, status_code, error_message, response_data
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    const params = [
      logData.api_key_id,
      logData.user_id,
      logData.client_ip,
      logData.query_ip,
      logData.user_agent,
      logData.referer,
      logData.response_time,
      logData.status_code,
      logData.error_message,
      JSON.stringify(logData.response_data)
    ];
    await this.query(sql, params);
  }

  // 统计查询
  async getApiCallStats(apiKeyId, timeRange = '24h') {
    let timeCondition = '';
    switch (timeRange) {
      case '1h':
        timeCondition = 'AND created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)';
        break;
      case '24h':
        timeCondition = 'AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)';
        break;
      case '7d':
        timeCondition = 'AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)';
        break;
      case '30d':
        timeCondition = 'AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)';
        break;
    }

    const sql = `
      SELECT 
        COUNT(*) as total_calls,
        COUNT(CASE WHEN status_code = 200 THEN 1 END) as success_calls,
        COUNT(CASE WHEN status_code != 200 THEN 1 END) as error_calls,
        AVG(response_time) as avg_response_time
      FROM api_logs 
      WHERE api_key_id = ? ${timeCondition}
    `;
    const rows = await this.query(sql, [apiKeyId]);
    return rows[0] || { total_calls: 0, success_calls: 0, error_calls: 0, avg_response_time: 0 };
  }
}

module.exports = new Database();
