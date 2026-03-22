"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.services.auth import authenticate_user, create_access_token, get_password_hash
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login user"""
    user = await authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
        }
    )
    
    return Token(access_token=access_token)


@router.post("/register", response_model=Token)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register new user"""
    
    # Check if user exists
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role=UserRole(request.role),
        hotel_id=request.hotel_id,
        is_active=True,
    )
    
    db.add(user)
    await db.commit()
    
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
        }
    )
    
    return Token(access_token=access_token)
