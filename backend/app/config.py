import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- NEW: Define a base directory for all app data ---
# This makes it easy to manage paths inside the container.
APP_DIR = "/app"

class Settings(BaseSettings):
    # Backend settings
    PORT: int = 8000
    
    # --- UPDATED: Use absolute paths derived from APP_DIR ---
    # The environment variable from Render will override this default.
    DATABASE_URL: str = f"sqlite:///{os.path.join(APP_DIR, 'kaas.db')}"

    # Vector store settings
    # The environment variable from Render will override this default.
    CHROMA_DB_DIR: str = os.path.join(APP_DIR, "chroma_db")

    # Generation settings
    GROQ_API_KEY: str = ""
    HF_FALLBACK: bool = True
    
    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Chunking settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# --- THE FIX: Create the vector store directory if it doesn't exist ---
# This code runs once when the application starts.
os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)