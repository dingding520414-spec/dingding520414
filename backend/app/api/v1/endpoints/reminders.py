from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from app.db.database import get_db
from app.models.models import User
from app.core.deps import get_current_user
from datetime import datetime
import time

router = APIRouter()


class ReminderSetting(BaseModel):
    """User reminder settings."""
    id: Optional[str] = None
    user_id: str
    reminder_time: str  # HH:MM format, e.g., "09:00"
    days_of_week: List[int]  # 0=Monday, 6=Sunday
    is_enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReminderSettingCreate(BaseModel):
    reminder_time: str  # HH:MM format
    days_of_week: List[int] = [0, 1, 2, 3, 4, 5, 6]  # Default: every day
    is_enabled: bool = True


class ReminderSettingUpdate(BaseModel):
    reminder_time: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    is_enabled: Optional[bool] = None


# In-memory reminder store (for MVP, replace with DB table in production)
_reminder_store: dict[str, dict] = {}


@router.get("", response_model=ReminderSetting)
async def get_reminder_setting(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's reminder settings."""
    user_id = str(current_user.id)

    if user_id in _reminder_store:
        setting = _reminder_store[user_id]
        return ReminderSetting(
            id=user_id,
            user_id=user_id,
            reminder_time=setting["reminder_time"],
            days_of_week=setting["days_of_week"],
            is_enabled=setting["is_enabled"],
            created_at=setting.get("created_at"),
            updated_at=setting.get("updated_at")
        )

    # Return default settings (no reminder)
    return ReminderSetting(
        id=user_id,
        user_id=user_id,
        reminder_time="09:00",
        days_of_week=[0, 1, 2, 3, 4, 5, 6],
        is_enabled=False
    )


@router.post("", response_model=ReminderSetting)
async def set_reminder_setting(
    data: ReminderSettingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set user's reminder settings."""
    user_id = str(current_user.id)

    # Validate time format
    try:
        time.strptime(data.reminder_time, "%H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

    # Validate days_of_week
    if not all(0 <= d <= 6 for d in data.days_of_week):
        raise HTTPException(status_code=400, detail="Days of week must be 0-6 (Mon-Sun)")

    now = datetime.utcnow()
    setting = {
        "reminder_time": data.reminder_time,
        "days_of_week": data.days_of_week,
        "is_enabled": data.is_enabled,
        "created_at": now,
        "updated_at": now
    }
    _reminder_store[user_id] = setting

    return ReminderSetting(
        id=user_id,
        user_id=user_id,
        reminder_time=setting["reminder_time"],
        days_of_week=setting["days_of_week"],
        is_enabled=setting["is_enabled"],
        created_at=setting["created_at"],
        updated_at=setting["updated_at"]
    )


@router.patch("", response_model=ReminderSetting)
async def update_reminder_setting(
    data: ReminderSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's reminder settings."""
    user_id = str(current_user.id)

    if user_id not in _reminder_store:
        # Create default first
        await set_reminder_setting(
            ReminderSettingCreate(reminder_time="09:00"),
            db, current_user
        )

    setting = _reminder_store[user_id]

    if data.reminder_time is not None:
        try:
            time.strptime(data.reminder_time, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
        setting["reminder_time"] = data.reminder_time

    if data.days_of_week is not None:
        if not all(0 <= d <= 6 for d in data.days_of_week):
            raise HTTPException(status_code=400, detail="Days of week must be 0-6 (Mon-Sun)")
        setting["days_of_week"] = data.days_of_week

    if data.is_enabled is not None:
        setting["is_enabled"] = data.is_enabled

    setting["updated_at"] = datetime.utcnow()

    return ReminderSetting(
        id=user_id,
        user_id=user_id,
        reminder_time=setting["reminder_time"],
        days_of_week=setting["days_of_week"],
        is_enabled=setting["is_enabled"],
        created_at=setting.get("created_at"),
        updated_at=setting["updated_at"]
    )


@router.delete("")
async def delete_reminder_setting(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete/disable user's reminder settings."""
    user_id = str(current_user.id)

    if user_id in _reminder_store:
        _reminder_store[user_id]["is_enabled"] = False
        _reminder_store[user_id]["updated_at"] = datetime.utcnow()

    return {"message": "Reminder disabled"}
