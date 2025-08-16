import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # GEMINI Model parameters
    PROVIDER: str

    API_KEY: str
    LLM_MODEL_NAME: str
    EMBEDDING_MODEL_NAME: str

    # GOOGLE_API_KEY: str
    # GEMINI_MODEL_NAME: str
    # GEMINI_EMBEDDING_MODEL_NAME: str

    # Load documentation folder
    DOC_DIR_PATH: str

    # Retrieval config
    TOP_K_DOCS: int
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    CHROMA_DB_NAME: str
    SCORE_THRESHOLD: float

    # Retrieval method
    RETRIEVAL_METHOD: str = "hybrid"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        home_path = os.path.join(os.path.dirname(__file__), "..")
        env_file = os.path.join(home_path, "fastapi_backend/.env")
        env_file_encoding = "utf-8"

settings = Settings()