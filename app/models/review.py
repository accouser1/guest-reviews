"""Review model"""

from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Text, Numeric, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin


class ReviewTag(str, enum.Enum):
    """Review tag enumeration"""
    THEFT = "theft"
    MINIBAR_UNPAID = "minibar_unpaid"
    NOISE = "noise"
    PARTY = "party"
    PROPERTY_DAMAGE = "property_damage"
    FRAUD = "fraud"
    RUDE_BEHAVIOR = "rude_behavior"
    PAYMENT_ISSUE = "payment_issue"


class ModerationStatus(str, enum.Enum):
    """Moderation status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    HIDDEN = "hidden"
    DISPUTED = "disputed"


class Review(Base, TimestampMixin):
    """Review model"""
    
    __tablename__ = "reviews"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    booking_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    guest_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("guests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    hotel_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    damage_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    unpaid_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    evidence_files: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    moderation_status: Mapped[ModerationStatus] = mapped_column(
        SQLEnum(ModerationStatus),
        default=ModerationStatus.APPROVED,
        nullable=False,
        index=True,
    )
    
    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")
    guest: Mapped["Guest"] = relationship("Guest", back_populates="reviews")
    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="reviews")
    author: Mapped["User"] = relationship("User", back_populates="reviews")
