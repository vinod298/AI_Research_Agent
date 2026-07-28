from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.rag import SummarizeRequest, SummarizeResponse
from src.services.rag_service import RAGService

router = APIRouter(prefix="/summarize", tags=["Summarization Engine"])


@router.post("", response_model=SummarizeResponse)
async def summarize_document(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate multi-granularity document summaries:
    Executive, Technical, Detailed, Bullet points, Key Takeaways, Limitations, and Future Work.
    """
    service = RAGService(db)
    res = await service.summarize(request)

    analytics_repo = AnalyticsRepository(db)
    await analytics_repo.log_event(
        event_type="summarize",
        user_id=current_user.id,
        latency_ms=res.latency_ms,
        details={"document_id": request.document_id, "summary_type": request.summary_type}
    )

    return res
