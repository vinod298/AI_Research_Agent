from sqlalchemy.ext.asyncio import AsyncSession
from src.rag.document_comparator import DocumentComparator
from src.rag.rag_pipeline import RAGPipeline
from src.rag.summarizer import MultiGranularitySummarizer
from src.schemas.rag import (
    ChatRequest, ChatResponse,
    CompareRequest, CompareResponse,
    SummarizeRequest, SummarizeResponse
)


class RAGService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.pipeline = RAGPipeline(db_session)
        self.comparator = DocumentComparator(db_session)
        self.summarizer = MultiGranularitySummarizer(db_session)

    async def chat(self, request: ChatRequest, user_id: str) -> ChatResponse:
        return await self.pipeline.execute_rag(request, user_id)

    async def compare(self, request: CompareRequest) -> CompareResponse:
        return await self.comparator.compare_documents(request)

    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        return await self.summarizer.summarize_document(request)
