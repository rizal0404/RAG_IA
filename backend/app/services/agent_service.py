from typing import List
from ..schemas import AgentRequest, AgentResponse, AgentMode, Citation
from .retrieval_service import retrieve
from .llm_client import LLMClient

llm_client = LLMClient()


TEMPLATES = {
    AgentMode.DRAFT_PLAN: (
        "Buat draft Program Audit Internal. Sertakan: Objective, Risiko & Kontrol, Prosedur audit "
        "(langkah berurutan), Pendekatan sampling, Evidence yang dibutuhkan, Output/deliverables. "
        "Gunakan bahasa Indonesia ringkas dan bullet. Sertakan citation untuk tiap poin jika ada."
    ),
    AgentMode.FOLLOW_UP: (
        "Buat rekomendasi tindak lanjut atas temuan audit. Sertakan: tindakan korektif, PIC, due date (perkiraan), "
        "indikator keberhasilan. Jawab ringkas."
    ),
    AgentMode.SUMMARIZE: "Ringkas laporan audit menjadi poin utama: scope, temuan, rekomendasi, status tindak lanjut.",
}


async def run_agent(req: AgentRequest) -> AgentResponse:
    mode = req.mode
    instruction = TEMPLATES.get(mode, "Buat ringkasan berdasarkan konteks.")
    base_prompt = (
        "Peran: Internal Audit Assistant. Hasil harus siap edit, beri bullet yang rapi. "
        "Sertakan citation (doc, page) di setiap sub-poin yang berasal dari dokumen."
    )
    # Optional retrieval when payload carries 'query' or 'scope'
    query = req.payload.get("query") or req.payload.get("scope") or ""
    retrieved = await retrieve(query, 5) if query else []
    context = "\n\n".join([f"(doc:{c.filename}, page:{c.page}) {c.snippet}" for c in retrieved])
    messages = [
        {
            "role": "user",
            "content": f"{instruction}\n\nInput pengguna: {req.payload}\n\nKonteks dokumen:\n{context}",
        }
    ]
    answer = llm_client.chat(base_prompt, messages)
    citations = [
        Citation(
            document_id=c.document_id, filename=c.filename, page=c.page, chunk_id=c.chunk_id, snippet=c.snippet[:200]
        )
        for c in retrieved
    ]
    return AgentResponse(content=answer, citations=citations)
