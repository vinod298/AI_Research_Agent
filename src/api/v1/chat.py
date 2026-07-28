from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.schemas.rag import ChatRequest, ChatResponse
from src.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["RAG QA Engine"])


@router.post("", response_model=ChatResponse)
async def chat_rag(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    RAG Question-Answering Endpoint with Conversation Memory & Inline Citations.
    Strictly anti-hallucinating pipeline: Question -> Hybrid Retrieval -> Context Prompt -> LLM -> Citations.
    """
    service = RAGService(db)
    res = await service.chat(request, user_id=current_user.id)

    # Log analytics
    analytics_repo = AnalyticsRepository(db)
    await analytics_repo.log_event(
        event_type="chat_query",
        user_id=current_user.id,
        latency_ms=res.latency_ms,
        details={"question": request.question, "llm_provider": res.llm_provider, "confidence": res.confidence_score}
    )

    return res
