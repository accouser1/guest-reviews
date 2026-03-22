# Инструкция по развертыванию

## Быстрый старт (5 минут)

### Вариант 1: Docker (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd hotel-guest-reviews

# 2. Создать .env файл
copy .env.example .env

# 3. Запустить все сервисы
docker-compose up -d

# 4. Дождаться запуска (проверить логи)
docker-compose logs -f api

# 5. Применить миграции
docker-compose exec api alembic upgrade head

# 6. Инициализировать тестовые данные
docker-compose exec api python scripts/init_db.py

# 7. Открыть документацию API
# http://localhost:8000/api/v1/docs
```

### Вариант 2: Локальная установка

```bash
# 1. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить PostgreSQL и Redis
docker-compose up -d postgres redis

# 4. Создать .env файл
copy .env.example .env

# 5. Применить миграции
alembic upgrade head

# 6. Инициализировать данные
python scripts/init_db.py

# 7. Запустить сервер
uvicorn app.main:app --reload
```

## Проверка работоспособности

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Вход в систему

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}'
```

### 3. Создание тестовой брони

См. файл `examples.sh` или `test_api.http`

## Настройка окружения

### Обязательные переменные

В файле `.env` обязательно измените:

```env
# Безопасность
SECRET_KEY=your-very-long-secret-key-at-least-32-characters

# База данных (если не используете Docker)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Redis (если не используете Docker)
REDIS_URL=redis://host:6379/0
```

### Опциональные настройки

```env
# Email уведомления
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# CORS для фронтенда
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Производственное развертывание

### 1. Подготовка

```bash
# Изменить окружение
ENVIRONMENT=production
DEBUG=false

# Сгенерировать безопасный SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. База данных

```bash
# Создать базу данных
createdb hotel_reviews

# Применить миграции
alembic upgrade head

# Создать первого пользователя
python scripts/init_db.py
```

### 3. Запуск с Gunicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 4. Nginx (reverse proxy)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. Systemd Service

Создать `/etc/systemd/system/hotel-reviews.service`:

```ini
[Unit]
Description=Hotel Guest Review System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/hotel-reviews
Environment="PATH=/opt/hotel-reviews/venv/bin"
ExecStart=/opt/hotel-reviews/venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Запустить:
```bash
sudo systemctl enable hotel-reviews
sudo systemctl start hotel-reviews
sudo systemctl status hotel-reviews
```

## Мониторинг

### Логи

```bash
# Docker
docker-compose logs -f api

# Systemd
sudo journalctl -u hotel-reviews -f
```

### Метрики

Рекомендуется добавить:
- Prometheus для метрик
- Grafana для визуализации
- Sentry для отслеживания ошибок

## Резервное копирование

### База данных

```bash
# Создать бэкап
pg_dump hotel_reviews > backup_$(date +%Y%m%d).sql

# Восстановить
psql hotel_reviews < backup_20260322.sql
```

### Redis

```bash
# Создать снимок
docker-compose exec redis redis-cli BGSAVE

# Файл сохранится в /data/dump.rdb
```

## Обновление

```bash
# 1. Остановить сервис
docker-compose down
# или
sudo systemctl stop hotel-reviews

# 2. Получить обновления
git pull

# 3. Применить миграции
alembic upgrade head

# 4. Перезапустить
docker-compose up -d
# или
sudo systemctl start hotel-reviews
```

## Устранение неполадок

### База данных не подключается

```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Проверить логи
docker-compose logs postgres

# Проверить подключение
docker-compose exec postgres psql -U postgres -d hotel_reviews
```

### Redis не работает

```bash
# Проверить статус
docker-compose ps redis

# Проверить подключение
docker-compose exec redis redis-cli ping
```

### API не отвечает

```bash
# Проверить логи
docker-compose logs api

# Проверить порты
netstat -tulpn | grep 8000

# Перезапустить
docker-compose restart api
```

## Безопасность

### Чеклист

- [ ] Изменен SECRET_KEY
- [ ] DEBUG=false в продакшене
- [ ] Настроен CORS
- [ ] Используется HTTPS
- [ ] Настроен firewall
- [ ] Регулярные бэкапы
- [ ] Мониторинг логов
- [ ] Rate limiting включен

## Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь, что все сервисы запущены
3. Проверьте переменные окружения
4. Обратитесь к документации API
