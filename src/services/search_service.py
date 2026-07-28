import time
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.rag.embeddings import embedding_service
from src.repositories.document_repository import DocumentChunkRepository
from src.schemas.search import SearchQuery, SearchResponse, SearchResultItem
from src.vector_store.hybrid_search import hybrid_search_engine
from src.vector_store.qdrant_client import VectorSearchResult, qdrant_store


class SearchService:
    def __init__(self, db_session: AsyncSession):
        self.chunk_repo = DocumentChunkRepository(db_session)

    async def search(self, query: SearchQuery) -> SearchResponse:
        start_time = time.time()
        search_type = query.search_type.lower()

        vector_results: List[VectorSearchResult] = []
        if search_type in ["semantic", "hybrid"]:
            query_vec = embedding_service.embed_text(query.query)
            vector_results = qdrant_store.search_vectors(
                query_vector=query_vec,
                top_k=query.top_k,
                document_ids=query.document_ids,
                category_filter=query.category_filter
            )

        bm25_results = []
        if search_type in ["keyword", "hybrid"]:
            corpus_chunks = []
            if query.document_ids:
                for doc_id in query.document_ids:
                    db_chunks = await self.chunk_repo.get_by_document(doc_id)
                    for c in db_chunks:
                        corpus_chunks.append({
                            "chunk_id": c.id,
                            "document_id": c.document_id,
                            "filename": c.document.filename if c.document else "Document",
                            "doc_title": c.document.title if c.document else "Document",
                            "page_number": c.page_number,
                            "content": c.content,
                            "metadata": c.chunk_metadata or {}
                        })
            else:
                db_chunks = await self.chunk_repo.get_all_with_document(limit=1000)
                for c in db_chunks:
                    corpus_chunks.append({
                        "chunk_id": c.id,
                        "document_id": c.document_id,
                        "filename": c.document.filename if c.document else "Document",
                        "doc_title": c.document.title if c.document else "Document",
                        "page_number": c.page_number,
                        "content": c.content,
                        "metadata": c.chunk_metadata or {}
                    })

            bm25_results = hybrid_search_engine.bm25_search(
                query=query.query,
                corpus_chunks=corpus_chunks,
                top_k=query.top_k
            )

        combined_items = hybrid_search_engine.combine_rrf(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=query.top_k
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return SearchResponse(
            query=query.query,
            search_type=search_type,
            total_results=len(combined_items),
            results=combined_items,
            latency_ms=latency_ms
        )
