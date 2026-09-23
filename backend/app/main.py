"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import get_settings
from backend.app.models.database import create_tables, get_engine
from backend.app.api import health, resume, interview, roles, results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()

    # Ensure directories exist
    settings.upload_directory.mkdir(parents=True, exist_ok=True)
    settings.data_directory.mkdir(parents=True, exist_ok=True)
    settings.chroma_directory.mkdir(parents=True, exist_ok=True)

    # Create database tables
    engine = get_engine()
    create_tables(engine)

    # Warm up embedding model in background thread or lazily
    import threading
    def _warmup():
        try:
            from backend.app.services.embedding_service import generate_embedding
            generate_embedding("warmup")
        except Exception as e:
            logger.warning(f"Embedding model warmup warning: {e}")
    threading.Thread(target=_warmup, daemon=True).start()

    logger.info("="*60)
    logger.info("AI Interview System started")
    logger.info(f"  LLM Mode: {'Real' if settings.is_llm_available else 'Mock/Demo'}")
    logger.info(f"  Database: {settings.database_url}")
    logger.info(f"  Embedding Model: {settings.embedding_model}")
    logger.info(f"  ChromaDB: {settings.chroma_directory}")
    logger.info(f"  Questions per interview: {settings.interview_question_count}")
    logger.info("="*60)

    yield

    logger.info("AI Interview System shutting down")


# Create FastAPI app
app = FastAPI(
    title="AI Interview System",
    description="AI-powered role-based candidate screening and technical interview system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
# In production, set FRONTEND_URL to the exact deployed origin(s) (comma
# separated for multiple). The localhost entries below are dev-only
# conveniences and are harmless to keep in production since browsers only
# send matching Origin headers from those exact hosts.
settings = get_settings()
_cors_origins = list(dict.fromkeys(
    settings.cors_allowed_origins + [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router, prefix="/api")
app.include_router(health.router)
app.include_router(resume.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(results.router, prefix="/api")

# Mount static frontend files if built
frontend_dist = settings.project_root / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static_frontend")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return clean error response."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again.",
            "error_code": "INTERNAL_ERROR",
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError as 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_code": "VALIDATION_ERROR"},
    )
