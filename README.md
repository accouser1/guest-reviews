# Система проверки гостей для отелей

Веб-платформа для автоматической проверки гостей отелей с расчетом риск-скоринга и управлением депозитами.

## 🎯 Основные возможности

- ✅ Автоматическая проверка гостей при создании брони
- 📊 Риск-скоринг на основе истории отзывов и инцидентов
- 💰 Управление депозитами (холд, списание, возврат)
- 📝 Система отзывов на гостей после выезда
- 👥 Профили гостей с полной историей
- 🏨 Мультитенантность (несколько отелей)
- 🔐 Role-based access control
- 📈 Базовая аналитика

## 🚀 Быстрый старт

### Локальная разработка

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd hotel-guest-reviews

# 2. Запустить через Docker
docker-compose up -d

# 3. Применить миграции
docker-compose exec api alembic upgrade head

# 4. Инициализировать тестовые данные
docker-compose exec api python scripts/init_db.py

# 5. Открыть документацию API
# http://localhost:8000/api/v1/docs
```

### Production развертывание на guestreviews.ru

#### На VPS/VDS REG.RU (рекомендуется)

```bash
# На сервере
cd /opt/hotel-reviews
bash scripts/deploy.sh
```

**Пошаговая инструкция для REG.RU**: [REGRU_QUICKSTART.md](REGRU_QUICKSTART.md)

**Полная документация**:
- [Быстрый старт на REG.RU](REGRU_QUICKSTART.md) - 15 минут
- [Подробная инструкция REG.RU](REGRU_SETUP.md) - все варианты
- [Общее руководство](DEPLOY_GUESTREVIEWS_RU.md) - для любого хостинга

**Тестовые учетные данные:**
- Владелец: `admin@grandhotel.ru` / `admin123`
- Менеджер: `manager@grandhotel.ru` / `manager123`

## 📚 Документация

### Установка и развертывание
- **[Быстрый старт на REG.RU](REGRU_QUICKSTART.md)** - 15 минут ⭐
- **[Визуальное руководство REG.RU](REGRU_VISUAL_GUIDE.md)** - с картинками
- **[Шпаргалка REG.RU](REGRU_CHEATSHEET.md)** - все команды
- [Полная инструкция REG.RU](REGRU_SETUP.md) - все варианты
- [Быстрый старт](SETUP.md) - Локальная установка
- [Развертывание на guestreviews.ru](DEPLOY_GUESTREVIEWS_RU.md) - Общая инструкция
- [Production Setup](PRODUCTION_SETUP.md) - Полное руководство
- [Развертывание](DEPLOYMENT.md) - Общие инструкции

### Разработка
- [Руководство по API](API_GUIDE.md) - Описание всех endpoints
- [Архитектура](ARCHITECTURE.md) - Техническая документация
- [Модули системы](MODULES.md) - Описание всех модулей
- [Руководство разработчика](DEVELOPER_GUIDE.md) - Для разработчиков
- [Интеграции](INTEGRATIONS.md) - Примеры интеграций

### Справка
- [FAQ](FAQ.md) - Часто задаваемые вопросы
- [Резюме проекта](PROJECT_SUMMARY.md) - Обзор системы
- [Чеклист развертывания](DEPLOYMENT_CHECKLIST.md) - Проверка

## 🔄 Основной поток работы

```
Новая бронь → Поиск/создание гостя → Сбор истории → 
Расчет риска → Решение (одобрить/депозит/отклонить) → 
Депозит (если нужен) → Отзыв после выезда
```

## 🛠 Технологический стек

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 16
- **Cache/Sessions**: Redis 7
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Testing**: pytest with async support

## 📖 Пример использования API

### 1. Авторизация

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}'
```

### 2. Создание брони с автоматической проверкой

```bash
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

**Ответ:**
```json
{
  "id": "booking-uuid",
  "status": "approved_with_deposit",
  "guest_id": "guest-uuid",
  "risk_level": "medium",
  "risk_score": 55,
  "recommendation": "APPROVE WITH DEPOSIT: Consider security deposit.",
  "deposit_required": true,
  "deposit_amount": 4500.00
}
```

### 3. Создание отзыва после выезда

```bash
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "BOOKING_ID",
    "rating": 4,
    "comment": "Хороший гость",
    "tags": []
  }'
```

## 🎯 Логика риск-скоринга

Система рассчитывает риск на основе:
- ⚠️ Наличие в черном списке (+50 баллов)
- ⭐ Средняя оценка < 3.0 (+20 баллов)
- 💔 История повреждений (+15 баллов)
- 🆕 Новый гость без истории (+10 баллов)

**Уровни риска:**
- **0-40**: LOW - Заселить без депозита
- **40-60**: MEDIUM - Рассмотреть депозит
- **60-80**: HIGH - Требуется депозит (30%)
- **80+**: CRITICAL - Отклонить бронь

## 📁 Структура проекта

```
.
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── router.py
│   ├── core/             # Core configuration
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/               # Database
│   │   ├── session.py
│   │   └── redis.py
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── auth.py
│   │   ├── booking.py
│   │   ├── guest.py
│   │   └── risk_scoring.py
│   └── main.py           # Application entry point
├── migrations/           # Alembic migrations
├── scripts/              # Utility scripts
├── tests/                # Test suite
├── docker-compose.yml    # Local development setup
├── Dockerfile            # Container image
└── requirements.txt      # Python dependencies
```

## 🚦 API Endpoints

### Авторизация
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/register` - Регистрация

### Бронирования
- `POST /api/v1/bookings/` - Создать бронь (с автопроверкой)
- `GET /api/v1/bookings/{id}` - Детали брони
- `GET /api/v1/bookings/` - Список броней

### Гости
- `GET /api/v1/guests/{id}` - Профиль гостя
- `GET /api/v1/guests/` - Список гостей

### Отзывы
- `POST /api/v1/reviews/` - Создать отзыв
- `GET /api/v1/reviews/guest/{guest_id}` - Отзывы о госте

**Полная документация:** http://localhost:8000/api/v1/docs

## 🧪 Тестирование

```bash
# Запустить тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Использовать примеры
bash examples.sh
```

## 🔧 Разработка

### Локальный запуск

```bash
# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить базы данных
docker-compose up -d postgres redis

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

### Создание миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```

## 🌟 Следующие шаги

Для полноценной работы можно добавить:
- [ ] Webhook для booking.com, Airbnb
- [ ] Интеграция с платежными системами
- [ ] Email/SMS уведомления
- [ ] Панель аналитики и отчеты
- [ ] Мобильное приложение
- [ ] Экспорт данных

## 📄 Лицензия

Proprietary - All rights reserved
