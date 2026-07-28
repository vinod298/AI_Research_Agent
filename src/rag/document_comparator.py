import time
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.document import Document
from src.rag.llm_provider import llm_factory
from src.repositories.document_repository import DocumentRepository, DocumentChunkRepository
from src.schemas.rag import CompareRequest, CompareResponse, ComparisonMatrixItem


class DocumentComparator:
    """Evaluates and compares multiple research documents across key dimensions."""

    def __init__(self, db_session: AsyncSession):
        self.doc_repo = DocumentRepository(db_session)
        self.chunk_repo = DocumentChunkRepository(db_session)

    async def compare_documents(self, request: CompareRequest) -> CompareResponse:
        start_time = time.time()
        docs: List[Document] = []
        doc_texts: Dict[str, str] = {}
        compared_info: List[Dict[str, str]] = []

        for doc_id in request.document_ids:
            doc = await self.doc_repo.get_by_id(doc_id)
            if doc:
                docs.append(doc)
                chunks = await self.chunk_repo.get_by_document(doc.id)
                text = " ".join([c.content for c in chunks[:5]]) # Take top chunks
                doc_texts[doc.id] = text[:2000]
                compared_info.append({
                    "id": doc.id,
                    "title": doc.title,
                    "filename": doc.filename,
                    "category": doc.predicted_category or "General"
                })

        aspects = request.aspects or ["Methodology", "Advantages", "Disadvantages", "Architecture", "Complexity", "Conclusion"]
        matrix: List[ComparisonMatrixItem] = []

        for aspect in aspects:
            summaries: Dict[str, str] = {}
            for doc in docs:
                txt = doc_texts.get(doc.id, "")
                prompt = f"Excerpt from '{doc.filename}':\n{txt}\n\nTask: Provide a concise summary of the '{aspect}' for this document."
                provider = llm_factory.get_provider(request.llm_provider)
                analysis = await provider.generate_response(prompt)
                summaries[doc.filename] = analysis.strip()
            
            matrix.append(ComparisonMatrixItem(aspect=aspect, document_summaries=summaries))

        narrative_prompt = f"Based on the comparison of {len(docs)} documents ({', '.join([d.filename for d in docs])}), synthesize an overall narrative analysis."
        provider = llm_factory.get_provider(request.llm_provider)
        narrative = await provider.generate_response(narrative_prompt)
        conclusion = f"Document evaluation completed across {len(aspects)} core criteria."

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return CompareResponse(
            compared_documents=compared_info,
            comparison_table=matrix,
            narrative_analysis=narrative,
            conclusion=conclusion,
            latency_ms=latency_ms
        )
