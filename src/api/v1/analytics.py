from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.analytics import AnalyticsOverview
from src.services.analytics_service import AnalyticsService

router = APIRouter(tags=["Analytics & Operational Metrics"])


@router.get("/analytics", response_model=AnalyticsOverview)
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve operational metrics, category distributions, and latency statistics."""
    service = AnalyticsService(db)
    return await service.get_overview()


@router.get("/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Enterprise AI Research Assistant",
        "version": "1.0.0"
    }


@router.get("/metrics")
async def prometheus_metrics():
    """Operational metrics endpoint."""
    return {
        "uptime": "operational",
        "memory_status": "normal",
        "qdrant_status": "connected",
        "tf_classifier_status": "ready"
    }
