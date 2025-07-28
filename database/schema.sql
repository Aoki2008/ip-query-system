-- IP查询系统数据库结构
-- 创建时间: 2024-07-28

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ip_query_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE ip_query_system;

-- 用户表
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status ENUM('active', 'disabled', 'pending') DEFAULT 'pending',
    email_verified_at TIMESTAMP NULL,
    daily_limit INT DEFAULT 1000,
    user_type ENUM('free', 'premium', 'enterprise') DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_status (status)
);

-- API密钥表
CREATE TABLE api_keys (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    key_name VARCHAR(64) NOT NULL,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    secret_key VARCHAR(128) NOT NULL,
    allowed_origins JSON,
    rate_limit_per_minute INT DEFAULT 60,
    rate_limit_per_day INT DEFAULT 1000,
    status ENUM('active', 'disabled', 'expired') DEFAULT 'active',
    expires_at TIMESTAMP NULL,
    last_used_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_api_key (api_key),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- API调用日志表
CREATE TABLE api_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    api_key_id CHAR(36),
    user_id CHAR(36),
    client_ip VARCHAR(45) NOT NULL,
    query_ip VARCHAR(45) NOT NULL,
    user_agent TEXT,
    referer VARCHAR(500),
    response_time INT, -- 毫秒
    status_code SMALLINT NOT NULL,
    error_message TEXT,
    response_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_api_key_id (api_key_id),
    INDEX idx_user_id (user_id),
    INDEX idx_client_ip (client_ip),
    INDEX idx_query_ip (query_ip),
    INDEX idx_created_at (created_at),
    INDEX idx_status_code (status_code)
);

-- 用户登录日志表
CREATE TABLE user_login_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    login_type ENUM('web', 'api') DEFAULT 'web',
    status ENUM('success', 'failed') NOT NULL,
    failure_reason VARCHAR(255),
    location_country VARCHAR(100),
    location_city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_ip_address (ip_address),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
);

-- 系统配置表
CREATE TABLE system_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key),
    INDEX idx_is_public (is_public)
);

-- 管理员表
CREATE TABLE admins (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'admin', 'operator') DEFAULT 'operator',
    status ENUM('active', 'disabled') DEFAULT 'active',
    last_login_at TIMESTAMP NULL,
    last_login_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- 管理员操作日志表
CREATE TABLE admin_operation_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    admin_id CHAR(36) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    operation_desc TEXT,
    target_type VARCHAR(50), -- user, api_key, config等
    target_id VARCHAR(100),
    old_data JSON,
    new_data JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE,
    INDEX idx_admin_id (admin_id),
    INDEX idx_operation_type (operation_type),
    INDEX idx_target_type (target_type),
    INDEX idx_created_at (created_at)
);

-- 邮件队列表
CREATE TABLE email_queue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    to_email VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    template_name VARCHAR(100),
    template_data JSON,
    priority TINYINT DEFAULT 5, -- 1-10, 1最高
    status ENUM('pending', 'sending', 'sent', 'failed') DEFAULT 'pending',
    attempts TINYINT DEFAULT 0,
    max_attempts TINYINT DEFAULT 3,
    error_message TEXT,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_scheduled_at (scheduled_at),
    INDEX idx_priority (priority)
);

-- 创建视图：API使用统计
CREATE VIEW api_usage_stats AS
SELECT
    ak.id as api_key_id,
    ak.key_name,
    u.username,
    u.email,
    COUNT(al.id) as total_requests,
    COUNT(CASE WHEN al.status_code = 200 THEN 1 END) as success_requests,
    COUNT(CASE WHEN al.status_code != 200 THEN 1 END) as error_requests,
    AVG(al.response_time) as avg_response_time,
    MAX(al.created_at) as last_request_at,
    DATE(al.created_at) as request_date
FROM api_keys ak
LEFT JOIN users u ON ak.user_id = u.id
LEFT JOIN api_logs al ON ak.id = al.api_key_id
GROUP BY ak.id, DATE(al.created_at);

-- 创建存储过程：清理过期日志
DELIMITER //
CREATE PROCEDURE CleanupOldLogs(IN days_to_keep INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 删除过期的API调用日志
    DELETE FROM api_logs
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);

    -- 删除过期的登录日志
    DELETE FROM user_login_logs
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);

    -- 删除过期的管理员操作日志
    DELETE FROM admin_operation_logs
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);

    -- 删除过期的邮件队列记录
    DELETE FROM email_queue
    WHERE status IN ('sent', 'failed')
    AND created_at < DATE_SUB(NOW(), INTERVAL days_to_keep DAY);

    COMMIT;
END //
DELIMITER ;

-- 创建触发器：更新API密钥最后使用时间
DELIMITER //
CREATE TRIGGER update_api_key_last_used
    AFTER INSERT ON api_logs
    FOR EACH ROW
BEGIN
    UPDATE api_keys
    SET last_used_at = NEW.created_at
    WHERE id = NEW.api_key_id;
END //
DELIMITER ;
