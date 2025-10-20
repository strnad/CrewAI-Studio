"""
Health Check API
Provides system status and diagnostics
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bend.database.connection import get_db_session

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    Returns API status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "CrewAI Studio API",
    }


@router.get("/health/detailed")
async def detailed_health_check(db=Depends(get_db_session)):
    """
    Detailed health check with database connectivity
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "CrewAI Studio API",
        "components": {},
    }

    # Check database connection
    try:
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }

    return health_status


@router.get("/version")
async def version_info():
    """
    API version information
    """
    return {
        "api_version": "1.0.0",
        "python_version": sys.version,
        "build_date": "2025-10-20",
    }
