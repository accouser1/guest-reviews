# Развертывание на REG.RU

## Типы хостинга REG.RU

REG.RU предлагает несколько типов хостинга. Для нашего проекта подходят:

1. **VPS/VDS** (рекомендуется) - полный контроль, Docker поддерживается
2. **Облачный хостинг** - масштабируемое решение
3. **Виртуальный хостинг** - не подходит (нет Docker, нет root доступа)

## Вариант 1: VPS/VDS на REG.RU (рекомендуется)

### Шаг 1: Настройка VPS

1. Войдите в панель управления REG.RU
2. Перейдите в раздел "VPS"
3. Выберите ваш VPS сервер
4. Запишите:
   - IP адрес сервера
   - Логин (обычно root)
   - Пароль (из письма или панели)

### Шаг 2: Настройка DNS

1. В панели REG.RU перейдите в "Домены"
2. Выберите домен guestreviews.ru
3. Перейдите в "Управление DNS"
4. Добавьте/измените записи:

```
Тип    Имя                  Значение
A      @                    ВАШ_IP_VPS
A      www                  ВАШ_IP_VPS
```

5. Сохраните изменения
6. Подождите 5-30 минут для применения DNS

### Шаг 3: Подключение к VPS

#### Windows (PowerShell или PuTTY)

```powershell
# PowerShell
ssh root@ВАШ_IP_VPS

# Или используйте PuTTY:
# Host: ВАШ_IP_VPS
# Port: 22
# Username: root
```

#### Первое подключение

```bash
# Обновить систему
apt update && apt upgrade -y

# Установить необходимые пакеты
apt install -y git curl wget nano
```

### Шаг 4: Загрузка проекта

```bash
# Создать директорию
mkdir -p /opt/hotel-reviews
cd /opt/hotel-reviews

# Вариант A: Загрузить через Git (если код в репозитории)
git clone https://github.com/YOUR_USERNAME/hotel-guest-reviews.git .

# Вариант B: Загрузить с локального компьютера через SCP
# На вашем компьютере (Windows PowerShell):
# scp -r C:\path\to\hotel-guest-reviews\* root@ВАШ_IP_VPS:/opt/hotel-reviews/

# Вариант C: Загрузить через FTP/SFTP (FileZilla)
# Host: sftp://ВАШ_IP_VPS
# Username: root
# Password: ваш_пароль
# Port: 22
```

### Шаг 5: Автоматическое развертывание

```bash
cd /opt/hotel-reviews

# Сделать скрипт исполняемым
chmod +x scripts/deploy.sh

# Запустить автоматическое развертывание
bash scripts/deploy.sh
```

Скрипт автоматически:
- Установит Docker и Docker Compose
- Проверит DNS
- Настроит firewall
- Получит SSL сертификат
- Запустит все сервисы
- Применит миграции
- Создаст тестовые данные

### Шаг 6: Проверка

Откройте в браузере:
- https://guestreviews.ru
- https://guestreviews.ru/api/v1/docs

## Вариант 2: Ручная настройка на VPS REG.RU

Если автоматический скрипт не сработал, выполните вручную:

### 1. Установка Docker

```bash
# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Установить Docker Compose
apt install docker-compose -y

# Проверить установку
docker --version
docker-compose --version
```

### 2. Настройка firewall

```bash
# Установить UFW
apt install ufw -y

# Разрешить необходимые порты
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS

# Включить firewall
ufw enable

# Проверить статус
ufw status
```

### 3. Настройка переменных окружения

```bash
cd /opt/hotel-reviews

# Скопировать шаблон
cp .env.production .env

# Сгенерировать SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Редактировать .env
nano .env
```

Измените в .env:
```env
SECRET_KEY=<вставьте сгенерированный ключ>
POSTGRES_PASSWORD=<придумайте сильный пароль>
REDIS_PASSWORD=<придумайте сильный пароль>
SMTP_USER=noreply@guestreviews.ru
SMTP_PASSWORD=<пароль от email>
```

Сохраните: Ctrl+O, Enter, Ctrl+X

### 4. Получение SSL сертификата

```bash
# Изменить email в скрипте
nano scripts/setup_ssl.sh
# Измените строку: EMAIL="admin@guestreviews.ru"

# Сделать исполняемым
chmod +x scripts/setup_ssl.sh

# Запустить
bash scripts/setup_ssl.sh
```

### 5. Запуск production окружения

```bash
# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f
```

### 6. Инициализация базы данных

```bash
# Применить миграции
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Создать тестовые данные
docker-compose -f docker-compose.prod.yml exec api python scripts/init_db.py
```

## Вариант 3: Облачный хостинг REG.RU

Если у вас облачный хостинг REG.RU:

1. Создайте виртуальную машину в панели управления
2. Выберите Ubuntu 20.04 или 22.04
3. Следуйте инструкциям для VPS выше

## Особенности REG.RU

### Панель управления ISPmanager

Если у вас есть ISPmanager:

1. **Добавление домена**:
   - Веб-сайты → Создать → WWW-домен
   - Имя: guestreviews.ru
   - IP: выберите IP сервера

2. **Настройка DNS**:
   - Домены → guestreviews.ru → DNS
   - Добавьте A-записи как указано выше

3. **SSL сертификат**:
   - Можно использовать встроенный Let's Encrypt
   - Или использовать наш скрипт setup_ssl.sh

### Firewall в панели REG.RU

Если firewall управляется через панель:

1. Перейдите в "Безопасность" → "Firewall"
2. Разрешите порты:
   - 22 (SSH)
   - 80 (HTTP)
   - 443 (HTTPS)

## Загрузка файлов на REG.RU

### Способ 1: Git (рекомендуется)

```bash
cd /opt/hotel-reviews
git clone https://github.com/YOUR_USERNAME/hotel-guest-reviews.git .
```

### Способ 2: SCP с Windows

```powershell
# В PowerShell на вашем компьютере
scp -r C:\path\to\hotel-guest-reviews\* root@ВАШ_IP_VPS:/opt/hotel-reviews/
```

### Способ 3: FileZilla (SFTP)

1. Скачайте FileZilla: https://filezilla-project.org/
2. Подключитесь:
   - Хост: sftp://ВАШ_IP_VPS
   - Имя пользователя: root
   - Пароль: ваш_пароль
   - Порт: 22
3. Загрузите все файлы в /opt/hotel-reviews/

### Способ 4: Через панель ISPmanager

1. Файловый менеджер → /opt/hotel-reviews/
2. Загрузите файлы через веб-интерфейс
3. Или используйте встроенный FTP

## Проверка DNS

```bash
# На сервере или локально
dig guestreviews.ru +short

# Должен вернуть IP вашего VPS
```

Если DNS не обновился:
- Подождите 5-30 минут
- Очистите DNS кеш на компьютере:
  ```powershell
  # Windows
  ipconfig /flushdns
  ```

## Управление сайтом

### Просмотр логов

```bash
cd /opt/hotel-reviews
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

### Автоматические бэкапы

```bash
# Создать скрипт
cat > /opt/hotel-reviews/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cd /opt/hotel-reviews
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres hotel_reviews > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/hotel-reviews/scripts/backup.sh

# Добавить в cron (каждый день в 3:00)
crontab -e
# Добавить строку:
# 0 3 * * * /opt/hotel-reviews/scripts/backup.sh
```

## Troubleshooting

### Проблема: Не могу подключиться по SSH

1. Проверьте IP адрес в панели REG.RU
2. Проверьте, что порт 22 открыт
3. Попробуйте сбросить пароль в панели управления

### Проблема: DNS не обновляется

1. Проверьте настройки DNS в панели REG.RU
2. Подождите до 30 минут
3. Проверьте через: https://www.whatsmydns.net/

### Проблема: SSL сертификат не получается

1. Убедитесь, что DNS настроен правильно
2. Проверьте, что порты 80 и 443 открыты
3. Попробуйте еще раз через 10 минут

### Проблема: Сайт не открывается

```bash
# Проверить статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Проверить логи
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs api

# Перезапустить
docker-compose -f docker-compose.prod.yml restart
```

## Поддержка REG.RU

- Техподдержка: https://www.reg.ru/support/
- Телефон: 8 (800) 505-42-85
- Email: support@reg.ru
- Документация: https://help.reg.ru/

## Готово! 🎉

Ваш сайт теперь доступен:
- https://guestreviews.ru
- https://guestreviews.ru/api/v1/docs

Тестовые учетные данные:
- admin@grandhotel.ru / admin123
- manager@grandhotel.ru / manager123

## Следующие шаги

1. ✅ Измените пароли тестовых пользователей
2. ✅ Настройте email уведомления
3. ✅ Настройте автоматические бэкапы
4. ✅ Настройте мониторинг
5. ✅ Добавьте свой отель и пользователей
