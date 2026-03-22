"""Booking endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking import create_booking_with_check

router = APIRouter()


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new booking with automatic risk check"""
    
    booking, deposit = await create_booking_with_check(db, booking_data)
    
    # Get risk score
    risk_score = None
    if booking.risk_score_id:
        risk_score = await db.get("RiskScore", booking.risk_score_id)
    
    return BookingResponse(
        id=booking.id,
        status=booking.status.value,
        guest_id=booking.guest_id,
        risk_level=risk_score.risk_level.value if risk_score else None,
        risk_score=risk_score.score if risk_score else None,
        recommendation=risk_score.recommendation if risk_score else None,
        deposit_required=deposit is not None,
        deposit_amount=deposit.amount if deposit else None,
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get booking details"""
    
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get risk score
    from app.models.risk_score import RiskScore
    risk_score = None
    if booking.risk_score_id:
        risk_score = await db.get(RiskScore, booking.risk_score_id)
    
    # Get deposit
    from app.models.deposit import Deposit
    deposit = None
    if booking.deposit_id:
        deposit = await db.get(Deposit, booking.deposit_id)
    
    return BookingResponse(
        id=booking.id,
        status=booking.status.value,
        guest_id=booking.guest_id,
        risk_level=risk_score.risk_level.value if risk_score else None,
        risk_score=risk_score.score if risk_score else None,
        recommendation=risk_score.recommendation if risk_score else None,
        deposit_required=deposit is not None,
        deposit_amount=deposit.amount if deposit else None,
    )


@router.get("/")
async def list_bookings(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List bookings"""
    
    query = select(Booking).offset(skip).limit(limit)
    
    # Filter by hotel for non-admin users
    if current_user.hotel_id:
        query = query.where(Booking.hotel_id == current_user.hotel_id)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return {"bookings": bookings, "total": len(bookings)}
