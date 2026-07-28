from typing import Any, Dict, List
from src.schemas.search import SearchResultItem


SYSTEM_RAG_PROMPT = """You are an Enterprise AI Research Assistant.
Your directive is to answer user questions with extreme precision based ONLY on the provided document excerpts.

STRICT ANTI-HALLUCINATION RULES:
1. Use ONLY facts directly mentioned in the RETRIEVED CONTEXT below.
2. NEVER invent, extrapolate, or introduce external unverified knowledge.
3. If the retrieved context does not contain enough information to answer the question, you MUST respond EXACTLY:
   "I cannot determine the answer from the uploaded documents."
4. ALWAYS provide inline citations for statements in the exact format: [Document Name, Page X].
5. Maintain a professional, objective, academic, and analytical tone.
"""


def build_rag_prompt(
    question: str,
    retrieved_chunks: List[SearchResultItem],
    conversation_history: List[Dict[str, str]] = None
) -> str:
    """Build formatted prompt string with strict citations context."""
    if not retrieved_chunks:
        return f"USER QUESTION: {question}\n\nRELEVANT RETRIEVED CONTEXT:\nUNAVAILABLE_FALLBACK"

    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        filename = chunk.filename or "Document"
        page_num = chunk.page_number
        context_str += f"\n--- Source [{idx}]: {filename} | Page: {page_num} | Chunk ID: {chunk.chunk_id} ---\n"
        context_str += f"{chunk.content.strip()}\n"

    history_str = ""
    if conversation_history:
        history_str = "\nRECENT CONVERSATION HISTORY:\n"
        for msg in conversation_history[-4:]: # Last 2 turns
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            history_str += f"{role}: {content}\n"

    prompt = f"""
{history_str}
RELEVANT RETRIEVED CONTEXT EXCERPTS:
{context_str}

USER QUESTION: {question}

INSTRUCTIONS FOR ANSWER:
1. Synthesize a comprehensive answer to the user question using ONLY facts from the retrieved excerpts above.
2. Include inline page citations in format: [{retrieved_chunks[0].filename}, Page {retrieved_chunks[0].page_number}].
3. Do not include information outside of these excerpts.
"""
    return prompt
