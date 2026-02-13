from datetime import datetime
from pathlib import Path
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from databases import Database
from .config import get_settings


settings = get_settings()
db_path = Path(settings.sqlite_path)
db_path.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{db_path}"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

documents = Table(
    "documents",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String, nullable=False),
    Column("file_hash", String, unique=True, nullable=False),
    Column("type", String, nullable=False),
    Column("uploaded_at", DateTime, default=datetime.utcnow),
    Column("source_unit", String),
    Column("year", Integer),
    Column("tags", JSON),
)

chunks = Table(
    "chunks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id"), nullable=False),
    Column("chunk_index", Integer, nullable=False),
    Column("text", Text, nullable=False),
    Column("page_start", Integer),
    Column("page_end", Integer),
    Column("token_count", Integer),
)

embeddings_index_map = Table(
    "embeddings_index_map",
    metadata,
    Column("chunk_id", Integer, ForeignKey("chunks.id"), primary_key=True),
    Column("faiss_vector_id", Integer, nullable=False, unique=True),
)

chat_sessions = Table(
    "chat_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user", String, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

chat_messages = Table(
    "chat_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", Integer, ForeignKey("chat_sessions.id"), nullable=False),
    Column("role", String, nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

audit_logs = Table(
    "audit_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("action", String, nullable=False),
    Column("payload_json", JSON),
    Column("created_at", DateTime, server_default=func.now()),
)


def get_engine():
    return sqlalchemy.create_engine(DATABASE_URL)


def init_db():
    engine = get_engine()
    metadata.create_all(engine)

