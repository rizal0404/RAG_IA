from fastapi import APIRouter
from ..schemas import AgentRequest, AgentResponse
from ..services.agent_service import run_agent

router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/agent/run", response_model=AgentResponse)
async def agent_endpoint(payload: AgentRequest):
    return await run_agent(payload)
