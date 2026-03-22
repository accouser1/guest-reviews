"""Booking model"""

from typing import Optional
from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin


class BookingStatus(str, enum.Enum):
    """Booking status enumeration"""
    NEW = "new"
    PENDING_CHECK = "pending_check"
    CHECKED = "checked"
    APPROVED = "approved"
    APPROVED_WITH_DEPOSIT = "approved_with_deposit"
    REJECTED = "rejected"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"


class Booking(Base, TimestampMixin):
    """Booking model"""
    
    __tablename__ = "bookings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    hotel_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("hotel_branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    booking_external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    guest_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("guests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    room_type: Mapped[str] = mapped_column(String(100), nullable=False)
    room_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus),
        default=BookingStatus.NEW,
        nullable=False,
        index=True,
    )
    risk_score_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("risk_scores.id", ondelete="SET NULL"),
        nullable=True,
    )
    deposit_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("deposits.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Relationships
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="bookings")
    branch: Mapped[Optional["HotelBranch"]] = relationship("HotelBranch", back_populates="bookings")
    guest: Mapped["Guest"] = relationship("Guest", back_populates="bookings")
    risk_score: Mapped[Optional["RiskScore"]] = relationship("RiskScore", foreign_keys=[risk_score_id])
    deposit: Mapped[Optional["Deposit"]] = relationship("Deposit", back_populates="booking", uselist=False)
    review: Mapped[Optional["Review"]] = relationship("Review", back_populates="booking", uselist=False)
