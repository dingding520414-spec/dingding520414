from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.db.database import init_db, close_db
from app.api.v1.endpoints import auth, users, courses, training, family, subscription, webhooks

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users, prefix="/api/v1/users", tags=["users"])
app.include_router(courses, prefix="/api/v1/courses", tags=["courses"])
app.include_router(training, prefix="/api/v1/training", tags=["training"])
app.include_router(family, prefix="/api/v1/family", tags=["family"])
app.include_router(subscription, prefix="/api/v1/subscription", tags=["subscription"])
app.include_router(webhooks, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }