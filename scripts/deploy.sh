#!/bin/bash

# Автоматическое развертывание на guestreviews.ru

set -e

echo "=== Развертывание Guest Reviews System на guestreviews.ru ==="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода ошибок
error() {
    echo -e "${RED}❌ Ошибка: $1${NC}"
    exit 1
}

# Функция для вывода успеха
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Функция для вывода предупреждений
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then 
    error "Запустите скрипт от root: sudo bash scripts/deploy.sh"
fi

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    warning "Docker не установлен. Устанавливаю..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    success "Docker установлен"
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    warning "Docker Compose не установлен. Устанавливаю..."
    apt install docker-compose -y
    success "Docker Compose установлен"
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    warning ".env файл не найден. Создаю из шаблона..."
    cp .env.production .env
    
    # Генерация SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    
    warning "ВАЖНО: Отредактируйте .env файл и установите пароли!"
    echo "nano .env"
    read -p "Нажмите Enter после редактирования .env..."
fi

# Проверка DNS
echo ""
echo "Проверка DNS..."
DOMAIN_IP=$(dig +short guestreviews.ru | head -n1)
SERVER_IP=$(curl -s ifconfig.me)

if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    warning "DNS не настроен правильно!"
    echo "Домен guestreviews.ru указывает на: $DOMAIN_IP"
    echo "IP сервера: $SERVER_IP"
    read -p "Продолжить? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    success "DNS настроен правильно"
fi

# Настройка firewall
echo ""
echo "Настройка firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    success "Firewall настроен"
else
    warning "UFW не установлен. Установите вручную: apt install ufw"
fi

# Получение SSL сертификата
echo ""
read -p "Получить SSL сертификат? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -d "certbot/conf/live/guestreviews.ru" ]; then
        echo "Получение SSL сертификата..."
        bash scripts/setup_ssl.sh
        success "SSL сертификат получен"
    else
        success "SSL сертификат уже существует"
    fi
fi

# Запуск production окружения
echo ""
echo "Запуск production окружения..."
docker-compose -f docker-compose.prod.yml up -d

# Ожидание запуска
echo "Ожидание запуска сервисов..."
sleep 10

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Применение миграций
echo ""
echo "Применение миграций базы данных..."
docker-compose -f docker-compose.prod.yml exec -T api alembic upgrade head
success "Миграции применены"

# Инициализация данных
echo ""
read -p "Создать тестовые данные? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.prod.yml exec -T api python scripts/init_db.py
    success "Тестовые данные созданы"
fi

# Проверка работы
echo ""
echo "Проверка работы системы..."
sleep 5

if curl -s -o /dev/null -w "%{http_code}" https://guestreviews.ru/health | grep -q "200"; then
    success "Система работает!"
else
    warning "Система не отвечает. Проверьте логи: docker-compose -f docker-compose.prod.yml logs"
fi

# Итоговая информация
echo ""
echo "=========================================="
success "Развертывание завершено!"
echo "=========================================="
echo ""
echo "Ваш сайт доступен по адресу:"
echo "  🌐 https://guestreviews.ru"
echo "  📚 https://guestreviews.ru/api/v1/docs"
echo ""
echo "Тестовые учетные данные:"
echo "  👤 admin@grandhotel.ru / admin123"
echo "  👤 manager@grandhotel.ru / manager123"
echo ""
echo "Полезные команды:"
echo "  Логи:        docker-compose -f docker-compose.prod.yml logs -f"
echo "  Перезапуск:  docker-compose -f docker-compose.prod.yml restart"
echo "  Остановка:   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "Следующие шаги:"
echo "  1. Измените пароли тестовых пользователей"
echo "  2. Настройте email уведомления в .env"
echo "  3. Настройте автоматические бэкапы"
echo "  4. Настройте мониторинг"
echo ""
