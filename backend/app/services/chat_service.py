from typing import List
from sqlalchemy import insert

from ..db import database, chat_sessions, chat_messages
from ..schemas import ChatRequest, ChatResponse, Citation
from .retrieval_service import retrieve
from .llm_client import LLMClient

SYSTEM_PROMPT = (
    "Peran: Internal Audit Assistant. Jawab ringkas, dalam bahasa Indonesia. "
    "Gunakan bukti dari dokumen. Sertakan citation dengan format (doc:filename, page:X). "
    "Jika tidak ada bukti, jawab 'Tidak ditemukan di knowledge base'."
)

llm_client = LLMClient()


async def _ensure_session(user: str, session_id: int | None) -> int:
    if session_id:
        return session_id
    return await database.execute(insert(chat_sessions).values(user=user))


def _build_context(chunks) -> str:
    lines = []
    for c in chunks:
        cite = f"(doc:{c.filename}, page:{c.page or '?'}, chunk:{c.chunk_id})"
        lines.append(f"{cite}\n{c.snippet}")
    return "\n\n".join(lines)


async def handle_chat(req: ChatRequest) -> ChatResponse:
    session_id = await _ensure_session(req.user, req.session_id)
    retrieved = await retrieve(req.query, req.max_retrieve)

    if not retrieved:
        answer = "Tidak ditemukan di knowledge base."
        citations: List[Citation] = []
    else:
        context = _build_context(retrieved)
        messages = [
            {"role": "user", "content": f"Pertanyaan: {req.query}\n\nKonteks:\n{context}\n\nJawab dengan citation."}
        ]
        answer = llm_client.chat(SYSTEM_PROMPT, messages)
        citations = [
            Citation(
                document_id=c.document_id,
                filename=c.filename,
                page=c.page,
                chunk_id=c.chunk_id,
                snippet=c.snippet[:200],
            )
            for c in retrieved
        ]

    await database.execute(
        insert(chat_messages).values(session_id=session_id, role="user", content=req.query)
    )
    await database.execute(
        insert(chat_messages).values(session_id=session_id, role="assistant", content=answer)
    )

    return ChatResponse(answer=answer, citations=citations, session_id=session_id)

