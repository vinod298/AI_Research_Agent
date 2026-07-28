from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.rag import CompareRequest, CompareResponse
from src.services.rag_service import RAGService

router = APIRouter(prefix="/compare", tags=["Document Comparison"])


@router.post("", response_model=CompareResponse)
async def compare_documents(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple research documents side-by-side across core aspects.
    Evaluates: Methodology, Advantages, Disadvantages, Architecture, Complexity, Conclusion.
    """
    service = RAGService(db)
    res = await service.compare(request)

    analytics_repo = AnalyticsRepository(db)
    await analytics_repo.log_event(
        event_type="compare",
        user_id=current_user.id,
        latency_ms=res.latency_ms,
        details={"doc_count": len(request.document_ids)}
    )

    return res
