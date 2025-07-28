-- 初始化数据
USE ip_query_system;

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description, is_public) VALUES
('site_name', 'IP查询系统', 'string', '网站名称', TRUE),
('site_description', '专业的IP地址查询服务', 'string', '网站描述', TRUE),
('api_enabled', 'true', 'boolean', 'API服务是否启用', FALSE),
('default_daily_limit', '1000', 'number', '默认每日查询限制', FALSE),
('guest_daily_limit', '20', 'number', '游客每日查询限制', FALSE),
('max_batch_size', '100', 'number', '批量查询最大数量', TRUE),
('cache_ttl', '3600', 'number', '缓存过期时间(秒)', FALSE),
('email_enabled', 'false', 'boolean', '邮件服务是否启用', FALSE),
('smtp_host', '', 'string', 'SMTP服务器地址', FALSE),
('smtp_port', '587', 'number', 'SMTP端口', FALSE),
('smtp_username', '', 'string', 'SMTP用户名', FALSE),
('smtp_password', '', 'string', 'SMTP密码', FALSE),
('smtp_encryption', 'tls', 'string', 'SMTP加密方式', FALSE),
('recaptcha_enabled', 'false', 'boolean', 'reCAPTCHA是否启用', FALSE),
('recaptcha_site_key', '', 'string', 'reCAPTCHA站点密钥', TRUE),
('recaptcha_secret_key', '', 'string', 'reCAPTCHA私钥', FALSE),
('maintenance_mode', 'false', 'boolean', '维护模式', FALSE),
('maintenance_message', '系统维护中，请稍后再试', 'string', '维护模式提示信息', TRUE);

-- 插入默认管理员账号 (密码: admin123)
INSERT INTO admins (id, username, email, password_hash, role, status) VALUES
('admin-001', 'admin', 'admin@example.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'super_admin', 'active');

-- 插入测试用户 (密码: test123)
INSERT INTO users (id, username, email, password_hash, status, email_verified_at, user_type) VALUES
('user-001', 'testuser', 'test@example.com', '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'active', NOW(), 'free');

-- 为测试用户创建API密钥
INSERT INTO api_keys (id, user_id, key_name, api_key, secret_key, allowed_origins, rate_limit_per_minute, rate_limit_per_day, status) VALUES
('key-001', 'user-001', '测试密钥', 'test_api_key_123456789', 'test_secret_key_abcdefghijklmnop', '["*"]', 60, 1000, 'active');

-- 插入一些示例API调用日志
INSERT INTO api_logs (api_key_id, user_id, client_ip, query_ip, user_agent, response_time, status_code, response_data) VALUES
('key-001', 'user-001', '192.168.1.100', '8.8.8.8', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 150, 200, '{"country": "United States", "city": "Mountain View"}'),
('key-001', 'user-001', '192.168.1.100', '114.114.114.114', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 120, 200, '{"country": "China", "city": "Beijing"}'),
('key-001', 'user-001', '192.168.1.100', '1.1.1.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 180, 200, '{"country": "Australia", "city": "Sydney"}');

-- 插入示例登录日志
INSERT INTO user_login_logs (user_id, ip_address, user_agent, login_type, status, location_country, location_city) VALUES
('user-001', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'web', 'success', 'China', 'Beijing'),
('user-001', '192.168.1.101', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)', 'web', 'success', 'China', 'Shanghai');
