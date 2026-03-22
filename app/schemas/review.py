"""Review schemas"""

from pydantic import BaseModel, Field
from decimal import Decimal


class ReviewCreate(BaseModel):
    """Create review request"""
    booking_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    tags: list[str] = []
    damage_amount: Decimal | None = None
    unpaid_amount: Decimal | None = None


class ReviewResponse(BaseModel):
    """Review response"""
    id: str
    booking_id: str
    guest_id: str
    rating: int
    comment: str | None
    tags: list[str]
    moderation_status: str
    created_at: str
    
    class Config:
        from_attributes = True
