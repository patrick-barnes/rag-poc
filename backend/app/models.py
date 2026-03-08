from pydantic import BaseModel
from typing import Any


class QueryRequest(BaseModel):
    query: str
    top_k: int = 4


class QueryResponse(BaseModel):
    answer: str
    sources: list[Any]
