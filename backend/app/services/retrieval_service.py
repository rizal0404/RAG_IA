from typing import List
from sqlalchemy import select

from ..config import get_settings
from ..db import database, chunks, documents, embeddings_index_map
from ..vector_store.faiss_store import FaissStore
from .embedding_client import EmbeddingClient
from ..schemas import ChunkMetadata

settings = get_settings()
embedding_client = EmbeddingClient()


async def retrieve(query: str, k: int = None) -> List[ChunkMetadata]:
    k = k or settings.max_retrieve
    query_emb = embedding_client.embed([query])[0]
    store = FaissStore(settings.faiss_index_path, dim=384)
    faiss_ids, _ = store.search(query_emb, k)
    if not faiss_ids:
        return []

    rows = []
    for fid in faiss_ids:
        mapping = await database.fetch_one(
            select(embeddings_index_map.c.chunk_id).where(embeddings_index_map.c.faiss_vector_id == fid)
        )
        if not mapping:
            continue
        chunk_row = await database.fetch_one(select(chunks).where(chunks.c.id == mapping[0]))
        doc_row = await database.fetch_one(select(documents).where(documents.c.id == chunk_row["document_id"]))
        rows.append(
            ChunkMetadata(
                document_id=doc_row["id"],
                filename=doc_row["filename"],
                page=chunk_row["page_start"],
                chunk_id=chunk_row["id"],
                snippet=chunk_row["text"][:400],
            )
        )
    return rows
