# Быстрое развертывание на guestreviews.ru

## Одна команда для развертывания

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/scripts/deploy.sh | bash
```

## Или пошагово (5 команд)

### 1. Подготовка

```bash
# На вашем сервере
mkdir -p /opt/hotel-reviews && cd /opt/hotel-reviews
```

### 2. Загрузка кода

```bash
# Вариант A: Git
git clone <your-repository-url> .

# Вариант B: С локальной машины
# scp -r ./hotel-guest-reviews/* root@YOUR_SERVER_IP:/opt/hotel-reviews/
```

### 3. Настройка

```bash
# Скопировать .env и отредактировать
cp .env.production .env
nano .env  # Измените SECRET_KEY, пароли
```

### 4. SSL сертификат

```bash
# Изменить email и запустить
nano scripts/setup_ssl.sh  # Измените EMAIL
bash scripts/setup_ssl.sh
```

### 5. Запуск

```bash
# Запустить все
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py
```

## Готово! 🎉

Откройте: https://guestreviews.ru/api/v1/docs

---

## Автоматический скрипт

Для полностью автоматического развертывания:

```bash
cd /opt/hotel-reviews
bash scripts/deploy.sh
```

Скрипт автоматически:
- ✅ Установит Docker и Docker Compose
- ✅ Проверит DNS
- ✅ Настроит firewall
- ✅ Получит SSL сертификат
- ✅ Запустит все сервисы
- ✅ Применит миграции
- ✅ Создаст тестовые данные

---

## Минимальные требования

- **Сервер**: 2GB RAM, 2 CPU, 20GB диск
- **ОС**: Ubuntu 20.04+ или Debian 11+
- **DNS**: A-запись guestreviews.ru → IP сервера
- **Порты**: 22, 80, 443 открыты

---

## Проверка после развертывания

```bash
# Health check
curl https://guestreviews.ru/health

# API docs
curl https://guestreviews.ru/api/v1/docs

# Login test
curl -X POST https://guestreviews.ru/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}'
```

---

## Управление

```bash
# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапуск
docker-compose -f docker-compose.prod.yml restart

# Остановка
docker-compose -f docker-compose.prod.yml down

# Обновление
git pull && docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Помощь

Полная документация: [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)

Чеклист: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
