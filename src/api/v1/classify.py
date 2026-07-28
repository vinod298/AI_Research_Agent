from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.classification.inference import classifier_inference
from src.core.exceptions import BadRequestException, EntityNotFoundException
from src.models.user import User
from src.repositories.analytics_repository import AnalyticsRepository
from src.repositories.document_repository import DocumentChunkRepository, DocumentRepository
from src.schemas.classification import ClassifyRequest, ClassifyResponse

router = APIRouter(prefix="/classify", tags=["TensorFlow Category Classifier"])


@router.post("", response_model=ClassifyResponse)
async def classify_text_or_document(
    request: ClassifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Classify text or document into 10 enterprise AI domains using TensorFlow model:
    AI, Machine Learning, Cyber Security, Cloud, Computer Vision, Robotics, NLP, Blockchain, IoT, Data Science.
    """
    text_to_classify = ""
    if request.text:
        text_to_classify = request.text
    elif request.document_id:
        doc_repo = DocumentRepository(db)
        chunk_repo = DocumentChunkRepository(db)
        doc = await doc_repo.get_by_id(request.document_id)
        if not doc:
            raise EntityNotFoundException("Document", request.document_id)
        chunks = await chunk_repo.get_by_document(doc.id)
        text_to_classify = " ".join([c.content for c in chunks[:5]])
    else:
        raise BadRequestException("Either 'text' or 'document_id' must be provided.")

    res = classifier_inference.classify_text(text_to_classify)

    analytics_repo = AnalyticsRepository(db)
    await analytics_repo.log_event(
        event_type="classification",
        user_id=current_user.id,
        latency_ms=res.latency_ms,
        details={"category": res.predicted_category, "confidence": res.confidence}
    )

    return res
