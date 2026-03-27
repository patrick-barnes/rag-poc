from typing import Any, List
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import json


class VectorStore:
    def __init__(self, database_url: str | None):
        if not database_url:
            self._engine = None
        else:
            self._engine = create_async_engine(database_url, future=True)

    async def upsert(self, doc_id: str, text_content: str, embedding: List[float], metadata: dict | None = None):
        if not self._engine:
            return
        # pgvector expects a vector literal (text) like "[0.1, 0.2, ...]" cast to vector
        emb_text = '[' + ','.join(map(str, embedding)) + ']'
        async with self._engine.begin() as conn:
            await conn.execute(text(
                "INSERT INTO documents (id, content, embedding, metadata) VALUES (:id, :content, :embedding::vector, :metadata) "
                "ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata"
            ), {"id": doc_id, "content": text_content, "embedding": emb_text, "metadata": json.dumps(metadata or {})})

    async def query(self, embedding: List[float], top_k: int = 4) -> List[dict[str, Any]]:
        if not self._engine:
            return []
        # convert embedding to pgvector literal string and cast in SQL
        emb_text = '[' + ','.join(map(str, embedding)) + ']'
        async with self._engine.connect() as conn:
            result = await conn.execute(text(
                f"SELECT id, content, metadata FROM documents ORDER BY embedding <=> '{emb_text}'::vector LIMIT :k"
            ), {"k": top_k})
            rows = result.fetchall()
            out = []
            for r in rows:
                meta = r['metadata']
                try:
                    meta = json.loads(meta) if isinstance(meta, str) else meta
                except Exception:
                    meta = {}
                out.append({"id": r['id'], "content": r['content'], "metadata": meta})
            return out
