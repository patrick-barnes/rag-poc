import os
from typing import List
import httpx


class OpenAIClient:
    def __init__(self, api_key: str | None, embedding_model: str = "text-embedding-3-small", completion_model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.completion_model = completion_model
        self._client = httpx.AsyncClient(timeout=30.0)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            return [[0.0]] * len(texts)
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.embedding_model, "input": texts}
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        j = resp.json()
        return [d["embedding"] for d in j.get("data", [])]

    async def generate_answer(self, prompt: str) -> str:
        if not self.api_key:
            return ""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.completion_model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512}
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        j = resp.json()
        choices = j.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "")
