# Настройка домена guestreviews.ru - Краткая сводка

## ✅ Что создано для production

### Конфигурационные файлы

1. **Dockerfile.prod** - Production Docker образ
   - Gunicorn с 4 workers
   - Uvicorn worker class
   - Health check
   - Non-root пользователь

2. **docker-compose.prod.yml** - Production окружение
   - PostgreSQL с persistent storage
   - Redis с паролем
   - FastAPI с Gunicorn
   - Nginx reverse proxy
   - Certbot для SSL

3. **nginx/guestreviews.ru.conf** - Nginx конфигурация
   - HTTP → HTTPS редирект
   - SSL/TLS настройки
   - Security headers
   - Proxy к FastAPI
   - Static files

4. **.env.production** - Шаблон переменных окружения
   - Production настройки
   - Безопасные значения по умолчанию
   - Комментарии для каждой переменной

### Скрипты развертывания

1. **scripts/setup_ssl.sh** - Получение SSL сертификата
   - Автоматическое получение от Let's Encrypt
   - Поддержка www поддомена
   - Временный Nginx для challenge

2. **scripts/deploy.sh** - Полное автоматическое развертывание
   - Проверка зависимостей
   - Установка Docker
   - Проверка DNS
   - Настройка firewall
   - Получение SSL
   - Запуск сервисов
   - Применение миграций

### Документация

1. **PRODUCTION_SETUP.md** - Полное руководство (подробное)
2. **DEPLOY_GUESTREVIEWS_RU.md** - Краткая инструкция (10 минут)
3. **DEPLOYMENT_CHECKLIST.md** - Чеклист для проверки
4. **QUICK_DEPLOY.md** - Быстрое развертывание (5 команд)

## 🚀 Как развернуть

### Вариант 1: Автоматический (рекомендуется)

```bash
# На сервере
cd /opt/hotel-reviews
bash scripts/deploy.sh
```

### Вариант 2: Пошаговый

```bash
# 1. Настроить .env
cp .env.production .env
nano .env  # Изменить SECRET_KEY, пароли

# 2. Получить SSL
bash scripts/setup_ssl.sh

# 3. Запустить
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py
```

## 🌐 Результат

После развертывания сайт будет доступен:

- **Главная**: https://guestreviews.ru
- **API документация**: https://guestreviews.ru/api/v1/docs
- **Health check**: https://guestreviews.ru/health

### Особенности

✅ HTTPS с автоматическим обновлением сертификата
✅ HTTP автоматически редиректит на HTTPS
✅ www.guestreviews.ru работает
✅ Security headers настроены
✅ Gunicorn с 4 workers для production
✅ PostgreSQL и Redis с persistent storage
✅ Автоматические health checks
✅ Логирование всех запросов

## 📋 Требования

### DNS настройки

```
A     guestreviews.ru      → YOUR_SERVER_IP
A     www.guestreviews.ru  → YOUR_SERVER_IP
```

Проверка:
```bash
dig guestreviews.ru +short
```

### Сервер

- Ubuntu 20.04+ или Debian 11+
- Минимум 2GB RAM, 2 CPU cores
- 20GB свободного места
- Открытые порты: 22, 80, 443

### Обязательно изменить в .env

```env
SECRET_KEY=<сгенерировать 32+ символов>
POSTGRES_PASSWORD=<сильный пароль>
REDIS_PASSWORD=<сильный пароль>
SMTP_USER=noreply@guestreviews.ru
SMTP_PASSWORD=<пароль от email>
```

## 🔐 Безопасность

### Что настроено

- ✅ HTTPS с TLS 1.2+
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Firewall (UFW)
- ✅ Non-root пользователь в контейнере
- ✅ Пароли для PostgreSQL и Redis
- ✅ CORS настроен только для домена
- ✅ Rate limiting (60 req/min)

### Рекомендуется добавить

- [ ] fail2ban для защиты SSH
- [ ] Автоматические обновления безопасности
- [ ] Мониторинг (UptimeRobot, Pingdom)
- [ ] Backup стратегия

## 📊 Мониторинг

### Проверка статуса

```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Использование ресурсов
docker stats
```

### Health checks

```bash
# API health
curl https://guestreviews.ru/health

# SSL сертификат
openssl s_client -connect guestreviews.ru:443 -servername guestreviews.ru
```

## 💾 Резервное копирование

### Создать бэкап

```bash
mkdir -p /opt/backups
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres hotel_reviews > /opt/backups/backup_$(date +%Y%m%d).sql
```

### Автоматические бэкапы (cron)

```bash
# Каждый день в 3:00
0 3 * * * /opt/hotel-reviews/scripts/backup.sh
```

## 🔄 Обновление

```bash
# Получить обновления
git pull

# Пересобрать и перезапустить
docker-compose -f docker-compose.prod.yml up -d --build

# Применить миграции
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## 📞 Поддержка

### Документация

- Полная инструкция: [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)
- Быстрый старт: [DEPLOY_GUESTREVIEWS_RU.md](DEPLOY_GUESTREVIEWS_RU.md)
- Чеклист: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- FAQ: [FAQ.md](FAQ.md)

### Troubleshooting

Если что-то не работает:
1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs`
2. Проверьте DNS: `dig guestreviews.ru +short`
3. Проверьте SSL: `openssl s_client -connect guestreviews.ru:443`
4. См. раздел Troubleshooting в PRODUCTION_SETUP.md

## ✨ Готово!

Система полностью готова к работе на домене https://guestreviews.ru с:
- ✅ Автоматическим SSL
- ✅ Production конфигурацией
- ✅ Безопасными настройками
- ✅ Мониторингом и логированием
- ✅ Полной документацией
