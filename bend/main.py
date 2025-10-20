"""
CrewAI Studio - REST API Backend
FastAPI application with Keycloak-ready authentication
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sys
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bend.config import settings
from bend.api import health, crews, agents, tasks, tools

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=settings.api_docs_url if settings.debug else None,
    redoc_url=settings.api_redoc_url if settings.debug else None,
    openapi_url=f"{settings.api_prefix}/openapi.json" if settings.debug else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": f"{settings.api_docs_url}" if settings.debug else "disabled in production",
        "keycloak_enabled": settings.keycloak_enabled,
    }


# Include routers
app.include_router(health.router, prefix=settings.api_prefix, tags=["Health"])
app.include_router(crews.router, prefix=f"{settings.api_prefix}/crews", tags=["Crews"])
app.include_router(agents.router, prefix=f"{settings.api_prefix}/agents", tags=["Agents"])
app.include_router(tasks.router, prefix=f"{settings.api_prefix}/tasks", tags=["Tasks"])
app.include_router(tools.router, prefix=f"{settings.api_prefix}/tools", tags=["Tools"])


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
