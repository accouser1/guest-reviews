"""Booking schemas"""

from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class BookingCreate(BaseModel):
    """Create booking request"""
    hotel_id: str
    branch_id: str | None = None
    source: str
    booking_external_id: str
    guest_first_name: str
    guest_last_name: str
    guest_phone: str | None = None
    guest_email: str | None = None
    checkin_date: date
    checkout_date: date
    room_type: str
    total_amount: Decimal
    currency: str = "RUB"


class BookingResponse(BaseModel):
    """Booking response"""
    id: str
    status: str
    guest_id: str
    risk_level: str | None = None
    risk_score: int | None = None
    recommendation: str | None = None
    deposit_required: bool = False
    deposit_amount: Decimal | None = None
    
    class Config:
        from_attributes = True
