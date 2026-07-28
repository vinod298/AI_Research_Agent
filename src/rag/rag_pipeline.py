import time
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.rag.embeddings import embedding_service
from src.rag.llm_provider import llm_factory
from src.rag.memory import ConversationMemoryManager
from src.rag.prompts import SYSTEM_RAG_PROMPT, build_rag_prompt
from src.schemas.rag import ChatRequest, ChatResponse
from src.schemas.search import Citation, SearchResultItem
from src.vector_store.hybrid_search import hybrid_search_engine
from src.vector_store.qdrant_client import qdrant_store
from src.repositories.document_repository import DocumentChunkRepository


class RAGPipeline:
    """Core Retrieval-Augmented Generation (RAG) Orchestrator."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.memory_manager = ConversationMemoryManager(db_session)
        self.chunk_repo = DocumentChunkRepository(db_session)

    async def execute_rag(self, request: ChatRequest, user_id: str) -> ChatResponse:
        start_time = time.time()

        # 1. Memory session
        chat_session = await self.memory_manager.get_or_create_session(
            session_id=request.session_id,
            user_id=user_id,
            llm_provider=request.llm_provider or "mock"
        )
        session_id = chat_session.id
        history = await self.memory_manager.get_recent_history(session_id)

        # 2. Embedding & Hybrid Search
        query_vector = embedding_service.embed_text(request.question)
        vector_results = qdrant_store.search_vectors(
            query_vector=query_vector,
            top_k=request.top_k,
            document_ids=request.document_ids
        )

        # Retrieve DB chunks for BM25 fallback fusion
        corpus_chunks = []
        if request.document_ids:
            for doc_id in request.document_ids:
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
            query=request.question,
            corpus_chunks=corpus_chunks,
            top_k=request.top_k
        )

        combined_results: List[SearchResultItem] = hybrid_search_engine.combine_rrf(
            vector_results=vector_results,
            bm25_results=bm25_results,
            top_k=request.top_k
        )

        # 3. Construct Anti-Hallucination Prompt
        formatted_prompt = build_rag_prompt(
            question=request.question,
            retrieved_chunks=combined_results,
            conversation_history=history
        )

        # 4. LLM Generation
        provider = llm_factory.get_provider(request.llm_provider)
        answer = await provider.generate_response(
            prompt=formatted_prompt,
            system_prompt=SYSTEM_RAG_PROMPT,
            temperature=request.temperature
        )

        # 5. Extract & Build Citations
        citations: List[Citation] = []
        for item in combined_results:
            cit = Citation(
                document_id=item.document_id,
                document_title=item.document_title,
                filename=item.filename,
                page_number=item.page_number,
                chunk_id=item.chunk_id,
                relevance_score=item.score,
                snippet=item.content[:150] + "..." if len(item.content) > 150 else item.content
            )
            citations.append(cit)

        # Confidence calculation
        confidence_score = round(combined_results[0].score, 2) if combined_results else 0.0
        if "I cannot determine the answer" in answer:
            confidence_score = 0.0

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # 6. Save Conversation History
        citations_json = [c.model_dump() for c in citations]
        await self.memory_manager.save_interaction(
            session_id=session_id,
            question=request.question,
            answer=answer,
            citations=citations_json,
            latency_ms=latency_ms
        )

        return ChatResponse(
            session_id=session_id,
            question=request.question,
            answer=answer,
            citations=citations,
            confidence_score=confidence_score,
            retrieved_chunks_count=len(combined_results),
            llm_provider=request.llm_provider or "mock",
            latency_ms=latency_ms
        )
