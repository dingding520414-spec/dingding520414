from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.database import get_db
from app.models.models import User, Course, TrainingSession, DailyCheckin, CourseProgress
from app.schemas.schemas import (
    TrainingStartRequest, TrainingStartResponse,
    TrainingCompleteRequest, TrainingCompleteResponse,
    AIFeedbackRequest, AIFeedbackResponse,
    WeeklyProgressResponse, DailyCheckinResponse,
    MonthlyReportResponse,
    CourseProgressResponse, CourseProgressItem, CourseMasteryResponse
)
from app.core.deps import get_current_user
from datetime import datetime, timedelta, date
from uuid import UUID

router = APIRouter()


@router.post("/start", response_model=TrainingStartResponse)
async def start_training(
    data: TrainingStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a training session."""
    # Verify course exists
    result = await db.execute(
        select(Course).where(Course.id == data.course_id, Course.is_active == True)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Create session
    session = TrainingSession(
        user_id=current_user.id,
        course_id=data.course_id,
        started_at=datetime.utcnow()
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return TrainingStartResponse(
        session_id=session.id,
        start_time=session.started_at
    )


@router.post("/{session_id}/complete", response_model=TrainingCompleteResponse)
async def complete_training(
    session_id: UUID,
    data: TrainingCompleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a training session and create check-in."""
    result = await db.execute(
        select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.completed_at:
        raise HTTPException(status_code=400, detail="Session already completed")
    
    # Update session
    session.completed_at = datetime.utcnow()
    session.duration_sec = data.duration_sec
    session.ai_score = data.ai_score
    
    # Create or update daily check-in (one per day per user)
    today = datetime.combine(date.today(), datetime.min.time())
    tomorrow = today.replace(hour=23, minute=59, second=59)
    with db.no_autoflush:
        checkin_result = await db.execute(
            select(DailyCheckin).where(
                DailyCheckin.user_id == current_user.id,
                DailyCheckin.checkin_date >= today,
                DailyCheckin.checkin_date <= tomorrow
            )
        )
        checkin = checkin_result.scalar_one_or_none()
        if checkin:
            # Already checked in today, just update
            checkin.completed = True
            checkin.course_id = session.course_id
        else:
            # New check-in
            checkin = DailyCheckin(
                user_id=current_user.id,
                checkin_date=today,
                course_id=session.course_id,
                completed=True
            )
            db.add(checkin)
    
    # Update course progress
    MASTERY_THRESHOLD = 3
    progress_result = await db.execute(
        select(CourseProgress).where(
            CourseProgress.user_id == current_user.id,
            CourseProgress.course_id == session.course_id
        )
    )
    progress = progress_result.scalar_one_or_none()
    
    now = datetime.utcnow()
    if progress:
        progress.completion_count += 1
        progress.last_completed_at = now
        if progress.completion_count >= MASTERY_THRESHOLD and not progress.is_mastered:
            progress.is_mastered = True
            progress.mastered_at = now
    else:
        is_mastered = False
        mastered_at = None
        if 1 >= MASTERY_THRESHOLD:
            is_mastered = True
            mastered_at = now
        progress = CourseProgress(
            user_id=current_user.id,
            course_id=session.course_id,
            completion_count=1,
            is_mastered=is_mastered,
            mastered_at=mastered_at,
            last_completed_at=now
        )
        db.add(progress)
    
    await db.commit()
    await db.refresh(session)
    await db.refresh(checkin)
    await db.refresh(progress)
    
    # Get course title for response
    course_result = await db.execute(
        select(Course.title).where(Course.id == session.course_id)
    )
    course_title = course_result.scalar() or ""
    
    remaining = max(0, MASTERY_THRESHOLD - progress.completion_count)
    if progress.is_mastered:
        message = f"🎉 恭喜！您已完全掌握「{course_title}」！"
    elif remaining > 0:
        message = f"再来{remaining}次就能掌握「{course_title}」了！"
    else:
        message = f"再完成1次即可掌握「{course_title}」！"
    
    course_mastery = CourseMasteryResponse(
        course_id=session.course_id,
        course_title=course_title,
        completion_count=progress.completion_count,
        is_mastered=progress.is_mastered,
        required_completions=MASTERY_THRESHOLD,
        progress_percentage=min(100, progress.completion_count / MASTERY_THRESHOLD * 100),
        message=message
    )
    
    return TrainingCompleteResponse(
        session_id=session.id,
        duration_sec=session.duration_sec,
        ai_score=session.ai_score,
        checkin_id=checkin.id,
        course_progress=course_mastery
    )


@router.post("/{session_id}/ai-feedback", response_model=AIFeedbackResponse)
async def get_ai_feedback(
    session_id: UUID,
    data: AIFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI feedback for an exercise.
    Note: This is a placeholder. Real implementation would use MediaPipe
    on the video frames to analyze pose and provide feedback.
    """
    result = await db.execute(
        select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # TODO: Replace with actual MediaPipe analysis
    # For MVP, return placeholder feedback
    score = 75
    feedback_text = "动作基本标准，注意膝盖不要超过脚尖"
    suggestions = [
        "保持核心收紧",
        "下蹲时膝盖对准第二脚趾方向",
        "起身时用脚跟发力"
    ]
    
    return AIFeedbackResponse(
        score=score,
        feedback_text=feedback_text,
        suggestions=suggestions
    )


@router.get("/progress/weekly", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    user_id: UUID = Query(None),  # For adult viewing elder's progress
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly progress for current user or specified elder."""
    target_user_id = user_id if user_id else current_user.id
    
    # Verify adult can view this elder's data
    if user_id and user_id != current_user.id:
        # TODO: Add family verification
        pass
    
    # Calculate date range (last 7 days)
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    result = await db.execute(
        select(DailyCheckin)
        .where(
            DailyCheckin.user_id == target_user_id,
            DailyCheckin.checkin_date >= week_ago,
            DailyCheckin.completed == True
        )
        .order_by(DailyCheckin.checkin_date)
    )
    checkins = result.scalars().all()
    
    # Calculate stats
    total_duration = 0
    for checkin in checkins:
        session_result = await db.execute(
            select(TrainingSession).where(
                TrainingSession.user_id == target_user_id,
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
                DailyCheckin.user_id == target_user_id,
                DailyCheckin.checkin_date == check_date,
                DailyCheckin.completed == True
            )
        )
        if check_result.scalar_one_or_none():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    return WeeklyProgressResponse(
        checkins=[
            DailyCheckinResponse(
                id=c.id,
                checkin_date=c.checkin_date,
                course_title=None,  # TODO: join with course
                completed=c.completed
            )
            for c in checkins
        ],
        total_duration_min=total_duration // 60,
        streak_days=streak
    )


@router.get("/progress/monthly", response_model=MonthlyReportResponse)
async def get_monthly_report(
    user_id: UUID = Query(None),
    month: int = Query(None, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate monthly progress report as PDF."""
    # TODO: Implement PDF generation
    # For now, return placeholder URL
    
    return MonthlyReportResponse(
        report_url=f"/reports/{current_user.id}/monthly.pdf",
        generated_at=datetime.utcnow()
    )


@router.get("/progress/courses", response_model=CourseProgressResponse)
async def get_course_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all course progress for current user."""
    MASTERY_THRESHOLD = 3  # Need to complete a course 3 times to master it
    
    # Get all courses
    courses_result = await db.execute(
        select(Course).where(Course.is_active == True).order_by(Course.difficulty, Course.id)
    )
    courses = courses_result.scalars().all()
    
    # Get user's progress for all courses
    progress_result = await db.execute(
        select(CourseProgress).where(CourseProgress.user_id == current_user.id)
    )
    progress_list = progress_result.scalars().all()
    progress_map = {p.course_id: p for p in progress_list}
    
    # Build response
    course_items = []
    mastered_count = 0
    
    for course in courses:
        prog = progress_map.get(course.id)
        if prog:
            course_items.append(CourseProgressItem(
                course_id=course.id,
                course_title=course.title,
                completion_count=prog.completion_count,
                is_mastered=prog.is_mastered,
                mastered_at=prog.mastered_at,
                last_completed_at=prog.last_completed_at
            ))
            if prog.is_mastered:
                mastered_count += 1
        else:
            course_items.append(CourseProgressItem(
                course_id=course.id,
                course_title=course.title,
                completion_count=0,
                is_mastered=False,
                mastered_at=None,
                last_completed_at=None
            ))
    
    total = len(courses)
    percentage = (mastered_count / total * 100) if total > 0 else 0
    
    return CourseProgressResponse(
        total_courses=total,
        mastered_courses=mastered_count,
        completion_percentage=round(percentage, 1),
        courses=course_items
    )


@router.get("/progress/courses/{course_id}", response_model=CourseMasteryResponse)
async def get_course_mastery(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get mastery progress for a specific course."""
    MASTERY_THRESHOLD = 3
    
    # Get course
    course_result = await db.execute(
        select(Course).where(Course.id == course_id, Course.is_active == True)
    )
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Get progress
    prog_result = await db.execute(
        select(CourseProgress).where(
            CourseProgress.user_id == current_user.id,
            CourseProgress.course_id == course_id
        )
    )
    prog = prog_result.scalar_one_or_none()
    
    completion_count = prog.completion_count if prog else 0
    is_mastered = prog.is_mastered if prog else False
    remaining = max(0, MASTERY_THRESHOLD - completion_count)
    
    if is_mastered:
        message = f"🎉 恭喜！您已完全掌握「{course.title}」！"
    elif remaining > 0:
        message = f"再来{remaining}次就能掌握「{course.title}」了！"
    else:
        message = f"再完成1次即可掌握「{course.title}」！"
    
    return CourseMasteryResponse(
        course_id=course_id,
        course_title=course.title,
        completion_count=completion_count,
        is_mastered=is_mastered,
        required_completions=MASTERY_THRESHOLD,
        progress_percentage=min(100, completion_count / MASTERY_THRESHOLD * 100),
        message=message
    )