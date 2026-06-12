from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db
from app.models.models import Course, Exercise, User
from app.schemas.schemas import CourseResponse, CourseListResponse, ExerciseResponse
from app.core.deps import get_current_user
from typing import Optional, List
from uuid import UUID

router = APIRouter()


@router.get("", response_model=CourseListResponse)
async def list_courses(
    difficulty: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all active courses."""
    query = select(Course).where(Course.is_active == True)
    
    if difficulty:
        query = query.where(Course.difficulty == difficulty)
    
    # Get total count
    count_query = select(func.count(Course.id)).where(Course.is_active == True)
    if difficulty:
        count_query = count_query.where(Course.difficulty == difficulty)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get courses
    query = query.order_by(Course.difficulty, Course.created_at)
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    courses = result.scalars().all()
    
    # Fetch exercises for each course
    course_responses = []
    for course in courses:
        exercises_result = await db.execute(
            select(Exercise)
            .where(Exercise.course_id == course.id)
            .order_by(Exercise.order_index)
        )
        exercises = exercises_result.scalars().all()
        
        course_responses.append(CourseResponse(
            id=course.id,
            title=course.title,
            description=course.description,
            difficulty=course.difficulty,
            duration_min=course.duration_min,
            video_url=course.video_url,
            thumbnail_url=course.thumbnail_url,
            exercises=[
                ExerciseResponse(
                    id=ex.id,
                    name=ex.name,
                    description=ex.description,
                    reps=ex.reps,
                    duration_sec=ex.duration_sec,
                    video_timestamp=ex.video_timestamp,
                    order_index=ex.order_index
                )
                for ex in exercises
            ]
        ))
    
    return CourseListResponse(courses=course_responses, total=total)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get course details with exercises."""
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.is_active == True)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    exercises_result = await db.execute(
        select(Exercise)
        .where(Exercise.course_id == course.id)
        .order_by(Exercise.order_index)
    )
    exercises = exercises_result.scalars().all()
    
    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        difficulty=course.difficulty,
        duration_min=course.duration_min,
        video_url=course.video_url,
        thumbnail_url=course.thumbnail_url,
        exercises=[
            ExerciseResponse(
                id=ex.id,
                name=ex.name,
                description=ex.description,
                reps=ex.reps,
                duration_sec=ex.duration_sec,
                video_timestamp=ex.video_timestamp,
                order_index=ex.order_index
            )
            for ex in exercises
        ]
    )