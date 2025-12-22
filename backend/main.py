"""
Main FastAPI application for Multi-Agent RCA Platform.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import structlog

from api.v1 import rca, rag, websocket
from core.config import settings
from core.logging import setup_logging
from database.session import engine, init_db
# from middleware.rate_limit import RateLimitMiddleware
# from middleware.request_id import RequestIDMiddleware

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    logger.info("starting_application", environment=settings.ENVIRONMENT)
    
    # Initialize database
    await init_db()
    logger.info("database_initialized")
    
    # TODO: Initialize vector database connection
    # TODO: Initialize Redis connection
    # TODO: Load agent configurations
    
    yield
    
    # Shutdown
    logger.info("shutting_down_application")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Test Failure RCA Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware (TODO: implement these)
# app.add_middleware(RequestIDMiddleware)
# app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.API_RATE_LIMIT)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# API routes
app.include_router(rca.router, prefix=settings.API_V1_STR)
app.include_router(rag.router, prefix=settings.API_V1_STR)
app.include_router(websocket.router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/db")
async def health_check_db():
    """Database health check."""
    try:
        from database.session import AsyncSession
        async with AsyncSession() as session:
            await session.execute("SELECT 1")
        return {"status": "healthy", "service": "postgresql"}
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "service": "postgresql", "error": str(e)},
        )


@app.get("/health/redis")
async def health_check_redis():
    """Redis health check."""
    try:
        from core.cache import redis_client
        await redis_client.ping()
        return {"status": "healthy", "service": "redis"}
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "service": "redis", "error": str(e)},
        )


@app.get("/health/vectordb")
async def health_check_vectordb():
    """Vector database health check."""
    try:
        from vector_db.client import qdrant_client
        collections = await qdrant_client.get_collections()
        return {
            "status": "healthy",
            "service": "qdrant",
            "collections_count": len(collections.collections),
        }
    except Exception as e:
        logger.error("vectordb_health_check_failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "service": "qdrant", "error": str(e)},
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_config=None,  # Use our custom logging
    )
