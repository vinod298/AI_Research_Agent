import re
from typing import Any, Dict, List, Optional
from rank_bm25 import BM25Okapi
from src.vector_store.qdrant_client import VectorSearchResult, qdrant_store
from src.schemas.search import SearchResultItem


class HybridSearchEngine:
    """Hybrid Retrieval Engine combining BM25 keyword search & Qdrant dense vector search via Reciprocal Rank Fusion (RRF)."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return [w for w in cleaned.split() if len(w) > 1]

    def bm25_search(
        self,
        query: str,
        corpus_chunks: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not corpus_chunks:
            return []

        tokenized_corpus = [self._tokenize(c["content"]) for c in corpus_chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = self._tokenize(query)

        if not tokenized_query:
            return []

        scores = bm25.get_scores(tokenized_query)
        scored_chunks = []
        for idx, score in enumerate(scores):
            if score > 0:
                chunk = corpus_chunks[idx]
                scored_chunks.append({
                    "chunk": chunk,
                    "score": float(score)
                })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def combine_rrf(
        self,
        vector_results: List[VectorSearchResult],
        bm25_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[SearchResultItem]:
        """Reciprocal Rank Fusion (RRF) score calculation."""
        rrf_map: Dict[str, Dict[str, Any]] = {}

        # Process Vector Ranks
        for rank, res in enumerate(vector_results):
            cid = res.chunk_id
            rrf_score = 1.0 / (self.rrf_k + rank + 1)
            rrf_map[cid] = {
                "chunk_id": cid,
                "document_id": res.payload.get("document_id", ""),
                "document_title": res.payload.get("doc_title", res.payload.get("filename", "Document")),
                "filename": res.payload.get("filename", ""),
                "page_number": res.payload.get("page_number", 1),
                "content": res.payload.get("content", ""),
                "score": rrf_score,
                "search_mode": "semantic",
                "metadata": res.payload
            }

        # Process BM25 Ranks
        for rank, item in enumerate(bm25_results):
            chunk = item["chunk"]
            cid = chunk["chunk_id"]
            rrf_score = 1.0 / (self.rrf_k + rank + 1)

            if cid in rrf_map:
                rrf_map[cid]["score"] += rrf_score
                rrf_map[cid]["search_mode"] = "hybrid"
            else:
                rrf_map[cid] = {
                    "chunk_id": cid,
                    "document_id": chunk.get("document_id", ""),
                    "document_title": chunk.get("doc_title", chunk.get("filename", "Document")),
                    "filename": chunk.get("filename", ""),
                    "page_number": chunk.get("page_number", 1),
                    "content": chunk.get("content", ""),
                    "score": rrf_score,
                    "search_mode": "keyword",
                    "metadata": chunk.get("metadata", {})
                }

        combined = list(rrf_map.values())
        combined.sort(key=lambda x: x["score"], reverse=True)
        top_results = combined[:top_k]

        return [
            SearchResultItem(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                document_title=r["document_title"],
                filename=r["filename"],
                page_number=r["page_number"],
                content=r["content"],
                score=round(r["score"], 4),
                search_mode=r["search_mode"],
                metadata=r["metadata"]
            )
            for r in top_results
        ]


hybrid_search_engine = HybridSearchEngine()
