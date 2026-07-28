import io
import pytest
from httpx import AsyncClient
import fitz


@pytest.mark.asyncio
async def test_upload_pdf_document(async_client: AsyncClient):
    # Minimal valid PDF byte stream
    pdf_bytes = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"

    files = {"file": ("test_doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    res = await async_client.post("/api/v1/documents/upload", files=files)
    assert res.status_code == 202
    data = res.json()
    assert data["filename"] == "test_doc.pdf"
    assert data["processing_status"] in ["pending", "processing", "completed"]
