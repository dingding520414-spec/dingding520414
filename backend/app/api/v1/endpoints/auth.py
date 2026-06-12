from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import User, Subscription
from app.schemas.schemas import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest
)
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token
)
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


async def get_current_user(
    token: str = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/register", response_model=TokenResponse)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email/phone already exists
    if data.email:
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    if data.phone:
        result = await db.execute(select(User).where(User.phone == data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered"
            )
    
    # Create user
    user = User(
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        name=data.name,
        age=data.age
    )
    db.add(user)
    await db.flush()
    
    # Create free subscription
    subscription = Subscription(
        user_id=user.id,
        plan_type="free",
        status="active"
    )
    db.add(subscription)
    
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "fitness_goal": user.fitness_goal,
            "health_notes": user.health_notes,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user."""
    # Find user
    query = select(User)
    if data.email:
        query = query.where(User.email == data.email)
    else:
        query = query.where(User.phone == data.phone)
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "fitness_goal": user.fitness_goal,
            "health_notes": user.health_notes,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at
        }
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "fitness_goal": user.fitness_goal,
            "health_notes": user.health_notes,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at
        }
    )