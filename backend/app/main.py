"""
AgentCrashLab — FastAPI Application

"Break AI agents before they break production."
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, Base
from app.api.health import router as health_router
from app.api.agents import router as agents_router
from app.api.scenarios import router as scenarios_router
from app.api.test_runs import router as test_runs_router

# Import models so Alembic can detect them
import app.models  # noqa: F401
import structlog
import logging

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    # Startup: verify database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))

    yield

    # Shutdown
    engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(
    title="AgentCrashLab",
    description="Break AI agents before they break production. "
    "An AI Agent Reliability Testing Platform.",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router, prefix="/api")
app.include_router(agents_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(test_runs_router, prefix="/api")


@app.get("/", tags=["root"])
def root():
    """Root endpoint — API information."""
    return {
        "name": "AgentCrashLab",
        "tagline": "Break AI agents before they break production.",
        "version": settings.app_version,
        "docs": "/docs",
    }
