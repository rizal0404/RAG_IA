from typing import List, Tuple
import tiktoken


def _encoder():
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:  # pragma: no cover - fallback
        return tiktoken.get_encoding("gpt2")


enc = _encoder()


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> List[Tuple[str, int]]:
    """Return list of (chunk_text, token_count)."""
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(len(tokens), start + chunk_size)
        window = tokens[start:end]
        chunk_str = enc.decode(window)
        chunks.append((chunk_str, len(window)))
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
