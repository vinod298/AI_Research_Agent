from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.analytics_repository import AnalyticsRepository
from src.repositories.chat_repository import ChatRepository
from src.repositories.document_repository import DocumentChunkRepository, DocumentRepository
from src.repositories.user_repository import UserRepository
from src.schemas.analytics import AnalyticsOverview, CategoryDistribution, LatencyStats, SystemMetrics


class AnalyticsService:
    def __init__(self, db_session: AsyncSession):
        self.doc_repo = DocumentRepository(db_session)
        self.chunk_repo = DocumentChunkRepository(db_session)
        self.user_repo = UserRepository(db_session)
        self.chat_repo = ChatRepository(db_session)
        self.analytics_repo = AnalyticsRepository(db_session)

    async def get_overview(self) -> AnalyticsOverview:
        total_docs = await self.doc_repo.count()
        total_chunks = await self.chunk_repo.count()
        total_pages = await self.doc_repo.total_pages_processed()
        total_sessions = await self.chat_repo.count()
        total_events = await self.analytics_repo.count()
        total_users = await self.user_repo.count()

        metrics = SystemMetrics(
            total_documents=total_docs,
            total_chunks=total_chunks,
            total_pages_processed=total_pages,
            total_chat_sessions=total_sessions,
            total_queries_executed=total_events,
            total_users=total_users
        )

        cat_dist = await self.doc_repo.get_category_distribution()
        cat_items = [CategoryDistribution(category=item["category"], count=item["count"]) for item in cat_dist]

        avg_search = await self.analytics_repo.get_average_latency("search")
        avg_rag = await self.analytics_repo.get_average_latency("chat_query")
        avg_class = await self.analytics_repo.get_average_latency("classification")

        latency = LatencyStats(
            avg_search_latency_ms=round(avg_search, 2),
            avg_rag_latency_ms=round(avg_rag, 2),
            avg_classification_latency_ms=round(avg_class, 2)
        )

        return AnalyticsOverview(
            metrics=metrics,
            category_distribution=cat_items,
            latency=latency,
            recent_events_count=total_events
        )
