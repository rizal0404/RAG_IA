# Backend (FastAPI)

## Quick start
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # PowerShell
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints
- `POST /api/ingest` — upload PDF/DOCX; menyimpan metadata + chunk + embedding ke FAISS.
- `GET /api/documents` — daftar dokumen.
- `GET /api/retrieve?query=...` — top-k chunk + metadata kutipan.
- `POST /api/chat` — QA berbasis dokumen dengan citations.
- `POST /api/agent/run` — generate artefak (draft audit plan, follow-up, summary).
- `GET /health` — liveness.

## Konfigurasi
Lihat `.env.example`. Provider default: `gemini` untuk LLM & embedding; otomatis fallback ke `sentence-transformers` lokal bila API key kosong.

## Catatan Teknis
- Penyimpanan lokal: SQLite untuk metadata & audit trail, FAISS untuk index vektor, file asli di `../data/uploads`.
- Chunking: 900 token, overlap 120; per halaman (PDF) atau gabungan (DOCX).
- Dimensi FAISS mengikuti dimensi embedding pertama (mis. 384 untuk MiniLM).
