from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.search import SearchQuery, SearchResponse
from src.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Semantic & Hybrid Search"])


@router.post("", response_model=SearchResponse)
async def search(
    query: SearchQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform semantic, keyword, or hybrid retrieval using Qdrant vector store and BM25 search.
    """
    service = SearchService(db)
    res = await service.search(query)

    # Log analytics
    analytics_repo = AnalyticsRepository(db)
    await analytics_repo.log_event(
        event_type="search",
        user_id=current_user.id,
        latency_ms=res.latency_ms,
        details={"query": query.query, "search_type": query.search_type, "results_count": res.total_results}
    )

    return res
