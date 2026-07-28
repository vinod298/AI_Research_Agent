from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient as QClient
from qdrant_client.http import models as qmodels
from config.settings import settings
from config.logger import logger


class VectorSearchResult:
    def __init__(self, chunk_id: str, score: float, payload: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.score = score
        self.payload = payload


class QdrantVectorStore:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.EMBEDDING_DIMENSION
        self.client: Optional[QClient] = None
        self.in_memory_store: Dict[str, Dict[str, Any]] = {} # Fallback in-memory vector dictionary

    def initialize(self) -> None:
        """Initialize Qdrant client connection and collection."""
        try:
            if settings.QDRANT_IN_MEMORY:
                self.client = QClient(":memory:")
                logger.info("Initialized Qdrant in in-memory mode.")
            else:
                self.client = QClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=5.0
                )
                logger.info(f"Connected to Qdrant server at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

            self._ensure_collection()
        except Exception as e:
            logger.warning(f"Failed to connect to Qdrant server ({e}). Operating in memory fallback mode.")
            self.client = None

    def _ensure_collection(self) -> None:
        if not self.client:
            return

        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=self.vector_size,
                    distance=qmodels.Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {self.collection_name} (Dim: {self.vector_size})")

    def upsert_vectors(self, points: List[Dict[str, Any]]) -> bool:
        """
        Upsert a list of point dictionaries:
        [{ "id": str, "vector": List[float], "payload": dict }]
        """
        if not points:
            return True

        # Always update in-memory store for fallback parity
        for p in points:
            self.in_memory_store[p["id"]] = {
                "vector": p["vector"],
                "payload": p["payload"]
            }

        if self.client:
            try:
                qpoints = [
                    qmodels.PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p["payload"]
                    )
                    for p in points
                ]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=qpoints
                )
                return True
            except Exception as e:
                logger.error(f"Qdrant upsert failed: {e}. Storing in memory fallback.")

        return True

    def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        category_filter: Optional[str] = None
    ) -> List[VectorSearchResult]:
        if self.client:
            try:
                must_filters = []
                if document_ids:
                    must_filters.append(
                        qmodels.FieldCondition(
                            key="document_id",
                            match=qmodels.MatchAny(any=document_ids)
                        )
                    )
                if category_filter:
                    must_filters.append(
                        qmodels.FieldCondition(
                            key="category",
                            match=qmodels.MatchValue(value=category_filter)
                        )
                    )

                query_filter = qmodels.Filter(must=must_filters) if must_filters else None

                if hasattr(self.client, "query_points"):
                    res_obj = self.client.query_points(
                        collection_name=self.collection_name,
                        query=query_vector,
                        query_filter=query_filter,
                        limit=top_k
                    )
                    results = res_obj.points
                elif hasattr(self.client, "search"):
                    results = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        query_filter=query_filter,
                        limit=top_k
                    )
                else:
                    results = []

                if results:
                    return [
                        VectorSearchResult(
                            chunk_id=str(r.id),
                            score=float(r.score),
                            payload=dict(r.payload)
                        )
                        for r in results
                    ]
            except Exception as e:
                logger.error(f"Qdrant search error: {e}. Executing memory fallback search.")

        # In-memory cosine similarity search fallback
        import numpy as np
        if not self.in_memory_store:
            return []

        q_vec = np.array(query_vector)
        q_norm = np.linalg.norm(q_vec) + 1e-9

        scores = []
        for cid, item in self.in_memory_store.items():
            payload = item["payload"]
            if document_ids and payload.get("document_id") not in document_ids:
                continue
            if category_filter and payload.get("category") != category_filter:
                continue

            v = np.array(item["vector"])
            v_norm = np.linalg.norm(v) + 1e-9
            cos_sim = float(np.dot(q_vec, v) / (q_norm * v_norm))
            scores.append((cid, cos_sim, payload))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_scores = scores[:top_k]

        return [
            VectorSearchResult(chunk_id=cid, score=score, payload=payload)
            for cid, score, payload in top_scores
        ]

    def delete_document_vectors(self, document_id: str) -> bool:
        if self.client:
            try:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qmodels.FilterSelector(
                        filter=qmodels.Filter(
                            must=[
                                qmodels.FieldCondition(
                                    key="document_id",
                                    match=qmodels.MatchValue(value=document_id)
                                )
                            ]
                        )
                    )
                )
            except Exception as e:
                logger.error(f"Failed to delete Qdrant vectors for doc {document_id}: {e}")

        # Remove from memory store
        keys_to_del = [k for k, v in self.in_memory_store.items() if v["payload"].get("document_id") == document_id]
        for k in keys_to_del:
            del self.in_memory_store[k]
        return True


qdrant_store = QdrantVectorStore()
