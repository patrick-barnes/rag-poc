from .core.config import settings
from .services.openai_client import OpenAIClient
from .services.vector_store import VectorStore


def get_openai_client():
    return OpenAIClient(api_key=settings.OPENAI_API_KEY, embedding_model=settings.EMBEDDING_MODEL, completion_model=settings.COMPLETION_MODEL)


def get_vector_store():
    return VectorStore(database_url=settings.DATABASE_URL)
