from sqlalchemy import select
from fastapi import APIRouter

from ..db import database, documents
from ..schemas import DocumentOut

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents():
    rows = await database.fetch_all(select(documents))
    return [DocumentOut(**row) for row in rows]
