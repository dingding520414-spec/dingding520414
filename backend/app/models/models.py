import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import TypeDecorator, CHAR
from app.db.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses PostgreSQL's UUID type or CHAR(36) for others."""
    impl = CHAR
    cache_ok = True

    def __init__(self):
        super().__init__(36)
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return UUID()
        return CHAR(36)


class User(Base):
    """User model - both elders and adults."""
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    fitness_goal = Column(Text, nullable=True)
    health_notes = Column(Text, nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family_memberships = relationship("FamilyMember", back_populates="user")
    training_sessions = relationship("TrainingSession", back_populates="user")
    checkins = relationship("DailyCheckin", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)


class Family(Base):
    """Family grouping."""
    __tablename__ = "families"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    bind_code = Column(String(8), unique=True, nullable=True)
    bind_code_expires_at = Column(DateTime, nullable=True)

    # Relationships
    members = relationship("FamilyMember", back_populates="family")


class FamilyMember(Base):
    """Family member association with role."""
    __tablename__ = "family_members"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    family_id = Column(GUID(), ForeignKey("families.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'elder' or 'adult'
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    family = relationship("Family", back_populates="members")
    user = relationship("User", back_populates="family_memberships")

    __table_args__ = (
        UniqueConstraint('family_id', 'user_id', name='uq_family_member'),
    )


class Course(Base):
    """Training course."""
    __tablename__ = "courses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, default=1)  # 1-5
    duration_min = Column(Integer, nullable=True)
    video_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exercises = relationship("Exercise", back_populates="course", order_by="Exercise.order_index")
    training_sessions = relationship("TrainingSession", back_populates="course")


class Exercise(Base):
    """Exercise within a course."""
    __tablename__ = "exercises"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reps = Column(Integer, nullable=True)
    duration_sec = Column(Integer, nullable=True)
    video_timestamp = Column(Integer, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="exercises")


class TrainingSession(Base):
    """Training session record."""
    __tablename__ = "training_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_sec = Column(Integer, nullable=True)
    ai_score = Column(Integer, nullable=True)  # 0-100

    # Relationships
    user = relationship("User", back_populates="training_sessions")
    course = relationship("Course", back_populates="training_sessions")


class DailyCheckin(Base):
    """Daily training check-in."""
    __tablename__ = "daily_checkins"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    checkin_date = Column(DateTime, nullable=False)
    course_id = Column(GUID(), ForeignKey("courses.id"), nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="checkins")
    course = relationship("Course")

    __table_args__ = (
        UniqueConstraint('user_id', 'checkin_date', name='uq_user_checkin_date'),
    )


class Subscription(Base):
    """User subscription."""
    __tablename__ = "subscriptions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, unique=True)
    plan_type = Column(String(20), default="free")  # 'free', 'personal', 'family'
    status = Column(String(20), default="active")  # 'active', 'cancelled', 'expired'
    stripe_subscription_id = Column(String(255), nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")