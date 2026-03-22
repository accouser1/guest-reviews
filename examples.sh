#!/bin/bash

# Примеры использования API системы проверки гостей

BASE_URL="http://localhost:8000/api/v1"

echo "=== 1. Проверка здоровья системы ==="
curl -X GET http://localhost:8000/health
echo -e "\n"

echo "=== 2. Вход в систему ==="
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@grandhotel.ru","password":"admin123"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token: $TOKEN"
echo -e "\n"

echo "=== 3. Получение ID отеля ==="
# Предполагаем, что ID отеля известен из init_db.py
# В реальности нужно получить через API списка отелей
HOTEL_ID="YOUR_HOTEL_ID_HERE"

echo "=== 4. Создание брони с автоматической проверкой ==="
BOOKING_RESPONSE=$(curl -s -X POST "$BASE_URL/bookings/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "'$HOTEL_ID'",
    "source": "booking.com",
    "booking_external_id": "BK'$(date +%s)'",
    "guest_first_name": "Иван",
    "guest_last_name": "Петров",
    "guest_phone": "+79161234567",
    "guest_email": "ivan.petrov@example.com",
    "checkin_date": "2026-04-01",
    "checkout_date": "2026-04-05",
    "room_type": "Standard",
    "total_amount": 15000,
    "currency": "RUB"
  }')

echo "$BOOKING_RESPONSE" | python -m json.tool
BOOKING_ID=$(echo "$BOOKING_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
GUEST_ID=$(echo "$BOOKING_RESPONSE" | grep -o '"guest_id":"[^"]*' | cut -d'"' -f4)
echo -e "\n"

echo "=== 5. Просмотр деталей брони ==="
curl -s -X GET "$BASE_URL/bookings/$BOOKING_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
echo -e "\n"

echo "=== 6. Просмотр профиля гостя ==="
curl -s -X GET "$BASE_URL/guests/$GUEST_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
echo -e "\n"

echo "=== 7. Список всех броней ==="
curl -s -X GET "$BASE_URL/bookings/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
echo -e "\n"

echo "=== 8. Создание положительного отзыва ==="
curl -s -X POST "$BASE_URL/reviews/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "'$BOOKING_ID'",
    "rating": 5,
    "comment": "Отличный гость, все в порядке",
    "tags": []
  }' \
  | python -m json.tool
echo -e "\n"

echo "=== 9. Просмотр отзывов о госте ==="
curl -s -X GET "$BASE_URL/reviews/guest/$GUEST_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
echo -e "\n"

echo "=== 10. Создание брони для проблемного гостя ==="
curl -s -X POST "$BASE_URL/bookings/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": "'$HOTEL_ID'",
    "source": "airbnb",
    "booking_external_id": "AB'$(date +%s)'",
    "guest_first_name": "Проблемный",
    "guest_last_name": "Гость",
    "guest_phone": "+79169999999",
    "guest_email": "problem@example.com",
    "checkin_date": "2026-04-10",
    "checkout_date": "2026-04-12",
    "room_type": "Deluxe",
    "total_amount": 25000,
    "currency": "RUB"
  }' \
  | python -m json.tool
echo -e "\n"

echo "Готово! Все примеры выполнены."
