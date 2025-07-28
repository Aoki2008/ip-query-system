# 使用官方PHP镜像
FROM php:8.1-fpm-alpine

# 设置工作目录
WORKDIR /var/www/html

# 安装系统依赖
RUN apk add --no-cache \
    nginx \
    supervisor \
    curl \
    wget \
    zip \
    unzip \
    git \
    libpng-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    libzip-dev \
    icu-dev \
    oniguruma-dev \
    && rm -rf /var/cache/apk/*

# 安装PHP扩展
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
        pdo_mysql \
        mysqli \
        gd \
        zip \
        intl \
        mbstring \
        bcmath \
        opcache

# 安装Redis扩展
RUN pecl install redis \
    && docker-php-ext-enable redis

# 安装Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# 复制应用代码
COPY . .

# 安装PHP依赖
RUN composer install --no-dev --optimize-autoloader --no-interaction

# 设置权限
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html/storage \
    && chmod -R 755 /var/www/html/bootstrap/cache

# 复制配置文件
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/php.ini /usr/local/etc/php/php.ini
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 创建必要的目录
RUN mkdir -p /var/log/supervisor \
    && mkdir -p /var/log/nginx \
    && mkdir -p /run/nginx

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# 启动supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
