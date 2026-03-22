# Развертывание на guestreviews.ru - Краткая инструкция

## Быстрое развертывание (10 минут)

### 1. Подготовка DNS

Убедитесь, что домен указывает на ваш сервер:
```
A     guestreviews.ru      -> YOUR_SERVER_IP
A     www.guestreviews.ru  -> YOUR_SERVER_IP
```

Проверка:
```bash
dig guestreviews.ru +short
# Должен вернуть IP вашего сервера
```

### 2. Подключение к серверу

```bash
ssh root@YOUR_SERVER_IP
```

### 3. Установка Docker (если не установлен)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y
```

### 4. Загрузка проекта

```bash
# Создать директорию
mkdir -p /opt/hotel-reviews
cd /opt/hotel-reviews

# Загрузить файлы (выберите один способ)

# Способ 1: Git
git clone <your-repository-url> .

# Способ 2: SCP с локальной машины
# scp -r ./hotel-guest-reviews/* root@YOUR_SERVER_IP:/opt/hotel-reviews/
```

### 5. Настройка переменных окружения

```bash
# Скопировать шаблон
cp .env.production .env

# Сгенерировать SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Редактировать .env
nano .env
```

**Обязательно измените:**
- `SECRET_KEY` - используйте сгенерированный выше
- `POSTGRES_PASSWORD` - придумайте сильный пароль
- `REDIS_PASSWORD` - придумайте сильный пароль
- `SMTP_USER` и `SMTP_PASSWORD` - для email уведомлений

### 6. Настройка firewall

```bash
apt install ufw -y
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 7. Получение SSL сертификата

```bash
# Изменить email в скрипте
nano scripts/setup_ssl.sh
# Измените: EMAIL="admin@guestreviews.ru"

# Сделать исполняемым
chmod +x scripts/setup_ssl.sh

# Запустить
bash scripts/setup_ssl.sh
```

### 8. Запуск production окружения

```bash
# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f
```

### 9. Инициализация базы данных

```bash
# Применить миграции
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Создать тестовые данные
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py
```

### 10. Проверка работы

Откройте в браузере:
- https://guestreviews.ru
- https://guestreviews.ru/api/v1/docs

Или через curl:
```bash
curl https://guestreviews.ru/health
```

## ✅ Готово!

Ваш сайт теперь доступен по адресу:
- **Главная**: https://guestreviews.ru
- **API документация**: https://guestreviews.ru/api/v1/docs
- **Health check**: https://guestreviews.ru/health

### Тестовые учетные данные

- Владелец: `admin@grandhotel.ru` / `admin123`
- Менеджер: `manager@grandhotel.ru` / `manager123`

## Управление

### Просмотр логов
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Перезапуск
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Остановка
```bash
docker-compose -f docker-compose.prod.yml down
```

### Обновление
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

## Резервное копирование

### Создать бэкап
```bash
mkdir -p /opt/backups
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres hotel_reviews > /opt/backups/backup_$(date +%Y%m%d).sql
```

### Восстановить бэкап
```bash
cat /opt/backups/backup_YYYYMMDD.sql | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres hotel_reviews
```

## Troubleshooting

### Сайт не открывается
```bash
# Проверить DNS
dig guestreviews.ru +short

# Проверить Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Проверить API
docker-compose -f docker-compose.prod.yml logs api
```

### 502 Bad Gateway
```bash
# Перезапустить API
docker-compose -f docker-compose.prod.yml restart api
```

### SSL сертификат не работает
```bash
# Проверить сертификат
openssl s_client -connect guestreviews.ru:443

# Переполучить сертификат
bash scripts/setup_ssl.sh
```

## Следующие шаги

1. ✅ Измените пароли тестовых пользователей
2. ✅ Настройте email уведомления
3. ✅ Настройте автоматические бэкапы
4. ✅ Настройте мониторинг (UptimeRobot, Pingdom)
5. ✅ Настройте интеграции с booking.com, Airbnb

## Полная документация

См. `PRODUCTION_SETUP.md` для подробной информации.

## Поддержка

- Email: support@guestreviews.ru
- Документация: https://guestreviews.ru/api/v1/docs
