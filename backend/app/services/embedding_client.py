from typing import List
import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingClient:
    """Simple embedding client with cloud-first, local fallback."""

    def __init__(self):
        self.provider = settings.embed_provider.lower()
        self.api_key = settings.embed_api_key
        self._local_model = None

    def _ensure_local(self):
        if self._local_model:
            return
        from sentence_transformers import SentenceTransformer

        self._local_model = SentenceTransformer("all-MiniLM-L6-v2")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.provider in {"gemini", "google"} and self.api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                model = "models/text-embedding-004"
                res = genai.embed_content(model=model, content=texts)
                # API returns {"embedding": [...]} for single; list for batch
                if "embeddings" in res:
                    return [item["embedding"] for item in res["embeddings"]]
                if "embedding" in res:
                    return [res["embedding"]]
            except Exception as exc:  # pragma: no cover - safeguard
                logger.warning("Gemini embedding failed, falling back to local. %s", exc)

        if self.provider == "openai" and self.api_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key)
                response = client.embeddings.create(model="text-embedding-3-small", input=texts)
                return [d.embedding for d in response.data]
            except Exception as exc:  # pragma: no cover
                logger.warning("OpenAI embedding failed, falling back to local. %s", exc)

        if self.provider == "openrouter" and self.api_key:
            import httpx

            headers = {"Authorization": f"Bearer {self.api_key}"}
            body = {"model": "openrouter/clip-vit-base-patch16", "input": texts}
            try:
                r = httpx.post("https://openrouter.ai/api/v1/embeddings", json=body, headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
                return [item["embedding"] for item in data.get("data", [])]
            except Exception as exc:  # pragma: no cover
                logger.warning("OpenRouter embedding failed, falling back to local. %s", exc)

        # Local fallback
        self._ensure_local()
        return [self._local_model.encode(text).tolist() for text in texts]

