from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserUpdate
from app.core.deps import get_current_user
import uuid

router = APIRouter()


def get_user_from_header(x_token: str = None, db: AsyncSession = Depends(get_db)):
    """Extract user from X-Token header for adult viewing elder data."""
    if not x_token:
        return get_current_user(x_token, db)
    
    payload = decode_token(x_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user profile."""
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload user avatar."""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    # Generate filename
    ext = file.filename.split(".")[-1]
    filename = f"avatars/{current_user.id}/{uuid.uuid4()}.{ext}"
    
    # TODO: Upload to R2/S3
    # For now, store as local path (will be replaced with R2 upload)
    avatar_url = f"/uploads/{filename}"
    
    current_user.avatar_url = avatar_url
    await db.commit()
    
    return {"avatar_url": avatar_url}