import os
import time
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import settings
from config.logger import logger
from src.classification.inference import classifier_inference
from src.core.exceptions import BadRequestException, EntityNotFoundException
from src.document_processing.chunker import default_chunker
from src.document_processing.pdf_extractor import pdf_extractor
from src.models.document import Document, DocumentChunk
from src.rag.embeddings import embedding_service
from src.repositories.analytics_repository import ProcessingLogRepository
from src.repositories.document_repository import DocumentChunkRepository, DocumentRepository
from src.vector_store.qdrant_client import qdrant_store


class DocumentService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.doc_repo = DocumentRepository(db_session)
        self.chunk_repo = DocumentChunkRepository(db_session)
        self.log_repo = ProcessingLogRepository(db_session)

    async def save_uploaded_file(self, file: UploadFile, user_id: str) -> Document:

        file_id = f"doc_{int(time.time())}_{file.filename}"
        upload_dir = settings.UPLOAD_PATH
        file_path = os.path.join(upload_dir, file_id)

        contents = await file.read()
        file_size = len(contents)

        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise BadRequestException(f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB} MB.")

        with open(file_path, "wb") as f:
            f.write(contents)

        doc = Document(
            title=os.path.splitext(file.filename)[0].replace("_", " ").title(),
            filename=file.filename,
            file_path=file_path,
            file_size_bytes=file_size,
            mime_type=file.content_type or "application/pdf",
            processing_status="pending",
            user_id=user_id
        )
        return await self.doc_repo.create(doc)

    async def process_document_pipeline(self, document_id: str) -> Document:
        """Complete Background Processing Pipeline for PDF Document."""
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)

        try:
            await self.doc_repo.update(document_id, {"processing_status": "processing"})
            t0 = time.time()

            # 1. Text & Metadata Extraction
            t_extract = time.time()
            extracted_doc = pdf_extractor.extract(doc.file_path, doc.filename)
            dur_extract = round((time.time() - t_extract) * 1000, 2)
            await self.log_repo.log_step(document_id, "extract", "success", dur_extract, f"Extracted {extracted_doc.total_pages} pages.")

            # 2. Intelligent Text Chunking
            t_chunk = time.time()
            chunk_items = default_chunker.chunk_document(extracted_doc, document_id, doc.filename)
            dur_chunk = round((time.time() - t_chunk) * 1000, 2)
            await self.log_repo.log_step(document_id, "chunk", "success", dur_chunk, f"Created {len(chunk_items)} text chunks.")

            # 3. Embedding Generation
            t_embed = time.time()
            chunk_texts = [c.content for c in chunk_items]
            embeddings = embedding_service.embed_batch(chunk_texts)
            dur_embed = round((time.time() - t_embed) * 1000, 2)
            await self.log_repo.log_step(document_id, "embed", "success", dur_embed, f"Generated {len(embeddings)} vectors.")

            # 4. Save DB Chunks & Index Qdrant Vectors
            t_vec = time.time()
            qdrant_points = []
            for idx, item in enumerate(chunk_items):
                vec = embeddings[idx]
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=item.chunk_index,
                    page_number=item.page_number,
                    content=item.content,
                    token_count=item.token_count,
                    vector_id=item.chunk_id,
                    chunk_metadata=item.metadata
                )
                await self.chunk_repo.create(db_chunk)

                qdrant_points.append({
                    "id": item.chunk_id,
                    "vector": vec,
                    "payload": {
                        "document_id": document_id,
                        "filename": doc.filename,
                        "doc_title": doc.title,
                        "page_number": item.page_number,
                        "chunk_index": item.chunk_index,
                        "content": item.content,
                        "category": doc.predicted_category or "Unclassified"
                    }
                })

            qdrant_store.upsert_vectors(qdrant_points)
            dur_vec = round((time.time() - t_vec) * 1000, 2)
            await self.log_repo.log_step(document_id, "vector_index", "success", dur_vec, f"Indexed {len(qdrant_points)} vectors in Qdrant.")

            # 5. TensorFlow Category Classification
            t_class = time.time()
            sample_text = " ".join(chunk_texts[:5]) if chunk_texts else doc.title
            class_res = classifier_inference.classify_text(sample_text)
            dur_class = round((time.time() - t_class) * 1000, 2)
            await self.log_repo.log_step(document_id, "classify", "success", dur_class, f"Classified as '{class_res.predicted_category}' ({class_res.confidence}).")

            # Finalize Document Update
            updated_doc = await self.doc_repo.update(document_id, {
                "page_count": extracted_doc.total_pages,
                "chunk_count": len(chunk_items),
                "processing_status": "completed",
                "predicted_category": class_res.predicted_category,
                "category_confidence": class_res.confidence,
                "doc_metadata": extracted_doc.metadata
            })

            logger.info(f"Successfully processed document '{doc.filename}' (ID: {document_id}) in {round(time.time() - t0, 2)}s.")
            return updated_doc

        except Exception as e:
            logger.error(f"Error processing document pipeline for {document_id}: {e}")
            await self.doc_repo.update(document_id, {
                "processing_status": "failed",
                "error_message": str(e)
            })
            await self.log_repo.log_step(document_id, "pipeline", "failed", 0.0, str(e))
            raise e

    async def delete_document(self, document_id: str) -> bool:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise EntityNotFoundException("Document", document_id)

        # Delete file
        if os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass

        # Delete vectors
        qdrant_store.delete_document_vectors(document_id)

        # Delete DB record
        return await self.doc_repo.delete(document_id)
