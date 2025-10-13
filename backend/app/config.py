from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Pydantic will automatically read from .env file and environment variables
    
    # Database settings
    DATABASE_URL: str = "sqlite:///kaas.db"
    
    # Vector store settings
    CHROMA_DB_DIR: str = "./chroma_db"
    
    # Generation settings
    GROQ_API_KEY: str = ""
    HF_FALLBACK: bool = True
    
    # Embedding model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Chunking settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        # --- THIS IS THE FIX ---
        # It tells Pydantic to ignore any extra environment variables (like PORT)
        # that are not defined in this class.
        extra='ignore' 
    )

settings = Settings()