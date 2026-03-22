"""Deposit models"""

from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin


class DepositStatus(str, enum.Enum):
    """Deposit status enumeration"""
    NOT_REQUIRED = "not_required"
    REQUIRED = "required"
    HOLD_PENDING = "hold_pending"
    HELD = "held"
    PARTIALLY_CHARGED = "partially_charged"
    CHARGED = "charged"
    RELEASED = "released"
    FAILED = "failed"


class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    HOLD = "hold"
    CHARGE = "charge"
    RELEASE = "release"


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Deposit(Base, TimestampMixin):
    """Deposit model"""
    
    __tablename__ = "deposits"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    booking_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    status: Mapped[DepositStatus] = mapped_column(
        SQLEnum(DepositStatus),
        default=DepositStatus.REQUIRED,
        nullable=False,
        index=True,
    )
    payment_provider_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="deposit")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="deposit",
        cascade="all, delete-orphan",
    )


class Transaction(Base, TimestampMixin):
    """Transaction model"""
    
    __tablename__ = "transactions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    deposit_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("deposits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True,
    )
    provider_transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    deposit: Mapped["Deposit"] = relationship("Deposit", back_populates="transactions")
