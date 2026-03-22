"""Guest model"""

from typing import Optional
from datetime import date
from sqlalchemy import String, Boolean, Date, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Guest(Base, TimestampMixin):
    """Guest model"""
    
    __tablename__ = "guests"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    document_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    risk_level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel),
        default=RiskLevel.MEDIUM,
        nullable=False,
        index=True,
    )
    blacklist_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="guest")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="guest")
    risk_scores: Mapped[list["RiskScore"]] = relationship("RiskScore", back_populates="guest")
