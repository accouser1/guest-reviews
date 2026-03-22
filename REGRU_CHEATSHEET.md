# Шпаргалка по развертыванию на REG.RU

## 🚀 Быстрый старт (копируй-вставляй)

### 1. Получить данные VPS
```
reg.ru → Мои услуги → VPS
IP: _____________
Пароль: _____________
```

### 2. Настроить DNS
```
reg.ru → Домены → guestreviews.ru → DNS

A    @      ВАШ_IP
A    www    ВАШ_IP
```

### 3. Подключиться
```powershell
ssh root@ВАШ_IP
```

### 4. Загрузить проект

**FileZilla:**
```
sftp://ВАШ_IP:22
root / пароль
→ /opt/hotel-reviews/
```

**Или Git:**
```bash
mkdir -p /opt/hotel-reviews
cd /opt/hotel-reviews
git clone URL .
```

### 5. Развернуть
```bash
cd /opt/hotel-reviews
chmod +x scripts/deploy.sh
bash scripts/deploy.sh
```

### 6. Открыть
```
https://guestreviews.ru/api/v1/docs
```

## 📝 Команды для копирования

### Первое подключение
```bash
apt update && apt upgrade -y
apt install -y git curl wget nano
```

### Установка Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y
```

### Firewall
```bash
apt install ufw -y
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Создание проекта
```bash
mkdir -p /opt/hotel-reviews
cd /opt/hotel-reviews
```

### Настройка .env
```bash
cp .env.production .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
nano .env
```

### SSL сертификат
```bash
nano scripts/setup_ssl.sh  # Изменить EMAIL
chmod +x scripts/setup_ssl.sh
bash scripts/setup_ssl.sh
```

### Запуск production
```bash
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py
```

## 🔧 Управление

### Статус
```bash
cd /opt/hotel-reviews
docker-compose -f docker-compose.prod.yml ps
```

### Логи
```bash
docker-compose -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs api
```

### Перезапуск
```bash
docker-compose -f docker-compose.prod.yml restart
docker-compose -f docker-compose.prod.yml restart api
docker-compose -f docker-compose.prod.yml restart nginx
```

### Остановка/Запуск
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Обновление
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

## 💾 Бэкапы

### Создать
```bash
mkdir -p /opt/backups
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U postgres hotel_reviews > /opt/backups/backup_$(date +%Y%m%d).sql
```

### Восстановить
```bash
cat /opt/backups/backup_YYYYMMDD.sql | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres hotel_reviews
```

### Автоматические (cron)
```bash
crontab -e
# Добавить:
0 3 * * * /opt/hotel-reviews/scripts/backup.sh
```

## 🔍 Проверки

### DNS
```bash
dig guestreviews.ru +short
```

### SSL
```bash
openssl s_client -connect guestreviews.ru:443 -servername guestreviews.ru
```

### API
```bash
curl https://guestreviews.ru/health
curl https://guestreviews.ru/api/v1/status
```

### Тест входа
```bash
curl -X POST https://guestreviews.ru/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}'
```

## 🐛 Troubleshooting

### Сайт не открывается
```bash
# Проверить DNS
dig guestreviews.ru +short

# Проверить контейнеры
docker-compose -f docker-compose.prod.yml ps

# Проверить логи
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs api

# Перезапустить
docker-compose -f docker-compose.prod.yml restart
```

### 502 Bad Gateway
```bash
docker-compose -f docker-compose.prod.yml restart api
docker-compose -f docker-compose.prod.yml logs api
```

### SSL не работает
```bash
# Проверить DNS
dig guestreviews.ru +short

# Попробовать еще раз
bash scripts/setup_ssl.sh
```

### База данных
```bash
# Проверить подключение
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U postgres -d hotel_reviews -c "SELECT 1"

# Перезапустить
docker-compose -f docker-compose.prod.yml restart postgres
```

## 📱 Контакты

### REG.RU
- Сайт: https://www.reg.ru/support/
- Телефон: 8 (800) 505-42-85
- Email: support@reg.ru

### Документация
- Быстрый старт: [REGRU_QUICKSTART.md](REGRU_QUICKSTART.md)
- Полная инструкция: [REGRU_SETUP.md](REGRU_SETUP.md)
- Визуальное руководство: [REGRU_VISUAL_GUIDE.md](REGRU_VISUAL_GUIDE.md)
- FAQ: [FAQ.md](FAQ.md)

## 🔑 Тестовые данные

```
Email: admin@grandhotel.ru
Password: admin123

Email: manager@grandhotel.ru
Password: manager123
```

⚠️ Измените после первого входа!

## 📊 Мониторинг

### Использование ресурсов
```bash
docker stats
df -h
free -h
top
```

### Размер логов
```bash
du -sh /var/lib/docker/containers/*/*-json.log
```

### Очистка
```bash
docker system prune -a
```

## 🎯 Быстрые ссылки

- Сайт: https://guestreviews.ru
- API Docs: https://guestreviews.ru/api/v1/docs
- Health: https://guestreviews.ru/health
- Панель REG.RU: https://www.reg.ru/

---

**Сохраните эту шпаргалку!** 📌
