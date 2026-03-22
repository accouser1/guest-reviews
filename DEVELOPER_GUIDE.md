# Руководство для разработчика

## Начало работы

### Установка окружения

```bash
# Клонировать репозиторий
git clone <repository-url>
cd hotel-guest-reviews

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Скопировать .env
copy .env.example .env
```

### Запуск для разработки

```bash
# Запустить базы данных
docker-compose up -d postgres redis

# Применить миграции
alembic upgrade head

# Инициализировать данные
python scripts/init_db.py

# Запустить сервер с hot reload
uvicorn app.main:app --reload
```

## Структура кода

### Слои приложения

```
API Layer (endpoints)
    ↓
Service Layer (business logic)
    ↓
Data Layer (models, database)
```

### Добавление нового функционала

#### 1. Создать модель (если нужна)

```python
# app/models/new_model.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class NewModel(Base, TimestampMixin):
    __tablename__ = "new_models"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
```

#### 2. Создать миграцию

```bash
alembic revision --autogenerate -m "add new_model table"
alembic upgrade head
```

#### 3. Создать схемы

```python
# app/schemas/new_model.py
from pydantic import BaseModel


class NewModelCreate(BaseModel):
    name: str


class NewModelResponse(BaseModel):
    id: str
    name: str
    
    class Config:
        from_attributes = True
```

#### 4. Создать сервис

```python
# app/services/new_service.py
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.new_model import NewModel


async def create_new_model(db: AsyncSession, name: str) -> NewModel:
    """Create new model"""
    model = NewModel(
        id=str(uuid.uuid4()),
        name=name,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model
```

#### 5. Создать endpoint

```python
# app/api/v1/endpoints/new_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.new_model import NewModelCreate, NewModelResponse
from app.services.new_service import create_new_model

router = APIRouter()


@router.post("/", response_model=NewModelResponse)
async def create(
    data: NewModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new model"""
    model = await create_new_model(db, data.name)
    return model
```

#### 6. Подключить роутер

```python
# app/api/v1/router.py
from app.api.v1.endpoints import new_endpoint

api_router.include_router(
    new_endpoint.router,
    prefix="/new-models",
    tags=["new-models"]
)
```

## Работа с базой данных

### Создание миграции

```bash
# Автоматическая генерация
alembic revision --autogenerate -m "description"

# Ручная миграция
alembic revision -m "description"
```

### Применение миграций

```bash
# Применить все
alembic upgrade head

# Применить конкретную
alembic upgrade <revision>

# Откатить
alembic downgrade -1
```

### Работа с сессией

```python
from sqlalchemy import select
from app.db.session import get_db

async def get_items(db: AsyncSession):
    # SELECT
    result = await db.execute(select(Model))
    items = result.scalars().all()
    
    # INSERT
    item = Model(id=str(uuid.uuid4()), name="test")
    db.add(item)
    await db.commit()
    await db.refresh(item)
    
    # UPDATE
    item.name = "updated"
    await db.commit()
    
    # DELETE
    await db.delete(item)
    await db.commit()
```

## Тестирование

### Структура тестов

```
tests/
├── conftest.py          # Fixtures
├── test_auth.py         # Тесты авторизации
├── test_bookings.py     # Тесты бронирований
├── test_guests.py       # Тесты гостей
└── test_risk_scoring.py # Тесты риск-скоринга
```

### Написание тестов

```python
# tests/test_new_feature.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, auth_headers: dict):
    """Test creating item"""
    response = await client.post(
        "/api/v1/items/",
        json={"name": "test"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test"
```

### Запуск тестов

```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/test_bookings.py

# Конкретный тест
pytest tests/test_bookings.py::test_create_booking

# С покрытием
pytest --cov=app --cov-report=html
```

## Отладка

### Логирование

```python
from app.core.logging import logger

logger.info("Info message", extra_field="value")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Отладка в VS Code

`.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload"
            ],
            "jinja": true
        }
    ]
}
```

### Отладка SQL запросов

```python
# В .env
DATABASE_URL=postgresql+asyncpg://...?echo=true

# Или в коде
engine = create_async_engine(url, echo=True)
```

## Лучшие практики

### Код

1. **Используйте type hints**
   ```python
   async def get_user(user_id: str) -> User | None:
       ...
   ```

2. **Документируйте функции**
   ```python
   async def calculate_risk(guest_id: str) -> int:
       """
       Calculate risk score for guest.
       
       Args:
           guest_id: Guest UUID
           
       Returns:
           Risk score (0-100)
       """
   ```

3. **Обрабатывайте ошибки**
   ```python
   try:
       result = await some_operation()
   except SpecificError as e:
       logger.error("Operation failed", exc_info=True)
       raise HTTPException(status_code=400, detail=str(e))
   ```

### База данных

1. **Используйте индексы**
   ```python
   email: Mapped[str] = mapped_column(String(255), index=True)
   ```

2. **Используйте транзакции**
   ```python
   async with db.begin():
       # Все операции в одной транзакции
       db.add(item1)
       db.add(item2)
   ```

3. **Избегайте N+1 запросов**
   ```python
   # Плохо
   for booking in bookings:
       guest = await db.get(Guest, booking.guest_id)
   
   # Хорошо
   result = await db.execute(
       select(Booking).options(selectinload(Booking.guest))
   )
   ```

### API

1. **Используйте правильные HTTP коды**
   - 200: OK
   - 201: Created
   - 400: Bad Request
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not Found
   - 500: Internal Server Error

2. **Валидируйте входные данные**
   ```python
   class BookingCreate(BaseModel):
       total_amount: Decimal = Field(gt=0)
       checkin_date: date
       
       @validator('checkout_date')
       def checkout_after_checkin(cls, v, values):
           if v <= values['checkin_date']:
               raise ValueError('Checkout must be after checkin')
           return v
   ```

3. **Используйте пагинацию**
   ```python
   @router.get("/")
   async def list_items(skip: int = 0, limit: int = 50):
       ...
   ```

## Полезные команды

### Разработка

```bash
# Запустить сервер
make dev
# или
uvicorn app.main:app --reload

# Запустить тесты
make test
# или
pytest

# Применить миграции
make migrate
# или
alembic upgrade head

# Инициализировать БД
make init-db
# или
python scripts/init_db.py
```

### Docker

```bash
# Запустить все
docker-compose up -d

# Остановить
docker-compose down

# Посмотреть логи
docker-compose logs -f api

# Зайти в контейнер
docker-compose exec api bash

# Пересобрать
docker-compose up --build
```

### База данных

```bash
# Подключиться к PostgreSQL
docker-compose exec postgres psql -U postgres -d hotel_reviews

# Создать бэкап
pg_dump hotel_reviews > backup.sql

# Восстановить
psql hotel_reviews < backup.sql
```

## Troubleshooting

### Проблема: Миграции не применяются

```bash
# Проверить текущую версию
alembic current

# Посмотреть историю
alembic history

# Откатить и применить заново
alembic downgrade -1
alembic upgrade head
```

### Проблема: Ошибка импорта

```bash
# Переустановить зависимости
pip install -r requirements.txt --force-reinstall

# Проверить PYTHONPATH
echo $PYTHONPATH  # Linux/Mac
echo %PYTHONPATH%  # Windows
```

### Проблема: База данных заблокирована

```bash
# Убить все подключения
docker-compose restart postgres

# Или через SQL
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'hotel_reviews';
```

## Ресурсы

### Документация

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Alembic: https://alembic.sqlalchemy.org/

### Внутренняя документация

- `ARCHITECTURE.md` - Архитектура системы
- `MODULES.md` - Описание модулей
- `API_GUIDE.md` - Руководство по API
- `FAQ.md` - Часто задаваемые вопросы

## Контрибьюция

1. Создайте ветку для фичи
   ```bash
   git checkout -b feature/new-feature
   ```

2. Внесите изменения

3. Напишите тесты

4. Запустите тесты
   ```bash
   pytest
   ```

5. Создайте pull request

## Код-ревью чеклист

- [ ] Код следует PEP 8
- [ ] Добавлены type hints
- [ ] Добавлены docstrings
- [ ] Написаны тесты
- [ ] Тесты проходят
- [ ] Нет SQL injection уязвимостей
- [ ] Обработаны ошибки
- [ ] Добавлено логирование
- [ ] Обновлена документация
