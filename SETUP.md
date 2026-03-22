# Быстрый старт системы проверки гостей

## Описание системы

Система автоматической проверки гостей для отелей. При поступлении новой брони:
1. Автоматически создается запись
2. Находится или создается профиль гостя
3. Собирается история отзывов и инцидентов
4. Рассчитывается риск-скоринг
5. Возвращается решение: заселить, заселить с депозитом или отклонить

## Запуск через Docker (рекомендуется)

```bash
# 1. Скопировать .env файл
copy .env.example .env

# 2. Запустить все сервисы
docker-compose up -d

# 3. Применить миграции
docker-compose exec api alembic upgrade head

# 4. Инициализировать тестовые данные
docker-compose exec api python scripts/init_db.py
```

API будет доступен на http://localhost:8000

## Запуск локально

```bash
# 1. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Скопировать .env
copy .env.example .env

# 4. Запустить PostgreSQL и Redis (через Docker)
docker-compose up -d postgres redis

# 5. Применить миграции
alembic upgrade head

# 6. Инициализировать данные
python scripts/init_db.py

# 7. Запустить сервер
uvicorn app.main:app --reload
```

## Тестовые учетные данные

После инициализации базы данных:

- **Владелец отеля**: admin@grandhotel.ru / admin123
- **Менеджер**: manager@grandhotel.ru / manager123

## Основные API endpoints

### Авторизация
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/register` - Регистрация

### Бронирования
- `POST /api/v1/bookings/` - Создать бронь (с автоматической проверкой)
- `GET /api/v1/bookings/{id}` - Получить детали брони
- `GET /api/v1/bookings/` - Список броней

### Гости
- `GET /api/v1/guests/{id}` - Профиль гостя со статистикой
- `GET /api/v1/guests/` - Список гостей

### Отзывы
- `POST /api/v1/reviews/` - Оставить отзыв на гостя
- `GET /api/v1/reviews/guest/{guest_id}` - Отзывы о госте

## Пример создания брони

```bash
# 1. Получить токен
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}'

# 2. Создать бронь (система автоматически проверит гостя)
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "HOTEL_ID",
    "source": "booking.com",
    "booking_external_id": "BK123456",
    "guest_first_name": "Иван",
    "guest_last_name": "Иванов",
    "guest_phone": "+79161234567",
    "guest_email": "ivan@example.com",
    "checkin_date": "2026-04-01",
    "checkout_date": "2026-04-05",
    "room_type": "Standard",
    "total_amount": 15000,
    "currency": "RUB"
  }'
```

Ответ будет содержать:
- Статус брони (approved/approved_with_deposit/rejected)
- Уровень риска гостя
- Рекомендацию
- Информацию о депозите (если требуется)

## Документация API

После запуска доступна по адресам:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Логика риск-скоринга

Система рассчитывает риск на основе:
- Наличия в черном списке (+50 баллов)
- Средней оценки в отзывах (< 3.0 = +20 баллов)
- Истории повреждений (+15 баллов)
- Отсутствия истории бронирований (+10 баллов)

Уровни риска:
- **0-40**: LOW - Заселить без депозита
- **40-60**: MEDIUM - Рассмотреть депозит
- **60-80**: HIGH - Требуется депозит (30% от суммы)
- **80+**: CRITICAL - Отклонить бронь

## Структура проекта

```
app/
├── api/              # API endpoints
│   └── v1/
│       └── endpoints/
├── core/             # Конфигурация
├── db/               # База данных
├── models/           # SQLAlchemy модели
├── schemas/          # Pydantic схемы
└── services/         # Бизнес-логика
    ├── auth.py       # Авторизация
    ├── booking.py    # Обработка броней
    ├── guest.py      # Управление гостями
    └── risk_scoring.py # Расчет риска
```

## Следующие шаги

Для полноценной работы системы можно добавить:
1. Интеграцию с платежными системами для депозитов
2. Webhook для получения броней от booking.com, Airbnb и т.д.
3. Email уведомления
4. Панель аналитики
5. Экспорт отчетов
