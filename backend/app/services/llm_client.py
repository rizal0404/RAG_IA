import logging
from typing import List, Dict
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self.api_key = settings.llm_api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    def chat(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        if self.provider in {"gemini", "google"} and self.api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                full_prompt = [{"role": "system", "content": system_prompt}] + messages
                resp = model.generate_content(full_prompt, request_options={"timeout": 60})
                return resp.text
            except Exception as exc:  # pragma: no cover
                logger.warning("Gemini failed, falling back. %s", exc)

        if self.provider == "openai" and self.api_key:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.api_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": system_prompt}, *messages],
                )
                return resp.choices[0].message.content
            except Exception as exc:  # pragma: no cover
                logger.warning("OpenAI failed, falling back. %s", exc)

        if self.provider == "groq" and self.api_key:
            try:
                import groq

                client = groq.Groq(api_key=self.api_key)
                resp = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}, *messages],
                )
                return resp.choices[0].message.content
            except Exception as exc:  # pragma: no cover
                logger.warning("Groq failed, falling back. %s", exc)

        if self.provider == "openrouter" and self.api_key:
            headers = {"Authorization": f"Bearer {self.api_key}", "HTTP-Referer": "local-prototype"}
            payload = {
                "model": "openrouter/auto",
                "messages": [{"role": "system", "content": system_prompt}, *messages],
            }
            try:
                r = httpx.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=60)
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"]
            except Exception as exc:  # pragma: no cover
                logger.warning("OpenRouter failed, falling back. %s", exc)

        # Fallback: simple heuristic
        joined = "\n\n".join([f"- {m['content']}" for m in messages if m["role"] == "user"])
        return f"(Fallback) Berdasarkan konteks tersedia, berikut ringkasan:\n{joined}"

