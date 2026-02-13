from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from starlette import status
import json

from ..config import get_settings
from ..services.ingest_service import ingest_file
from ..db import database

router = APIRouter(prefix="/api", tags=["ingest"])
settings = get_settings()


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_endpoint(
    file: UploadFile = File(...),
    source_unit: str | None = Form(None),
    year: int | None = Form(None),
    tags: str | None = Form(None),
):
    if file.content_type not in {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX are supported.")

    tmp_path = Path(settings.upload_dir) / f"tmp_{file.filename}"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path.write_bytes(await file.read())

    try:
        parsed_tags = json.loads(tags) if tags else None
        doc_id = await ingest_file(
            tmp_path,
            filename=file.filename,
            source_unit=source_unit,
            year=year,
            tags=parsed_tags,
            faiss_index_path=settings.faiss_index_path,
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return {"document_id": doc_id}
