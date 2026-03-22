#!/bin/bash

# Script to setup SSL certificate for guestreviews.ru

set -e

DOMAIN="guestreviews.ru"
EMAIL="admin@guestreviews.ru"  # Измените на ваш email

echo "=== Настройка SSL сертификата для $DOMAIN ==="

# Создать директории
mkdir -p certbot/conf
mkdir -p certbot/www

# Временная конфигурация Nginx для получения сертификата
cat > nginx/temp.conf << 'EOF'
server {
    listen 80;
    server_name guestreviews.ru www.guestreviews.ru;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 "OK";
    }
}
EOF

echo "1. Запуск временного Nginx..."
docker run -d --name temp_nginx \
    -p 80:80 \
    -v $(pwd)/nginx/temp.conf:/etc/nginx/conf.d/default.conf \
    -v $(pwd)/certbot/www:/var/www/certbot \
    nginx:alpine

sleep 5

echo "2. Получение SSL сертификата от Let's Encrypt..."
docker run --rm \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    -v $(pwd)/certbot/www:/var/www/certbot \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo "3. Остановка временного Nginx..."
docker stop temp_nginx
docker rm temp_nginx

echo "✅ SSL сертификат успешно получен!"
echo ""
echo "Теперь можно запустить production окружение:"
echo "docker-compose -f docker-compose.prod.yml up -d"
