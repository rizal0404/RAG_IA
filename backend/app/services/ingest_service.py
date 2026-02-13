import hashlib
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF
import docx
from sqlalchemy import select, insert

from ..config import get_settings
from ..db import database, documents, chunks, embeddings_index_map
from ..vector_store.faiss_store import FaissStore
from .embedding_client import EmbeddingClient
from .chunking import chunk_text, count_tokens


settings = get_settings()
embedding_client = EmbeddingClient()


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()


def _extract_pdf(path: Path) -> List[tuple[int, str]]:
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append((page.number + 1, page.get_text("text")))
    return pages


def _extract_docx(path: Path) -> List[tuple[Optional[int], str]]:
    d = docx.Document(path)
    paragraphs = [p.text for p in d.paragraphs if p.text.strip()]
    return [(None, "\n".join(paragraphs))]


async def ingest_file(
    file_path: Path,
    filename: str,
    source_unit: Optional[str],
    year: Optional[int],
    tags: Optional[dict],
    faiss_index_path: str,
) -> int:
    file_hash = _hash_file(file_path)
    # Duplicate check
    existing = await database.fetch_one(select(documents.c.id).where(documents.c.file_hash == file_hash))
    if existing:
        return existing[0]

    suffix = file_path.suffix.lower()
    doc_type = "pdf" if suffix == ".pdf" else "docx"

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / filename
    stored_path.write_bytes(file_path.read_bytes())

    # Insert document
    doc_id = await database.execute(
        documents.insert().values(
            filename=filename,
            file_hash=file_hash,
            type=doc_type,
            source_unit=source_unit,
            year=year,
            tags=tags,
        )
    )

    # Extract pages
    if doc_type == "pdf":
        page_texts = _extract_pdf(stored_path)
    else:
        page_texts = _extract_docx(stored_path)

    all_chunks = []
    global_idx = 0
    for page_num, text in page_texts:
        for _, (chunk, token_count) in enumerate(chunk_text(text, settings.chunk_size, settings.chunk_overlap)):
            chunk_id = await database.execute(
                insert(chunks).values(
                    document_id=doc_id,
                    chunk_index=global_idx,
                    text=chunk,
                    page_start=page_num,
                    page_end=page_num,
                    token_count=token_count,
                )
            )
            all_chunks.append((chunk_id, chunk))
            global_idx += 1

    if all_chunks:
        embeddings = embedding_client.embed([c[1] for c in all_chunks])
        dim = len(embeddings[0])
        faiss_store = FaissStore(faiss_index_path, dim=dim)
        faiss_ids = faiss_store.add(embeddings)
        await database.execute_many(
            query=embeddings_index_map.insert(),
            values=[{"chunk_id": cid, "faiss_vector_id": vid} for (cid, _), vid in zip(all_chunks, faiss_ids)],
        )

    return doc_id
