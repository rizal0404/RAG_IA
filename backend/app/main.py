import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .config import get_settings
from .db import database, init_db
from .routers import ingest, documents, retrieval, chat, agent

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title="Internal Audit AI Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(ingest.router)
app.include_router(documents.router)
app.include_router(retrieval.router)
app.include_router(chat.router)
app.include_router(agent.router)


@app.exception_handler(Exception)
async def default_exception_handler(request, exc):
    logging.exception(exc)
    return JSONResponse(status_code=500, content={"detail": "Internal error", "error": str(exc)})
