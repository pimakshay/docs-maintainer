from typing import Set

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # GEMINI Model parameters
    GOOGLE_API_KEY: str
    GEMINI_MODEL_NAME: str
    GEMINI_EMBEDDING_MODEL_NAME: str

    # Load documentation folder
    DOC_DIR_PATH: str

    # Retrieval config
    TOP_K_DOCS: int
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    CHROMA_DB_NAME: str
    SCORE_THRESHOLD: float


    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = "/home/akshay/Documents/projects/pluno_tasks/docs-maintainer/fastapi_backend/.env"
        env_file_encoding = "utf-8"

settings = Settings()