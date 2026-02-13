from fastapi import APIRouter
from ..schemas import ChatRequest, ChatResponse
from ..services.chat_service import handle_chat

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    return await handle_chat(payload)
