"""Risk score model"""

from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, ARRAY, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import Base
from app.models.guest import RiskLevel


class RiskScore(Base):
    """Risk score model"""
    
    __tablename__ = "risk_scores"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
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
    booking_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("bookings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(String(20), nullable=False, index=True)
    reasons: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    
    # Relationships
    guest: Mapped["Guest"] = relationship("Guest", back_populates="risk_scores")
