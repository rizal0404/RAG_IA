from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DocumentIn(BaseModel):
    source_unit: Optional[str] = None
    year: Optional[int] = None
    tags: Optional[dict] = None


class DocumentOut(BaseModel):
    id: int
    filename: str
    type: str
    uploaded_at: datetime
    source_unit: Optional[str]
    year: Optional[int]
    tags: Optional[dict]

    class Config:
        orm_mode = True


class ChunkMetadata(BaseModel):
    document_id: int
    filename: str
    page: Optional[int]
    chunk_id: int
    snippet: str


class RetrievalResponse(BaseModel):
    query: str
    results: List[ChunkMetadata]


class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    user: str
    query: str
    max_retrieve: int = 5


class Citation(BaseModel):
    document_id: int
    filename: str
    page: Optional[int]
    chunk_id: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    session_id: int


class AgentMode(str):
    DRAFT_PLAN = "draft_audit_plan"
    FOLLOW_UP = "draft_followup_actions"
    SUMMARIZE = "summarize_audit_report"


class AgentRequest(BaseModel):
    mode: str
    payload: dict
    user: str


class AgentResponse(BaseModel):
    content: str
    citations: List[Citation]

