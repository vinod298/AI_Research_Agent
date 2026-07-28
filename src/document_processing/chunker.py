import uuid
from typing import Any, Dict, List
from src.document_processing.pdf_extractor import ExtractedDocument, ExtractedPage


class ChunkItem:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        filename: str,
        page_number: int,
        chunk_index: int,
        content: str,
        token_count: int,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.filename = filename
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.content = content
        self.token_count = token_count
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "filename": self.filename,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "content": self.content,
            "token_count": self.token_count,
            "metadata": self.metadata
        }


class IntelligentTextChunker:
    """Recursive Character Text Splitter with semantic paragraph preservation."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "; ", ", ", " "]

    def chunk_document(
        self,
        extracted_doc: ExtractedDocument,
        document_id: str,
        filename: str
    ) -> List[ChunkItem]:
        all_chunks: List[ChunkItem] = []
        global_chunk_idx = 0

        for page in extracted_doc.pages:
            if not page.text or not page.text.strip():
                continue

            page_chunks = self._split_text(page.text)
            for text_chunk in page_chunks:
                text_chunk = text_chunk.strip()
                if not text_chunk:
                    continue

                chunk_id = str(uuid.uuid4())
                word_tokens = len(text_chunk.split())

                chunk_obj = ChunkItem(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    filename=filename,
                    page_number=page.page_number,
                    chunk_index=global_chunk_idx,
                    content=text_chunk,
                    token_count=word_tokens,
                    metadata={
                        "document_id": document_id,
                        "filename": filename,
                        "page_number": page.page_number,
                        "chunk_id": chunk_id,
                        "chunk_index": global_chunk_idx,
                        "doc_title": extracted_doc.title
                    }
                )
                all_chunks.append(chunk_obj)
                global_chunk_idx += 1

        return all_chunks

    def _split_text(self, text: str) -> List[str]:
        """Recursive splitting based on hierarchical separators."""
        if len(text) <= self.chunk_size:
            return [text]

        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        final_chunks = []
        if not separators:
            # Hard character split fallback
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                final_chunks.append(text[i:i + self.chunk_size])
            return final_chunks

        separator = separators[0]
        splits = text.split(separator)
        current_chunk = ""

        for split in splits:
            item = split + (separator if separator != " " else "")
            if len(current_chunk) + len(item) <= self.chunk_size:
                current_chunk += item
            else:
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
                if len(item) > self.chunk_size:
                    # Recursively split large segment with finer separator
                    sub_splits = self._recursive_split(item, separators[1:])
                    final_chunks.extend(sub_splits)
                    current_chunk = ""
                else:
                    current_chunk = item

        if current_chunk:
            final_chunks.append(current_chunk.strip())

        # Apply overlap where needed
        overlapped_chunks = []
        for i, chk in enumerate(final_chunks):
            if i > 0 and self.chunk_overlap > 0:
                prev_text = final_chunks[i - 1][-self.chunk_overlap:]
                combined = f"... {prev_text} {chk}"
                overlapped_chunks.append(combined)
            else:
                overlapped_chunks.append(chk)

        return overlapped_chunks


default_chunker = IntelligentTextChunker()
