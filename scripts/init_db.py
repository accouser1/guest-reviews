"""Initialize database with sample data"""

import asyncio
import uuid
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base
from app.models.user import User, UserRole
from app.models.hotel import Hotel, HotelSettings
from app.models.guest import Guest, RiskLevel
from app.services.auth import get_password_hash


async def init_sample_data():
    """Initialize database with sample data"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create hotel
        hotel_id = str(uuid.uuid4())
        hotel = Hotel(
            id=hotel_id,
            name="Grand Hotel",
            legal_name="Grand Hotel LLC",
            address={"city": "Moscow", "street": "Tverskaya 1"},
            phone="+7 495 123-45-67",
            email="info@grandhotel.ru",
        )
        session.add(hotel)
        
        # Create hotel settings
        settings_obj = HotelSettings(
            id=str(uuid.uuid4()),
            hotel_id=hotel_id,
            deposit_policy={"default_percentage": 30},
            risk_thresholds={"low": 40, "medium": 60, "high": 80},
            auto_scoring_enabled=True,
            notification_preferences={},
            custom_risk_rules={},
        )
        session.add(settings_obj)
        
        # Create admin user
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@grandhotel.ru",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.OWNER,
            hotel_id=hotel_id,
            is_active=True,
        )
        session.add(admin)
        
        # Create manager user
        manager = User(
            id=str(uuid.uuid4()),
            email="manager@grandhotel.ru",
            password_hash=get_password_hash("manager123"),
            first_name="Manager",
            last_name="User",
            role=UserRole.MANAGER,
            hotel_id=hotel_id,
            is_active=True,
        )
        session.add(manager)
        
        # Create sample guests
        guest1 = Guest(
            id=str(uuid.uuid4()),
            first_name="Ivan",
            last_name="Petrov",
            phone="+79161234567",
            email="ivan@example.com",
            risk_level=RiskLevel.LOW,
            blacklist_flag=False,
        )
        session.add(guest1)
        
        guest2 = Guest(
            id=str(uuid.uuid4()),
            first_name="Maria",
            last_name="Sidorova",
            phone="+79167654321",
            email="maria@example.com",
            risk_level=RiskLevel.MEDIUM,
            blacklist_flag=False,
        )
        session.add(guest2)
        
        await session.commit()
        
        print("✅ Database initialized with sample data")
        print(f"Hotel: {hotel.name} (ID: {hotel_id})")
        print(f"Admin: admin@grandhotel.ru / admin123")
        print(f"Manager: manager@grandhotel.ru / manager123")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_sample_data())
