"""API v1 Router"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, bookings, guests, reviews

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(guests.router, prefix="/guests", tags=["guests"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])


@api_router.get("/status")
async def api_status():
    """API status endpoint"""
    return {"status": "operational", "version": "1.0.0"}
