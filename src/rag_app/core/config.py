from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RAG DB Model"
    app_env: str = Field(default="dev", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    raw_data_dir: Path = Field(default=Path("data/raw"), alias="RAW_DATA_DIR")
    vector_db_dir: Path = Field(default=Path("data/chroma"), alias="VECTOR_DB_DIR")

    collection_name: str = Field(default="rag_documents", alias="COLLECTION_NAME")
    embedding_provider: str = Field(default="huggingface", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    top_k: int = Field(default=4, alias="TOP_K")
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")

    # MMR (Maximal Marginal Relevance) settings
    use_mmr: bool = Field(default=True, alias="USE_MMR")
    mmr_fetch_k: int = Field(default=20, alias="MMR_FETCH_K")
    mmr_lambda_mult: float = Field(default=0.5, alias="MMR_LAMBDA_MULT")
    
    # Chat history settings
    use_history: bool = Field(default=True, alias="USE_HISTORY")

    llm_provider: str = Field(default="huggingface", alias="LLM_PROVIDER")
    use_llm: bool = Field(default=True, alias="USE_LLM")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")

    ollama_model: str = Field(default="llama3.2:3b", alias="OLLAMA_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    hf_model_id: str = Field(
        default="TinyLlama/TinyLlama-1.1B-Chat-v1.0", alias="HF_MODEL_ID"
    )
    hf_task: str = Field(default="text-generation", alias="HF_TASK")
    hf_temperature: float = Field(default=0.5, alias="HF_TEMPERATURE")
    hf_max_new_tokens: int = Field(default=512, alias="HF_MAX_NEW_TOKENS")
    hf_token: str = Field(default="", alias="HF_TOKEN")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_db_dir.mkdir(parents=True, exist_ok=True)
    return settings
