import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    embed_provider: str = os.getenv("EMBED_PROVIDER", "gemini")
    embed_api_key: str = os.getenv("EMBED_API_KEY", "")
    sqlite_path: str = os.getenv("SQLITE_PATH", "../data/sqlite/app.db")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "../data/faiss/index.bin")
    upload_dir: str = os.getenv("UPLOAD_DIR", "../data/uploads")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 900))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 120))
    max_retrieve: int = int(os.getenv("MAX_RETRIEVE", 5))

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
