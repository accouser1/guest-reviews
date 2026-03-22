# Визуальное руководство по развертыванию на REG.RU

## 📋 Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Панель REG.RU                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Домен      │  │   VPS/VDS    │  │     DNS      │     │
│  │ guestreviews │  │  IP: X.X.X.X │  │  A-записи    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              2. Подключение к серверу (SSH)                 │
│                                                              │
│  Windows → PowerShell/PuTTY → ssh root@IP                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              3. Загрузка проекта на сервер                  │
│                                                              │
│  Git / FileZilla / SCP → /opt/hotel-reviews/               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           4. Автоматическое развертывание                   │
│                                                              │
│  bash scripts/deploy.sh                                     │
│    ├─ Установка Docker                                      │
│    ├─ Настройка firewall                                    │
│    ├─ Получение SSL                                         │
│    ├─ Запуск сервисов                                       │
│    └─ Инициализация БД                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  5. Готово! 🎉                              │
│                                                              │
│  https://guestreviews.ru                                    │
│  https://guestreviews.ru/api/v1/docs                        │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Шаг 1: Панель REG.RU

### Где найти IP адрес VPS

```
reg.ru → Войти → Мои услуги → VPS
┌────────────────────────────────────────┐
│ VPS-сервер #12345                      │
│                                        │
│ IP адрес: 123.45.67.89  ← ЗАПИШИТЕ    │
│ Логин: root                            │
│ Пароль: ******** (показать)           │
│                                        │
│ [Управление] [Перезагрузка]           │
└────────────────────────────────────────┘
```

### Настройка DNS

```
reg.ru → Домены → guestreviews.ru → Управление DNS
┌────────────────────────────────────────────────────┐
│ DNS-записи для guestreviews.ru                     │
│                                                     │
│ [Добавить запись]                                  │
│                                                     │
│ Тип: A    Имя: @      Значение: 123.45.67.89     │
│ Тип: A    Имя: www    Значение: 123.45.67.89     │
│                                                     │
│ [Сохранить изменения]                              │
└────────────────────────────────────────────────────┘
```

## 🔌 Шаг 2: Подключение к серверу

### Windows PowerShell

```powershell
# Нажмите Win+X → Windows PowerShell

PS C:\Users\User> ssh root@123.45.67.89
The authenticity of host '123.45.67.89' can't be established.
Are you sure you want to continue connecting (yes/no)? yes

root@123.45.67.89's password: ********

Welcome to Ubuntu 22.04 LTS
root@vps12345:~#  ← ВЫ ПОДКЛЮЧЕНЫ!
```

### PuTTY (альтернатива)

```
┌─────────────────────────────────────┐
│ PuTTY Configuration                 │
│                                     │
│ Host Name: 123.45.67.89            │
│ Port: 22                            │
│ Connection type: SSH                │
│                                     │
│ [Open]                              │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ login as: root                      │
│ password: ********                  │
│                                     │
│ root@vps12345:~#                   │
└─────────────────────────────────────┘
```

## 📦 Шаг 3: Загрузка проекта

### Вариант A: FileZilla (самый простой)

```
1. Скачать FileZilla
   https://filezilla-project.org/

2. Подключиться
┌──────────────────────────────────────────────────┐
│ Хост: sftp://123.45.67.89                       │
│ Имя пользователя: root                          │
│ Пароль: ********                                 │
│ Порт: 22                                         │
│                                                  │
│ [Быстрое соединение]                            │
└──────────────────────────────────────────────────┘

3. Создать папку на сервере
   Правая панель → /opt/ → Правый клик → 
   Создать каталог → hotel-reviews

4. Загрузить файлы
   Левая панель: ваш компьютер
   Правая панель: /opt/hotel-reviews/
   
   Перетащите все файлы слева направо →
```

### Вариант B: Git

```bash
root@vps12345:~# mkdir -p /opt/hotel-reviews
root@vps12345:~# cd /opt/hotel-reviews
root@vps12345:/opt/hotel-reviews# git clone https://github.com/YOUR/repo.git .
```

## 🚀 Шаг 4: Развертывание

### Запуск автоматического скрипта

```bash
root@vps12345:~# cd /opt/hotel-reviews
root@vps12345:/opt/hotel-reviews# chmod +x scripts/deploy.sh
root@vps12345:/opt/hotel-reviews# bash scripts/deploy.sh

=== Развертывание Guest Reviews System на guestreviews.ru ===

✅ Docker установлен
✅ Docker Compose установлен
⚠️  .env файл не найден. Создаю из шаблона...

ВАЖНО: Отредактируйте .env файл и установите пароли!
nano .env
Нажмите Enter после редактирования .env...
```

### Редактирование .env

```bash
# Откроется редактор nano
┌────────────────────────────────────────────────────┐
│ GNU nano 6.2        .env                           │
│                                                     │
│ SECRET_KEY=CHANGE_THIS... ← ИЗМЕНИТЕ               │
│ POSTGRES_PASSWORD=CHANGE_THIS... ← ИЗМЕНИТЕ        │
│ REDIS_PASSWORD=CHANGE_THIS... ← ИЗМЕНИТЕ           │
│                                                     │
│ ^O Сохранить  ^X Выход                             │
└────────────────────────────────────────────────────┘

1. Измените пароли
2. Нажмите Ctrl+O (сохранить)
3. Нажмите Enter
4. Нажмите Ctrl+X (выход)
```

### Продолжение развертывания

```bash
Проверка DNS...
✅ DNS настроен правильно

Настройка firewall...
✅ Firewall настроен

Получить SSL сертификат? (y/n) y  ← ВВЕДИТЕ y

Получение SSL сертификата...
✅ SSL сертификат получен

Запуск production окружения...
✅ Сервисы запущены

Применение миграций базы данных...
✅ Миграции применены

Создать тестовые данные? (y/n) y  ← ВВЕДИТЕ y
✅ Тестовые данные созданы

==========================================
✅ Развертывание завершено!
==========================================

Ваш сайт доступен по адресу:
  🌐 https://guestreviews.ru
  📚 https://guestreviews.ru/api/v1/docs
```

## ✅ Шаг 5: Проверка

### Откройте в браузере

```
1. https://guestreviews.ru
   ┌────────────────────────────────────┐
   │ 🔒 guestreviews.ru                │
   │                                    │
   │ {                                  │
   │   "message": "Hotel Guest Review   │
   │              System API",          │
   │   "version": "1.0.0",              │
   │   "docs": "/api/v1/docs"           │
   │ }                                  │
   └────────────────────────────────────┘

2. https://guestreviews.ru/api/v1/docs
   ┌────────────────────────────────────┐
   │ 🔒 guestreviews.ru/api/v1/docs    │
   │                                    │
   │ Guest Reviews System API           │
   │                                    │
   │ [Authorize]                        │
   │                                    │
   │ ▼ authentication                   │
   │   POST /api/v1/auth/login          │
   │   POST /api/v1/auth/register       │
   │                                    │
   │ ▼ bookings                         │
   │   POST /api/v1/bookings/           │
   │   GET  /api/v1/bookings/{id}       │
   └────────────────────────────────────┘
```

## 🎉 Готово!

Ваш сайт работает на https://guestreviews.ru

### Войдите в систему

```
1. Откройте https://guestreviews.ru/api/v1/docs
2. Найдите POST /api/v1/auth/login
3. Нажмите "Try it out"
4. Введите:
   {
     "email": "admin@grandhotel.ru",
     "password": "admin123"
   }
5. Нажмите "Execute"
6. Скопируйте access_token
7. Нажмите "Authorize" вверху
8. Вставьте токен
9. Теперь можете использовать все API!
```

## 🔧 Управление

### Полезные команды

```bash
# Перейти в папку проекта
cd /opt/hotel-reviews

# Посмотреть статус
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапустить
docker-compose -f docker-compose.prod.yml restart

# Остановить
docker-compose -f docker-compose.prod.yml down

# Запустить снова
docker-compose -f docker-compose.prod.yml up -d
```

## ❓ Проблемы?

### Сайт не открывается

```bash
# 1. Проверить DNS
dig guestreviews.ru +short
# Должен вернуть IP вашего VPS

# 2. Проверить статус
docker-compose -f docker-compose.prod.yml ps
# Все должны быть "Up"

# 3. Проверить логи
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs api
```

### SSL не работает

```bash
# Попробовать еще раз
cd /opt/hotel-reviews
bash scripts/setup_ssl.sh
```

## 📞 Помощь

- **REG.RU**: 8 (800) 505-42-85
- **Документация**: [REGRU_SETUP.md](REGRU_SETUP.md)
- **FAQ**: [FAQ.md](FAQ.md)
