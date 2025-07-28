const maxmind = require('maxmind');
const path = require('path');
const fs = require('fs');
const logger = require('../utils/logger');

class MaxMindService {
  constructor() {
    this.cityReader = null;
    this.asnReader = null;
    this.dbPath = path.join(__dirname, '../../data/GeoLite2-City.mmdb');
    this.asnDbPath = path.join(__dirname, '../../data/GeoLite2-ASN.mmdb');
  }

  async init() {
    try {
      // 检查数据库文件是否存在
      if (!fs.existsSync(this.dbPath)) {
        logger.warn(`MaxMind City database not found at: ${this.dbPath}`);
        throw new Error('MaxMind City database file not found');
      }

      // 加载城市数据库
      this.cityReader = await maxmind.open(this.dbPath);
      logger.info('MaxMind City database loaded successfully');

      // 尝试加载ASN数据库（可选）
      if (fs.existsSync(this.asnDbPath)) {
        this.asnReader = await maxmind.open(this.asnDbPath);
        logger.info('MaxMind ASN database loaded successfully');
      } else {
        logger.warn('MaxMind ASN database not found, ASN information will not be available');
      }

    } catch (error) {
      logger.error('Failed to initialize MaxMind service:', error);
      throw error;
    }
  }

  async lookupIp(ip) {
    try {
      if (!this.cityReader) {
        await this.init();
      }

      // 验证IP地址格式
      if (!this.isValidIp(ip)) {
        throw new Error('Invalid IP address format');
      }

      // 查询城市信息
      const cityData = this.cityReader.get(ip);
      
      // 查询ASN信息（如果可用）
      let asnData = null;
      if (this.asnReader) {
        try {
          asnData = this.asnReader.get(ip);
        } catch (error) {
          logger.warn('ASN lookup failed:', error.message);
        }
      }

      // 格式化返回数据
      const result = this.formatResult(ip, cityData, asnData);
      
      logger.info(`IP lookup successful for ${ip}`);
      return result;

    } catch (error) {
      logger.error(`IP lookup failed for ${ip}:`, error.message);
      throw error;
    }
  }

  formatResult(ip, cityData, asnData) {
    const result = {
      ip: ip,
      country: null,
      country_code: null,
      region: null,
      region_code: null,
      city: null,
      postal_code: null,
      latitude: null,
      longitude: null,
      timezone: null,
      isp: null,
      organization: null,
      asn: null,
      asn_organization: null,
      is_eu: false,
      accuracy_radius: null
    };

    if (cityData) {
      // 国家信息
      if (cityData.country) {
        result.country = cityData.country.names?.en || cityData.country.names?.zh_CN || null;
        result.country_code = cityData.country.iso_code || null;
        result.is_eu = cityData.country.is_in_european_union || false;
      }

      // 地区信息
      if (cityData.subdivisions && cityData.subdivisions.length > 0) {
        const subdivision = cityData.subdivisions[0];
        result.region = subdivision.names?.en || subdivision.names?.zh_CN || null;
        result.region_code = subdivision.iso_code || null;
      }

      // 城市信息
      if (cityData.city) {
        result.city = cityData.city.names?.en || cityData.city.names?.zh_CN || null;
      }

      // 邮政编码
      if (cityData.postal) {
        result.postal_code = cityData.postal.code || null;
      }

      // 地理位置
      if (cityData.location) {
        result.latitude = cityData.location.latitude || null;
        result.longitude = cityData.location.longitude || null;
        result.timezone = cityData.location.time_zone || null;
        result.accuracy_radius = cityData.location.accuracy_radius || null;
      }

      // ISP信息（从traits获取）
      if (cityData.traits) {
        result.isp = cityData.traits.isp || null;
        result.organization = cityData.traits.organization || null;
      }
    }

    // ASN信息
    if (asnData) {
      result.asn = asnData.autonomous_system_number || null;
      result.asn_organization = asnData.autonomous_system_organization || null;
      
      // 如果没有ISP信息，使用ASN组织名称
      if (!result.isp && result.asn_organization) {
        result.isp = result.asn_organization;
      }
    }

    return result;
  }

  isValidIp(ip) {
    // IPv4正则表达式
    const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    
    // IPv6正则表达式（简化版）
    const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$/;
    
    return ipv4Regex.test(ip) || ipv6Regex.test(ip);
  }

  async updateDatabase() {
    // 这里可以实现自动更新MaxMind数据库的逻辑
    // 需要MaxMind许可证密钥
    logger.info('Database update functionality not implemented yet');
  }

  getDbInfo() {
    const info = {
      cityDbExists: fs.existsSync(this.dbPath),
      asnDbExists: fs.existsSync(this.asnDbPath),
      cityDbPath: this.dbPath,
      asnDbPath: this.asnDbPath
    };

    if (info.cityDbExists) {
      const stats = fs.statSync(this.dbPath);
      info.cityDbSize = stats.size;
      info.cityDbModified = stats.mtime;
    }

    if (info.asnDbExists) {
      const stats = fs.statSync(this.asnDbPath);
      info.asnDbSize = stats.size;
      info.asnDbModified = stats.mtime;
    }

    return info;
  }
}

module.exports = new MaxMindService();
