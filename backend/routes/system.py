from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..database.database import get_db
from ..utils.api_response import success_response

router = APIRouter(prefix="/api/v1/system", tags=["System & Health"])


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Standardized health check endpoint for deployment orchestration (Railway, Vercel)."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return success_response(
        data={
            "status": "healthy" if db_status == "connected" else "degraded",
            "database": db_status,
            "environment": settings.ENVIRONMENT,
        },
        message="System health check completed",
    )
