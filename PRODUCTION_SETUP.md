# Настройка production для guestreviews.ru

## Предварительные требования

1. **Сервер**
   - Ubuntu 20.04+ или Debian 11+
   - Минимум 2GB RAM, 2 CPU cores
   - 20GB свободного места на диске

2. **Домен**
   - Домен guestreviews.ru должен указывать на IP вашего сервера
   - DNS записи:
     ```
     A     guestreviews.ru      -> YOUR_SERVER_IP
     A     www.guestreviews.ru  -> YOUR_SERVER_IP
     ```

3. **Установленное ПО**
   - Docker
   - Docker Compose
   - Git

## Шаг 1: Подготовка сервера

### Подключение к серверу

```bash
ssh root@YOUR_SERVER_IP
```

### Установка Docker

```bash
# Обновить систему
apt update && apt upgrade -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установить Docker Compose
apt install docker-compose -y

# Проверить установку
docker --version
docker-compose --version
```

### Настройка firewall

```bash
# Установить UFW
apt install ufw -y

# Разрешить SSH
ufw allow 22/tcp

# Разрешить HTTP и HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Включить firewall
ufw enable
ufw status
```

## Шаг 2: Клонирование проекта

```bash
# Создать директорию
mkdir -p /opt/hotel-reviews
cd /opt/hotel-reviews

# Клонировать репозиторий
git clone <your-repository-url> .

# Или загрузить файлы через SCP
# scp -r ./hotel-guest-reviews root@YOUR_SERVER_IP:/opt/hotel-reviews/
```

## Шаг 3: Настройка переменных окружения

```bash
# Скопировать шаблон
cp .env.production .env

# Редактировать .env
nano .env
```

### Обязательно измените:

```env
# Сгенерировать SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Установить надежные пароли
POSTGRES_PASSWORD=your_strong_postgres_password_here
REDIS_PASSWORD=your_strong_redis_password_here

# Email для уведомлений
SMTP_USER=noreply@guestreviews.ru
SMTP_PASSWORD=your_email_password
```

## Шаг 4: Получение SSL сертификата

### Проверка DNS

```bash
# Убедитесь, что домен указывает на ваш сервер
dig guestreviews.ru +short
# Должен вернуть IP вашего сервера
```

### Получение сертификата

```bash
# Сделать скрипт исполняемым
chmod +x scripts/setup_ssl.sh

# Изменить email в скрипте
nano scripts/setup_ssl.sh
# Измените: EMAIL="admin@guestreviews.ru"

# Запустить скрипт
bash scripts/setup_ssl.sh
```

Скрипт автоматически:
1. Запустит временный Nginx
2. Получит SSL сертификат от Let's Encrypt
3. Остановит временный Nginx

## Шаг 5: Запуск production окружения

```bash
# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f
```

## Шаг 6: Инициализация базы данных

```bash
# Применить миграции
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Создать первого пользователя
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py
```

## Шаг 7: Проверка работы

### Проверка через браузер

1. Откройте https://guestreviews.ru
2. Должна открыться главная страница API
3. Перейдите на https://guestreviews.ru/api/v1/docs
4. Должна открыться Swagger документация

### Проверка через curl

```bash
# Health check
curl https://guestreviews.ru/health

# API status
curl https://guestreviews.ru/api/v1/status

# Login
curl -X POST https://guestreviews.ru/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}'
```

## Шаг 8: Настройка автоматического обновления SSL

SSL сертификат автоматически обновляется через контейнер certbot.

Проверить:
```bash
docker-compose -f docker-compose.prod.yml logs certbot
```

## Управление системой

### Просмотр логов

```bash
# Все логи
docker-compose -f docker-compose.prod.yml logs -f

# Логи API
docker-compose -f docker-compose.prod.yml logs -f api

# Логи Nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Перезапуск сервисов

```bash
# Перезапустить все
docker-compose -f docker-compose.prod.yml restart

# Перезапустить API
docker-compose -f docker-compose.prod.yml restart api

# Перезапустить Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Остановка системы

```bash
docker-compose -f docker-compose.prod.yml down
```

### Обновление кода

```bash
# Получить обновления
git pull

# Пересобрать и перезапустить
docker-compose -f docker-compose.prod.yml up -d --build
```

## Резервное копирование

### Создание бэкапа базы данных

```bash
# Создать директорию для бэкапов
mkdir -p /opt/backups

# Создать бэкап
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres hotel_reviews > /opt/backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### Автоматические бэкапы (cron)

```bash
# Создать скрипт бэкапа
cat > /opt/hotel-reviews/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cd /opt/hotel-reviews
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres hotel_reviews > $BACKUP_DIR/backup_$DATE.sql
# Удалить бэкапы старше 7 дней
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/hotel-reviews/scripts/backup.sh

# Добавить в cron (каждый день в 3:00)
crontab -e
# Добавить строку:
# 0 3 * * * /opt/hotel-reviews/scripts/backup.sh
```

### Восстановление из бэкапа

```bash
# Остановить API
docker-compose -f docker-compose.prod.yml stop api

# Восстановить базу
cat /opt/backups/backup_YYYYMMDD_HHMMSS.sql | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres hotel_reviews

# Запустить API
docker-compose -f docker-compose.prod.yml start api
```

## Мониторинг

### Проверка использования ресурсов

```bash
# Использование CPU и памяти
docker stats

# Использование диска
df -h

# Логи системы
journalctl -u docker -f
```

### Настройка алертов (опционально)

Рекомендуется настроить:
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry)
- Log aggregation (ELK, Loki)
- Metrics (Prometheus + Grafana)

## Безопасность

### Чеклист безопасности

- [x] HTTPS включен
- [x] Firewall настроен
- [x] Сильные пароли установлены
- [x] DEBUG=false
- [x] CORS настроен правильно
- [ ] Настроить fail2ban
- [ ] Настроить автоматические обновления
- [ ] Настроить мониторинг
- [ ] Настроить алерты

### Дополнительная защита

```bash
# Установить fail2ban
apt install fail2ban -y

# Настроить для SSH
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
```

## Troubleshooting

### Проблема: Сайт не открывается

```bash
# Проверить DNS
dig guestreviews.ru +short

# Проверить Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Проверить SSL сертификат
openssl s_client -connect guestreviews.ru:443 -servername guestreviews.ru
```

### Проблема: 502 Bad Gateway

```bash
# Проверить API
docker-compose -f docker-compose.prod.yml logs api

# Проверить, что API запущен
docker-compose -f docker-compose.prod.yml ps api

# Перезапустить API
docker-compose -f docker-compose.prod.yml restart api
```

### Проблема: База данных не подключается

```bash
# Проверить PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres

# Проверить подключение
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d hotel_reviews -c "SELECT 1"
```

## Контакты и поддержка

- Документация: https://guestreviews.ru/api/v1/docs
- Email: support@guestreviews.ru

## Готово!

Ваша система теперь доступна по адресу:
- https://guestreviews.ru
- https://guestreviews.ru/api/v1/docs

Следующие шаги:
1. Создайте первых пользователей
2. Настройте интеграции
3. Настройте мониторинг
4. Настройте резервное копирование
