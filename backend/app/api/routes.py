from fastapi import APIRouter, Depends, HTTPException
from ..models import QueryRequest, QueryResponse
from ..deps import get_openai_client, get_vector_store

router = APIRouter()


@router.get('/health')
async def health():
    return {"status": "ok"}


@router.post('/ingest')
async def ingest(items: list[dict], vector_store = Depends(get_vector_store), openai = Depends(get_openai_client)):
    inserted = 0
    for it in items:
        doc_id = it.get('id')
        text = it.get('text')
        metadata = it.get('metadata', {})
        if not doc_id or not text:
            continue
        emb = await openai.embed_texts([text])
        await vector_store.upsert(doc_id, text, emb[0], metadata)
        inserted += 1
    return {"inserted": inserted}


@router.post('/query', response_model=QueryResponse)
async def query(req: QueryRequest, vector_store = Depends(get_vector_store), openai = Depends(get_openai_client)):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query is required")

    q_emb = await openai.embed_texts([req.query])
    rows = await vector_store.query(q_emb[0], top_k=req.top_k)

    context = "\n\n".join([r['content'] for r in rows])
    prompt = f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {req.query}\n\nAnswer:" 
    answer = await openai.generate_answer(prompt)
    sources = [r.get('metadata', {}) for r in rows]
    return {"answer": answer, "sources": sources}
