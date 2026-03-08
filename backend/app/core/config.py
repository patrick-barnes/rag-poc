import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    COMPLETION_MODEL: str = os.getenv("COMPLETION_MODEL", "gpt-4o-mini")
    TOP_K: int = int(os.getenv("TOP_K", "4"))


settings = Settings()
