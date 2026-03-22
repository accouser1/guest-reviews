# Быстрый старт за 5 минут

## Шаг 1: Запуск системы

```bash
# Запустить все сервисы
docker-compose up -d

# Дождаться запуска (30-60 секунд)
docker-compose logs -f api
```

Когда увидите `Application startup complete`, система готова.

## Шаг 2: Инициализация базы данных

```bash
# Применить миграции
docker-compose exec api alembic upgrade head

# Создать тестовые данные
docker-compose exec api python scripts/init_db.py
```

Будут созданы:
- Отель "Grand Hotel"
- Админ: `admin@grandhotel.ru` / `admin123`
- Менеджер: `manager@grandhotel.ru` / `manager123`
- 2 тестовых гостя

## Шаг 3: Проверка работы

Откройте в браузере:
- API документация: http://localhost:8000/api/v1/docs
- Health check: http://localhost:8000/health

## Шаг 4: Первый запрос

### 1. Получить токен

В Swagger UI (http://localhost:8000/api/v1/docs):
1. Найдите `POST /auth/login`
2. Нажмите "Try it out"
3. Введите:
   ```json
   {
     "email": "admin@grandhotel.ru",
     "password": "admin123"
   }
   ```
4. Скопируйте `access_token` из ответа

### 2. Авторизоваться

1. Нажмите кнопку "Authorize" вверху страницы
2. Вставьте токен
3. Нажмите "Authorize"

### 3. Создать бронь

1. Найдите `POST /bookings/`
2. Нажмите "Try it out"
3. Замените `YOUR_HOTEL_ID` на ID отеля из вывода `init_db.py`
4. Нажмите "Execute"

Система автоматически:
- Найдет или создаст гостя
- Рассчитает риск
- Примет решение
- Создаст депозит (если нужен)

### 4. Посмотреть результат

Ответ будет содержать:
```json
{
  "id": "booking-uuid",
  "status": "approved",
  "guest_id": "guest-uuid",
  "risk_level": "low",
  "risk_score": 60,
  "recommendation": "APPROVE: Low risk guest...",
  "deposit_required": false,
  "deposit_amount": null
}
```

## Шаг 5: Создать отзыв

После "выезда" гостя:

1. Найдите `POST /reviews/`
2. Используйте `booking_id` из предыдущего шага
3. Создайте отзыв:
   ```json
   {
     "booking_id": "booking-uuid",
     "rating": 5,
     "comment": "Отличный гость!",
     "tags": []
   }
   ```

## Готово!

Теперь вы можете:
- Создавать брони через API
- Просматривать профили гостей
- Оставлять отзывы
- Управлять депозитами

## Следующие шаги

1. Изучите [API Guide](API_GUIDE.md) для всех возможностей
2. Настройте интеграцию с вашей системой бронирования
3. Настройте webhook для автоматического получения броней
4. Интегрируйте платежную систему для депозитов

## Полезные команды

```bash
# Остановить систему
docker-compose down

# Перезапустить
docker-compose restart

# Посмотреть логи
docker-compose logs -f api

# Зайти в контейнер
docker-compose exec api bash

# Очистить все данные
docker-compose down -v
```

## Проблемы?

См. [FAQ](FAQ.md) или [DEPLOYMENT](DEPLOYMENT.md) для решения проблем.
