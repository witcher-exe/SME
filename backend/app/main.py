from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.dependencies import init_db, engine
from app.api.router import api_router
from app.models.schemas import ErrorResponse
from app.security.permission_service import PermissionDenied

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AuraCFO")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup checks and resource teardown."""
    logger.info("Starting up AuraCFO backend server...")
    
    # 1. Initialize DB tables
    await init_db()
    logger.info("Database schema initialized.")

    # 2. Check LLM availability / activate mock mode
    if not settings.LLM_API_KEY:
        settings.MOCK_LLM = True
        logger.info("No LLM API key detected. MOCK_LLM auto-activated for offline evaluation.")
    else:
        logger.info(f"LLM Provider configured: {settings.LLM_PROVIDER} ({settings.LLM_MODEL}).")

    # 3. Auto-seed benchmark on empty database (Winning Factor #4)
    try:
        from app.dependencies import async_session_factory
        from app.models.company import Company
        from app.services.benchmark_service import BenchmarkService
        from sqlalchemy import select

        async with async_session_factory() as s:
            has_comp = (await s.execute(select(Company))).scalars().first()
            if not has_comp:
                logger.info("Empty database detected. Auto-seeding Bengal Craft & Retail benchmark dataset...")
                await BenchmarkService.seed_scenario(async_session_factory)
                logger.info("Bengal Craft benchmark auto-seeded successfully.")
    except Exception as e:
        logger.warning(f"Startup auto-seed check skipped or failed: {e}")

    yield

    logger.info("Shutting down AuraCFO backend...")
    await engine.dispose()
    logger.info("Database connections closed.")

app = FastAPI(
    title="AuraCFO API",
    description="Autonomous Virtual CFO for SMEs — FinTechathon 2026 Topic E",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(PermissionDenied)
async def permission_denied_handler(request: Request, exc: PermissionDenied):
    logger.warning(f"Permission denied: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ErrorResponse(
            error="Permission Denied",
            detail=str(exc),
            code="PERMISSION_DENIED"
        ).model_dump()
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Financial engines preserved state integrity.",
            code="INTERNAL_ERROR"
        ).model_dump()
    )

# Mount master API router
app.include_router(api_router)

@app.get("/", tags=["System"])
async def root():
    return {
        "service": "AuraCFO Backend API",
        "version": "0.1.0",
        "docs_url": "/docs",
        "mock_llm": settings.MOCK_LLM
    }
