from fastapi import APIRouter, Query

from ..services.retrieval_service import retrieve
from ..schemas import RetrievalResponse, ChunkMetadata

router = APIRouter(prefix="/api", tags=["retrieve"])


@router.get("/retrieve", response_model=RetrievalResponse)
async def retrieve_endpoint(q: str = Query(..., alias="query"), k: int = Query(5)):
    results = await retrieve(q, k)
    return RetrievalResponse(query=q, results=results)
