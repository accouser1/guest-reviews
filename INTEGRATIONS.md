# Примеры интеграций

## Webhook для booking.com

### 1. Создать endpoint для webhook

```python
# app/api/v1/endpoints/webhooks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.booking import create_booking_with_check
from app.schemas.booking import BookingCreate

router = APIRouter()


@router.post("/webhooks/booking-com")
async def booking_com_webhook(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Webhook для получения броней от booking.com"""
    
    try:
        # Преобразовать данные booking.com в наш формат
        booking_data = BookingCreate(
            hotel_id=data["hotel_id"],
            source="booking.com",
            booking_external_id=data["reservation_id"],
            guest_first_name=data["guest"]["first_name"],
            guest_last_name=data["guest"]["last_name"],
            guest_phone=data["guest"]["phone"],
            guest_email=data["guest"]["email"],
            checkin_date=data["checkin"],
            checkout_date=data["checkout"],
            room_type=data["room_type"],
            total_amount=data["total_price"],
            currency=data["currency"],
        )
        
        # Создать бронь с автоматической проверкой
        booking, deposit = await create_booking_with_check(db, booking_data)
        
        # Вернуть результат
        return {
            "status": "success",
            "booking_id": booking.id,
            "decision": booking.status.value,
            "deposit_required": deposit is not None,
            "deposit_amount": float(deposit.amount) if deposit else None,
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Зарегистрировать webhook в booking.com

В панели управления booking.com:
1. Перейти в раздел "Connectivity"
2. Добавить webhook URL: `https://yourdomain.com/api/v1/webhooks/booking-com`
3. Выбрать события: "New Reservation"

## Интеграция с Airbnb

```python
# app/api/v1/endpoints/webhooks.py

@router.post("/webhooks/airbnb")
async def airbnb_webhook(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Webhook для получения броней от Airbnb"""
    
    booking_data = BookingCreate(
        hotel_id=data["listing_id"],
        source="airbnb",
        booking_external_id=data["confirmation_code"],
        guest_first_name=data["guest_details"]["first_name"],
        guest_last_name=data["guest_details"]["last_name"],
        guest_phone=data["guest_details"]["phone"],
        guest_email=data["guest_details"]["email"],
        checkin_date=data["start_date"],
        checkout_date=data["end_date"],
        room_type="Standard",
        total_amount=data["listing_base_price"],
        currency=data["listing_currency"],
    )
    
    booking, deposit = await create_booking_with_check(db, booking_data)
    
    return {
        "status": "accepted" if booking.status != "rejected" else "declined",
        "booking_id": booking.id,
    }
```

## Интеграция с платежной системой (Stripe)

### 1. Установить Stripe SDK

```bash
pip install stripe
```

### 2. Создать сервис для платежей

```python
# app/services/payment.py
import stripe
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.deposit import Deposit, Transaction, TransactionType, TransactionStatus

stripe.api_key = settings.STRIPE_SECRET_KEY


async def hold_deposit(
    db: AsyncSession,
    deposit: Deposit,
    payment_method_id: str,
) -> Transaction:
    """Холдирование депозита через Stripe"""
    
    try:
        # Создать PaymentIntent с capture_method='manual'
        intent = stripe.PaymentIntent.create(
            amount=int(deposit.amount * 100),  # В центах
            currency=deposit.currency.lower(),
            payment_method=payment_method_id,
            capture_method="manual",
            confirm=True,
            metadata={
                "deposit_id": deposit.id,
                "booking_id": deposit.booking_id,
            }
        )
        
        # Создать транзакцию
        transaction = Transaction(
            id=str(uuid.uuid4()),
            deposit_id=deposit.id,
            type=TransactionType.HOLD,
            amount=deposit.amount,
            status=TransactionStatus.COMPLETED,
            provider_transaction_id=intent.id,
        )
        
        db.add(transaction)
        deposit.status = DepositStatus.HELD
        deposit.payment_provider_id = intent.id
        
        await db.commit()
        return transaction
        
    except stripe.error.StripeError as e:
        # Обработка ошибки
        transaction = Transaction(
            id=str(uuid.uuid4()),
            deposit_id=deposit.id,
            type=TransactionType.HOLD,
            amount=deposit.amount,
            status=TransactionStatus.FAILED,
            reason=str(e),
        )
        db.add(transaction)
        deposit.status = DepositStatus.FAILED
        await db.commit()
        raise


async def charge_deposit(
    db: AsyncSession,
    deposit: Deposit,
    amount: Decimal,
    reason: str,
) -> Transaction:
    """Списание депозита"""
    
    try:
        # Захватить платеж
        intent = stripe.PaymentIntent.capture(
            deposit.payment_provider_id,
            amount_to_capture=int(amount * 100),
        )
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            deposit_id=deposit.id,
            type=TransactionType.CHARGE,
            amount=amount,
            reason=reason,
            status=TransactionStatus.COMPLETED,
            provider_transaction_id=intent.id,
        )
        
        db.add(transaction)
        deposit.status = DepositStatus.CHARGED
        await db.commit()
        return transaction
        
    except stripe.error.StripeError as e:
        raise


async def release_deposit(
    db: AsyncSession,
    deposit: Deposit,
) -> Transaction:
    """Возврат депозита"""
    
    try:
        # Отменить PaymentIntent
        intent = stripe.PaymentIntent.cancel(
            deposit.payment_provider_id
        )
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            deposit_id=deposit.id,
            type=TransactionType.RELEASE,
            amount=deposit.amount,
            status=TransactionStatus.COMPLETED,
            provider_transaction_id=intent.id,
        )
        
        db.add(transaction)
        deposit.status = DepositStatus.RELEASED
        await db.commit()
        return transaction
        
    except stripe.error.StripeError as e:
        raise
```

### 3. Добавить endpoints для депозитов

```python
# app/api/v1/endpoints/deposits.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.deposit import Deposit
from app.services.payment import hold_deposit, charge_deposit, release_deposit

router = APIRouter()


@router.post("/{deposit_id}/hold")
async def hold_deposit_endpoint(
    deposit_id: str,
    payment_method_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Холдировать депозит"""
    deposit = await db.get(Deposit, deposit_id)
    transaction = await hold_deposit(db, deposit, payment_method_id)
    return {"status": "success", "transaction_id": transaction.id}


@router.post("/{deposit_id}/charge")
async def charge_deposit_endpoint(
    deposit_id: str,
    amount: Decimal,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Списать депозит"""
    deposit = await db.get(Deposit, deposit_id)
    transaction = await charge_deposit(db, deposit, amount, reason)
    return {"status": "success", "transaction_id": transaction.id}


@router.post("/{deposit_id}/release")
async def release_deposit_endpoint(
    deposit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Вернуть депозит"""
    deposit = await db.get(Deposit, deposit_id)
    transaction = await release_deposit(db, deposit)
    return {"status": "success", "transaction_id": transaction.id}
```

## Email уведомления

### 1. Создать сервис для email

```python
# app/services/email.py
from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

from app.core.config import settings


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
):
    """Отправить email"""
    
    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    async with SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        use_tls=True,
    ) as smtp:
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)


async def send_booking_notification(booking_id: str, hotel_email: str):
    """Уведомление о новой брони"""
    
    template = Template("""
    <h2>Новая бронь</h2>
    <p>Получена новая бронь: {{ booking_id }}</p>
    <p>Уровень риска: {{ risk_level }}</p>
    <p>Рекомендация: {{ recommendation }}</p>
    """)
    
    html = template.render(
        booking_id=booking_id,
        risk_level="MEDIUM",
        recommendation="Требуется депозит",
    )
    
    await send_email(
        to_email=hotel_email,
        subject="Новая бронь",
        html_content=html,
    )


async def send_high_risk_alert(booking_id: str, hotel_email: str):
    """Алерт о высоком риске"""
    
    template = Template("""
    <h2>⚠️ Внимание: Высокий риск</h2>
    <p>Бронь {{ booking_id }} имеет высокий уровень риска.</p>
    <p>Рекомендуется проверить вручную.</p>
    """)
    
    html = template.render(booking_id=booking_id)
    
    await send_email(
        to_email=hotel_email,
        subject="⚠️ Высокий риск гостя",
        html_content=html,
    )
```

### 2. Добавить отправку в booking service

```python
# app/services/booking.py

async def create_booking_with_check(
    db: AsyncSession,
    booking_data: BookingCreate,
) -> tuple[Booking, Deposit | None]:
    # ... существующий код ...
    
    # Отправить уведомление
    if risk_score.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        await send_high_risk_alert(booking.id, hotel.email)
    else:
        await send_booking_notification(booking.id, hotel.email)
    
    return booking, deposit
```

## Интеграция с PMS (Property Management System)

```python
# app/services/pms.py
import httpx


async def sync_booking_to_pms(booking_id: str):
    """Синхронизация брони с PMS отеля"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://pms.hotel.com/api/bookings",
            json={
                "booking_id": booking_id,
                "guest_name": "...",
                "checkin": "...",
                "checkout": "...",
            },
            headers={"Authorization": "Bearer PMS_TOKEN"}
        )
        return response.json()


async def update_room_status(booking_id: str, status: str):
    """Обновить статус номера в PMS"""
    
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"https://pms.hotel.com/api/rooms/{room_id}",
            json={"status": status}
        )
```

## Telegram бот для уведомлений

```python
# app/services/telegram.py
import httpx

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"


async def send_telegram_message(message: str):
    """Отправить сообщение в Telegram"""
    
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            }
        )


async def notify_high_risk_booking(booking_id: str, guest_name: str, risk_score: int):
    """Уведомление о высоком риске в Telegram"""
    
    message = f"""
⚠️ <b>Высокий риск</b>

Бронь: {booking_id}
Гость: {guest_name}
Риск: {risk_score}/100

Требуется проверка!
"""
    
    await send_telegram_message(message)
```

## Настройка переменных окружения

Добавьте в `.env`:

```env
# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@hotel.com
SMTP_FROM_NAME=Hotel System

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789

# PMS
PMS_API_URL=https://pms.hotel.com/api
PMS_API_TOKEN=your-pms-token
```
