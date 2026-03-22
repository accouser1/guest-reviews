"""Guest schemas"""

from pydantic import BaseModel
from datetime import date


class GuestResponse(BaseModel):
    """Guest response"""
    id: str
    first_name: str
    last_name: str
    phone: str | None
    email: str | None
    risk_level: str
    blacklist_flag: bool
    total_bookings: int = 0
    total_reviews: int = 0
    average_rating: float | None = None
    
    class Config:
        from_attributes = True
