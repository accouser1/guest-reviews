"""Hotel models"""

from typing import Optional
from sqlalchemy import String, Boolean, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Hotel(Base, TimestampMixin):
    """Hotel model"""
    
    __tablename__ = "hotels"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[dict] = mapped_column(JSON, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="hotel")
    branches: Mapped[list["HotelBranch"]] = relationship("HotelBranch", back_populates="hotel", cascade="all, delete-orphan")
    settings: Mapped[Optional["HotelSettings"]] = relationship("HotelSettings", back_populates="hotel", uselist=False, cascade="all, delete-orphan")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="hotel")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="hotel")
    integrations: Mapped[list["Integration"]] = relationship("Integration", back_populates="hotel", cascade="all, delete-orphan")


class HotelBranch(Base, TimestampMixin):
    """Hotel branch model"""
    
    __tablename__ = "hotel_branches"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    hotel_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="branches")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="branch")


class HotelSettings(Base, TimestampMixin):
    """Hotel settings model"""
    
    __tablename__ = "hotel_settings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    hotel_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    deposit_policy: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    risk_thresholds: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    auto_scoring_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notification_preferences: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    custom_risk_rules: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="settings")


class Integration(Base, TimestampMixin):
    """Integration model for external booking platforms"""
    
    __tablename__ = "integrations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    hotel_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    credentials: Mapped[dict] = mapped_column(JSON, nullable=False)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="integrations")
