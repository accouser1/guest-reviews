"""Review endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.review import Review, ModerationStatus
from app.models.booking import Booking
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create review for guest after checkout"""
    
    # Get booking
    booking = await db.get(Booking, review_data.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if review already exists
    result = await db.execute(
        select(Review).where(Review.booking_id == review_data.booking_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Review already exists for this booking")
    
    # Create review
    review = Review(
        id=str(uuid.uuid4()),
        booking_id=review_data.booking_id,
        guest_id=booking.guest_id,
        hotel_id=booking.hotel_id,
        author_id=current_user.id,
        rating=review_data.rating,
        comment=review_data.comment,
        tags=review_data.tags,
        damage_amount=review_data.damage_amount,
        unpaid_amount=review_data.unpaid_amount,
        moderation_status=ModerationStatus.APPROVED,
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        booking_id=review.booking_id,
        guest_id=review.guest_id,
        rating=review.rating,
        comment=review.comment,
        tags=review.tags,
        moderation_status=review.moderation_status.value,
        created_at=review.created_at.isoformat(),
    )


@router.get("/guest/{guest_id}")
async def get_guest_reviews(
    guest_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all reviews for a guest"""
    
    result = await db.execute(
        select(Review)
        .where(Review.guest_id == guest_id)
        .where(Review.moderation_status == ModerationStatus.APPROVED)
    )
    reviews = result.scalars().all()
    
    return {"reviews": reviews, "total": len(reviews)}
