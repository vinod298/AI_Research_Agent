from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.repositories.document_repository import DocumentRepository
from src.schemas.document import DocumentDetailResponse, DocumentResponse, ReprocessRequest
from src.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a PDF document.
    Triggers background ingestion pipeline: Text Extraction -> Chunking -> Embedding -> Qdrant Vector Indexing -> TF Classification.
    """
    service = DocumentService(db)
    doc = await service.save_uploaded_file(file, current_user.id)
    background_tasks.add_task(service.process_document_pipeline, doc.id)
    return doc


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents owned by the current user."""
    repo = DocumentRepository(db)
    return await repo.get_by_user(current_user.id, skip=skip, limit=limit)


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document details with extracted chunks."""
    repo = DocumentRepository(db)
    doc = await repo.get_with_chunks(document_id)
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document, its database chunks, and vector embeddings."""
    service = DocumentService(db)
    await service.delete_document(document_id)
    return None


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    document_id: str,
    request: ReprocessRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Re-run ingestion pipeline for a document with custom parameters."""
    service = DocumentService(db)
    doc = await service.process_document_pipeline(document_id)
    return doc
