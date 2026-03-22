"""User model"""

from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"
    OWNER = "owner"
    MANAGER = "manager"
    AUDITOR = "auditor"


class User(Base, TimestampMixin):
    """User model"""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    hotel_id: Mapped[Optional[str]] = mapped_column(
        String(36), 
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    hotel: Mapped[Optional["Hotel"]] = relationship("Hotel", back_populates="users")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="author")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")
