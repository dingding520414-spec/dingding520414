from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.database import get_db
from app.models.models import User, Family, FamilyMember
from app.schemas.schemas import (
    BindCodeResponse, FamilyMemberResponse, FamilyProgressResponse
)
from app.core.deps import get_current_user
from datetime import datetime, timedelta, date
from uuid import UUID
import secrets
import string

router = APIRouter()


def generate_bind_code(length: int = 8) -> str:
    """Generate a random alphanumeric bind code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


@router.post("/generate-code", response_model=BindCodeResponse)
async def generate_bind_code_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a family bind code for elders."""
    # Check if user already has a family
    member_result = await db.execute(
        select(FamilyMember).where(FamilyMember.user_id == current_user.id)
    )
    member = member_result.scalar_one_or_none()
    
    if member:
        # Update existing code
        family_result = await db.execute(
            select(Family).where(Family.id == member.family_id)
        )
        family = family_result.scalar_one_or_none()
        if family:
            family.bind_code = generate_bind_code()
            family.bind_code_expires_at = datetime.utcnow() + timedelta(minutes=30)
            await db.commit()
            return BindCodeResponse(
                bind_code=family.bind_code,
                expires_at=family.bind_code_expires_at
            )
    
    # Create new family
    bind_code = generate_bind_code()
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    family = Family(
        bind_code=bind_code,
        bind_code_expires_at=expires_at
    )
    db.add(family)
    await db.flush()
    
    # Add elder as family member
    member = FamilyMember(
        family_id=family.id,
        user_id=current_user.id,
        role="elder"
    )
    db.add(member)
    
    await db.commit()
    
    return BindCodeResponse(
        bind_code=bind_code,
        expires_at=expires_at
    )


@router.post("/bind", response_model=list[FamilyMemberResponse])
async def bind_to_family(
    bind_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bind an adult to an elder's family using bind code."""
    # Find family by code
    result = await db.execute(
        select(Family).where(Family.bind_code == bind_code)
    )
    family = result.scalar_one_or_none()
    
    if not family:
        raise HTTPException(status_code=404, detail="Invalid bind code")
    
    if family.bind_code_expires_at and family.bind_code_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Bind code expired")
    
    # Check if already a member
    member_result = await db.execute(
        select(FamilyMember).where(
            and_(
                FamilyMember.family_id == family.id,
                FamilyMember.user_id == current_user.id
            )
        )
    )
    if member_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a family member")
    
    # Add adult as family member
    member = FamilyMember(
        family_id=family.id,
        user_id=current_user.id,
        role="adult"
    )
    db.add(member)
    await db.commit()
    
    # Return all family members
    members_result = await db.execute(
        select(FamilyMember).where(FamilyMember.family_id == family.id)
    )
    members = members_result.scalars().all()
    
    # Fetch user details
    response = []
    for m in members:
        user_result = await db.execute(
            select(User).where(User.id == m.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            response.append(FamilyMemberResponse(
                id=m.id,
                user_id=m.user_id,
                name=user.name,
                role=m.role,
                avatar_url=user.avatar_url,
                added_at=m.added_at
            ))
    
    return response


@router.get("/members", response_model=list[FamilyMemberResponse])
async def get_family_members(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all family members for current user."""
    # Find user's family
    member_result = await db.execute(
        select(FamilyMember).where(FamilyMember.user_id == current_user.id)
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Not in a family")
    
    # Get all members
    members_result = await db.execute(
        select(FamilyMember).where(FamilyMember.family_id == member.family_id)
    )
    members = members_result.scalars().all()
    
    response = []
    for m in members:
        user_result = await db.execute(
            select(User).where(User.id == m.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            response.append(FamilyMemberResponse(
                id=m.id,
                user_id=m.user_id,
                name=user.name,
                role=m.role,
                avatar_url=user.avatar_url,
                added_at=m.added_at
            ))
    
    return response


@router.get("/progress/{elder_id}", response_model=FamilyProgressResponse)
async def get_elder_progress(
    elder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific elder in the family."""
    # Verify current user is an adult in the same family
    adult_member_result = await db.execute(
        select(FamilyMember).where(
            and_(
                FamilyMember.user_id == current_user.id,
                FamilyMember.role == "adult"
            )
        )
    )
    adult_member = adult_member_result.scalar_one_or_none()
    
    if not adult_member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find elder in same family
    elder_member_result = await db.execute(
        select(FamilyMember).where(
            and_(
                FamilyMember.family_id == adult_member.family_id,
                FamilyMember.user_id == elder_id,
                FamilyMember.role == "elder"
            )
        )
    )
    elder_member = elder_member_result.scalar_one_or_none()
    
    if not elder_member:
        raise HTTPException(status_code=404, detail="Elder not found in family")
    
    # Get elder's user info
    elder_result = await db.execute(
        select(User).where(User.id == elder_id)
    )
    elder = elder_result.scalar_one_or_none()
    
    # Calculate weekly progress (reuse logic from training endpoint)
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    from app.models.models import DailyCheckin, TrainingSession
    
    checkins_result = await db.execute(
        select(DailyCheckin).where(
            DailyCheckin.user_id == elder_id,
            DailyCheckin.checkin_date >= week_ago,
            DailyCheckin.completed == True
        )
    )
    checkins = checkins_result.scalars().all()
    
    # Calculate total duration
    total_duration = 0
    for checkin in checkins:
        session_result = await db.execute(
            select(TrainingSession).where(
                TrainingSession.user_id == elder_id,
                TrainingSession.completed_at >= datetime.combine(checkin.checkin_date, datetime.min.time())
            )
        )
        sessions = session_result.scalars().all()
        for s in sessions:
            if s.duration_sec:
                total_duration += s.duration_sec
    
    # Calculate streak
    streak = 0
    check_date = today
    while True:
        check_result = await db.execute(
            select(DailyCheckin).where(
                DailyCheckin.user_id == elder_id,
                DailyCheckin.checkin_date == check_date,
                DailyCheckin.completed == True
            )
        )
        if check_result.scalar_one_or_none():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Get last training time
    last_session_result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.user_id == elder_id)
        .order_by(TrainingSession.completed_at.desc())
        .limit(1)
    )
    last_session = last_session_result.scalar_one_or_none()
    
    return FamilyProgressResponse(
        elder_id=elder_id,
        elder_name=elder.name if elder else "Unknown",
        weekly_checkins=len(checkins),
        total_duration_min=total_duration // 60,
        streak_days=streak,
        last_training_at=last_session.completed_at if last_session else None
    )