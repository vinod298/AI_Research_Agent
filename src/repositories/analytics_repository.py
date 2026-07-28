from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.analytics import AnalyticsEvent, ProcessingLog
from src.repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository[AnalyticsEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(AnalyticsEvent, session)

    async def log_event(self, event_type: str, user_id: Optional[str] = None, latency_ms: float = 0.0, status_code: int = 200, details: Optional[dict] = None) -> AnalyticsEvent:
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            latency_ms=latency_ms,
            status_code=status_code,
            details=details or {}
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_average_latency(self, event_type: str) -> float:
        stmt = select(func.avg(AnalyticsEvent.latency_ms)).where(AnalyticsEvent.event_type == event_type)
        res = await self.session.execute(stmt)
        return res.scalar() or 0.0


class ProcessingLogRepository(BaseRepository[ProcessingLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProcessingLog, session)

    async def log_step(self, document_id: str, step: str, status: str, duration_ms: float, message: Optional[str] = None) -> ProcessingLog:
        log_entry = ProcessingLog(
            document_id=document_id,
            step=step,
            status=status,
            duration_ms=duration_ms,
            message=message
        )
        self.session.add(log_entry)
        await self.session.flush()
        return log_entry
