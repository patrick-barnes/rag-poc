from fastapi import FastAPI
from .api.routes import router as api_router

def create_app() -> FastAPI:
    app = FastAPI(title="rag-poc backend")
    app.include_router(api_router, prefix="")
    return app

app = create_app()
