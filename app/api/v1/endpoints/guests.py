"""Guest endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.guest import Guest
from app.models.review import Review
from app.models.booking import Booking
from app.schemas.guest import GuestResponse

router = APIRouter()


@router.get("/{guest_id}", response_model=GuestResponse)
async def get_guest(
    guest_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get guest profile with statistics"""
    
    guest = await db.get(Guest, guest_id)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    # Get statistics
    booking_count = await db.scalar(
        select(func.count(Booking.id)).where(Booking.guest_id == guest_id)
    )
    
    review_stats = await db.execute(
        select(
            func.count(Review.id).label("total"),
            func.avg(Review.rating).label("avg_rating"),
        ).where(Review.guest_id == guest_id)
    )
    stats = review_stats.one()
    
    return GuestResponse(
        id=guest.id,
        first_name=guest.first_name,
        last_name=guest.last_name,
        phone=guest.phone,
        email=guest.email,
        risk_level=guest.risk_level.value,
        blacklist_flag=guest.blacklist_flag,
        total_bookings=booking_count or 0,
        total_reviews=stats.total or 0,
        average_rating=float(stats.avg_rating) if stats.avg_rating else None,
    )


@router.get("/")
async def list_guests(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List guests"""
    
    result = await db.execute(
        select(Guest).offset(skip).limit(limit)
    )
    guests = result.scalars().all()
    
    return {"guests": guests, "total": len(guests)}
