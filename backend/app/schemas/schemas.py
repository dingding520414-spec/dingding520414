from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============ Auth ============
class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    role: str = Field(default="elder")  # 'elder' or 'adult'

    @field_validator('email', 'phone')
    def at_least_one_contact(cls, v, info):
        if not v and not info.data.get('phone') and not info.data.get('email'):
            raise ValueError('Either email or phone must be provided')
        return v


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @field_validator('email', 'phone')
    def at_least_one_contact(cls, v, info):
        if not v and not info.data.get('phone') and not info.data.get('email'):
            raise ValueError('Either email or phone must be provided')
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ============ User ============
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = None
    fitness_goal: Optional[str] = None
    health_notes: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: Optional[str] = None
    phone: Optional[str] = None
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    fitness_goal: Optional[str] = None
    health_notes: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Family ============
class BindCodeResponse(BaseModel):
    bind_code: str
    expires_at: datetime


class FamilyMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    role: str
    avatar_url: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True


class FamilyProgressResponse(BaseModel):
    elder_id: UUID
    elder_name: str
    weekly_checkins: int
    total_duration_min: int
    streak_days: int
    last_training_at: Optional[datetime] = None


# ============ Course ============
class ExerciseResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    reps: Optional[int] = None
    duration_sec: Optional[int] = None
    video_timestamp: Optional[int] = None
    order_index: int

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    difficulty: int
    duration_min: Optional[int] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    exercises: List[ExerciseResponse] = []

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    courses: List[CourseResponse]
    total: int


# ============ Course Progress (MUST be before Training schemas) ============
class CourseProgressItem(BaseModel):
    course_id: UUID
    course_title: str
    completion_count: int
    is_mastered: bool
    mastered_at: Optional[datetime] = None
    last_completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseProgressResponse(BaseModel):
    total_courses: int
    mastered_courses: int  # Number of courses with is_mastered=True
    completion_percentage: float  # 0-100
    courses: List[CourseProgressItem]


class CourseMasteryResponse(BaseModel):
    course_id: UUID
    course_title: str
    completion_count: int
    is_mastered: bool
    required_completions: int = 3
    progress_percentage: float  # completion_count / required_completions * 100
    message: str  # e.g., "再来2次就能掌握本课程了！"


# ============ Training ============
class TrainingStartRequest(BaseModel):
    course_id: UUID


class TrainingStartResponse(BaseModel):
    session_id: UUID
    start_time: datetime


class TrainingCompleteRequest(BaseModel):
    duration_sec: int
    ai_score: Optional[int] = Field(None, ge=0, le=100)


class TrainingCompleteResponse(BaseModel):
    session_id: UUID
    duration_sec: int
    ai_score: Optional[int] = None
    checkin_id: UUID
    course_progress: Optional[CourseMasteryResponse] = None


class AIFeedbackRequest(BaseModel):
    exercise_id: UUID
    video_segment_base64: Optional[str] = None  # Base64 encoded video frame


class AIFeedbackResponse(BaseModel):
    score: int  # 0-100
    feedback_text: str
    suggestions: List[str] = []


# ============ Progress ============
class WeeklyProgressResponse(BaseModel):
    checkins: List["DailyCheckinResponse"]
    total_duration_min: int
    streak_days: int


class DailyCheckinResponse(BaseModel):
    id: UUID
    checkin_date: datetime
    course_title: Optional[str] = None
    completed: bool

    class Config:
        from_attributes = True


class MonthlyReportResponse(BaseModel):
    report_url: str  # URL to PDF report
    generated_at: datetime


# ============ Subscription ============
class SubscriptionCreateRequest(BaseModel):
    plan_type: str = Field(..., pattern="^(personal|family)$")
    interval: str = Field(default="month", pattern="^(month|year)$")


class SubscriptionResponse(BaseModel):
    id: UUID
    plan_type: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionStatusResponse(BaseModel):
    subscription: Optional[SubscriptionResponse] = None
    plan_type: str
    is_active: bool
    current_period_end: Optional[datetime] = None
    trial_days_remaining: int = 0


# Update forward references
TokenResponse.model_rebuild()
WeeklyProgressResponse.model_rebuild()
