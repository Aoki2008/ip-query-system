#!/bin/bash
# 🔒 SSL证书生成脚本
# 用于生成自签名证书或配置Let's Encrypt证书

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SSL_DIR="docker/nginx/ssl"
DOMAIN="ip-query.example.com"
COUNTRY="CN"
STATE="Beijing"
CITY="Beijing"
ORG="IP Query System"
OU="IT Department"

# 创建SSL目录
mkdir -p "$SSL_DIR"

echo -e "${BLUE}🔒 SSL证书生成工具${NC}"
echo "=================================="

# 选择证书类型
echo -e "${YELLOW}请选择证书类型:${NC}"
echo "1) 自签名证书 (开发/测试环境)"
echo "2) Let's Encrypt证书 (生产环境)"
echo "3) 导入现有证书"
read -p "请输入选择 (1-3): " cert_type

case $cert_type in
    1)
        echo -e "${BLUE}📝 生成自签名证书...${NC}"
        
        # 生成私钥
        openssl genrsa -out "$SSL_DIR/key.pem" 2048
        
        # 生成证书签名请求
        openssl req -new -key "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.csr" -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$OU/CN=$DOMAIN"
        
        # 生成自签名证书
        openssl x509 -req -days 365 -in "$SSL_DIR/cert.csr" -signkey "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem"
        
        # 生成证书链（自签名情况下与证书相同）
        cp "$SSL_DIR/cert.pem" "$SSL_DIR/chain.pem"
        
        # 清理临时文件
        rm "$SSL_DIR/cert.csr"
        
        echo -e "${GREEN}✅ 自签名证书生成完成${NC}"
        ;;
        
    2)
        echo -e "${BLUE}🌐 配置Let's Encrypt证书...${NC}"
        
        # 检查certbot是否安装
        if ! command -v certbot &> /dev/null; then
            echo -e "${RED}❌ certbot未安装，请先安装certbot${NC}"
            echo "Ubuntu/Debian: sudo apt install certbot"
            echo "CentOS/RHEL: sudo yum install certbot"
            exit 1
        fi
        
        read -p "请输入域名: " domain
        read -p "请输入邮箱: " email
        
        # 生成Let's Encrypt证书
        certbot certonly --standalone -d "$domain" --email "$email" --agree-tos --non-interactive
        
        # 复制证书到nginx目录
        cp "/etc/letsencrypt/live/$domain/fullchain.pem" "$SSL_DIR/cert.pem"
        cp "/etc/letsencrypt/live/$domain/privkey.pem" "$SSL_DIR/key.pem"
        cp "/etc/letsencrypt/live/$domain/chain.pem" "$SSL_DIR/chain.pem"
        
        echo -e "${GREEN}✅ Let's Encrypt证书配置完成${NC}"
        ;;
        
    3)
        echo -e "${BLUE}📁 导入现有证书...${NC}"
        
        read -p "请输入证书文件路径: " cert_path
        read -p "请输入私钥文件路径: " key_path
        read -p "请输入证书链文件路径 (可选): " chain_path
        
        # 验证文件存在
        if [[ ! -f "$cert_path" ]]; then
            echo -e "${RED}❌ 证书文件不存在: $cert_path${NC}"
            exit 1
        fi
        
        if [[ ! -f "$key_path" ]]; then
            echo -e "${RED}❌ 私钥文件不存在: $key_path${NC}"
            exit 1
        fi
        
        # 复制证书文件
        cp "$cert_path" "$SSL_DIR/cert.pem"
        cp "$key_path" "$SSL_DIR/key.pem"
        
        if [[ -f "$chain_path" ]]; then
            cp "$chain_path" "$SSL_DIR/chain.pem"
        else
            cp "$cert_path" "$SSL_DIR/chain.pem"
        fi
        
        echo -e "${GREEN}✅ 证书导入完成${NC}"
        ;;
        
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

# 生成DH参数（如果不存在）
if [[ ! -f "$SSL_DIR/dhparam.pem" ]]; then
    echo -e "${BLUE}🔐 生成DH参数...${NC}"
    openssl dhparam -out "$SSL_DIR/dhparam.pem" 2048
    echo -e "${GREEN}✅ DH参数生成完成${NC}"
fi

# 设置文件权限
chmod 600 "$SSL_DIR"/*.pem
chmod 755 "$SSL_DIR"

# 验证证书
echo -e "${BLUE}🔍 验证证书...${NC}"
if openssl x509 -in "$SSL_DIR/cert.pem" -text -noout > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 证书验证通过${NC}"
    
    # 显示证书信息
    echo -e "${YELLOW}📋 证书信息:${NC}"
    openssl x509 -in "$SSL_DIR/cert.pem" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)"
else
    echo -e "${RED}❌ 证书验证失败${NC}"
    exit 1
fi

# 创建证书更新脚本
cat > scripts/renew_ssl_cert.sh << 'EOF'
#!/bin/bash
# SSL证书更新脚本

SSL_DIR="docker/nginx/ssl"

# Let's Encrypt证书更新
if [[ -f "/etc/letsencrypt/renewal/*.conf" ]]; then
    echo "🔄 更新Let's Encrypt证书..."
    certbot renew --quiet
    
    # 复制更新后的证书
    for conf in /etc/letsencrypt/renewal/*.conf; do
        domain=$(basename "$conf" .conf)
        if [[ -f "/etc/letsencrypt/live/$domain/fullchain.pem" ]]; then
            cp "/etc/letsencrypt/live/$domain/fullchain.pem" "$SSL_DIR/cert.pem"
            cp "/etc/letsencrypt/live/$domain/privkey.pem" "$SSL_DIR/key.pem"
            cp "/etc/letsencrypt/live/$domain/chain.pem" "$SSL_DIR/chain.pem"
            echo "✅ 证书已更新: $domain"
        fi
    done
    
    # 重启nginx
    docker-compose restart nginx
    echo "✅ Nginx已重启"
fi
EOF

chmod +x scripts/renew_ssl_cert.sh

echo -e "${GREEN}🎉 SSL证书配置完成！${NC}"
echo -e "${YELLOW}📝 下一步操作:${NC}"
echo "1. 更新docker-compose.yml使用SSL配置"
echo "2. 重启服务: docker-compose restart"
echo "3. 访问: https://localhost 或 https://$DOMAIN"
echo "4. 设置定时任务更新证书: crontab -e"
echo "   0 2 * * 0 /path/to/scripts/renew_ssl_cert.sh"
